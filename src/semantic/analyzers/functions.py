from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import VoidType, ErrorType
from semantic.symbol_kinds import SymbolCategory
from semantic.registry.type_resolver import resolve_typectx, validate_known_types
from semantic.registry.closure_model import CaptureInfo
from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic, log_function


class FunctionsAnalyzer:
    
    @log_function
    def __init__(self, v):
        log_semantic("===== [Functions.py] Inicio =====")
        self.v = v

    @log_function
    def makeFuncLabel(self, name: str) -> str:
        """
        Convención de etiquetas:
          - Función libre: f_<name>
          - (Si alguna vez se declarara dentro de clase) f_<Class>_<name>
        """
        if getattr(self.v, "class_stack", None):
            owner = self.v.class_stack[-1] if self.v.class_stack else None
        else:
            owner = None

        label = f"f_{owner}_{name}" if owner else f"f_{name}"
        log_semantic(f"[makeFuncLabel] name='{name}', owner='{owner}' -> label='{label}'")
        return label

    @log_function
    def visitFunctionDeclaration(self, ctx: CompiscriptParser.FunctionDeclarationContext):
        name = ctx.Identifier().getText()
        log_semantic(f"[visitFunctionDeclaration] inicio: {name}")

        # ---- Parámetros: tipos y nombres ----
        param_types, param_names = [], []
        if ctx.parameters():
            for p in ctx.parameters().parameter():
                pname = p.Identifier().getText()
                tctx = p.type_()
                if tctx is None:
                    self.v.appendErr(SemanticError(
                        f"Parámetro '{pname}' debe declarar tipo.",
                        line=p.start.line, column=p.start.column))
                    ptype = ErrorType()
                else:
                    ptype = resolve_typectx(tctx)
                    if isinstance(ptype, VoidType):
                        self.v.appendErr(SemanticError(
                            f"Parámetro '{pname}' no puede ser de tipo void.",
                            line=p.start.line, column=p.start.column))
                        ptype = ErrorType()
                    elif not validate_known_types(
                        ptype, self.v.known_classes, p,
                        f"parámetro '{pname}'", self.v.errors
                    ):
                        ptype = ErrorType()
                param_names.append(pname)
                param_types.append(ptype)
                log_semantic(f"[param] {pname}: {ptype}")

        # ---- Tipo de retorno ----
        rtype = None
        if ctx.type_():
            rtype = resolve_typectx(ctx.type_())
            validate_known_types(rtype, self.v.known_classes, ctx,
                                 f"retorno de función '{name}'", self.v.errors)
        log_semantic(f"[return] tipo de retorno: {rtype if rtype else 'void'}")

        # ---- Declarar símbolo de función ----
        try:
            fsym = self.v.scopeManager.addSymbol(
                name,
                rtype if rtype is not None else VoidType(),
                category=SymbolCategory.FUNCTION,
                initialized=True,
                init_value_type=None,
                init_note="decl"
            )
            fsym.param_types = param_types
            fsym.return_type = rtype
            fsym.captures = CaptureInfo(captured=[])
            fsym.label = self.makeFuncLabel(name)
            log_semantic(f"[function] declarada: {name}({', '.join(param_names)}) -> {rtype if rtype else 'void'} ; label={fsym.label}")
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))
            log_semantic(f"[error] al declarar función {name}: {e}")
            return self.v.visit(ctx.block())

        # ---- Abrir scope de función y registrar parámetros ----
        self.v.scopeManager.enterScope()
        curr_fn_scope_id = self.v.scopeManager.scopeId
        self.v.fn_ctx_stack.append({
            "scope_id": curr_fn_scope_id,
            "captures": set(),
            "symbol": fsym
        })

        for pname, ptype in zip(param_names, param_types):
            try:
                psym = self.v.scopeManager.addSymbol(
                    pname, ptype, category=SymbolCategory.PARAMETER,
                    initialized=True, init_value_type=None, init_note="param"
                )
                log_semantic(f"[scope.param] {pname}: {ptype}, offset={psym.offset}")
            except Exception as e:
                self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))

        expected_r = rtype if rtype is not None else VoidType()
        self.v.fn_stack.append(expected_r)

        # ---- Emisión TAC: prólogo de función ----
        self.v.emitter.clearFlowTermination()
        self.v.emitter.beginFunction(fsym.label, 0)
        enter_quad = self.v.emitter.quads[-1]
        log_semantic(f"[TAC] beginFunction: label={fsym.label}, frame_size provisional=0")

        # ---- Guardar/limpiar flags de terminación del bloque exterior ----
        saved_term = self.v.stmt_just_terminated
        saved_node = self.v.stmt_just_terminator_node
        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None

        # ---- Visitar cuerpo ----
        prev_fn_body_ctx = getattr(self.v, "_fn_body_block_ctx", None)
        self.v._fn_body_block_ctx = ctx.block()
        block_result = self.v.visit(ctx.block())
        self.v._fn_body_block_ctx = prev_fn_body_ctx
        
        if isinstance(expected_r, VoidType) and (not block_result or not block_result.get("terminated")):
            self.v.emitter.endFunctionWithReturn(None)
            log_semantic(f"[TAC] return implícito en función void {name}")

        self.v.stmt_just_terminated = saved_term
        self.v.stmt_just_terminator_node = saved_node

        self.v.fn_stack.pop()

        fn_ctx = self.v.fn_ctx_stack.pop()
        cap_list = sorted(list(fn_ctx["captures"]), key=lambda x: x[0])
        fsym.captures = CaptureInfo(captured=[(n, t, sid) for (n, t, sid) in cap_list])
        if fsym.captures.captured:
            log_semantic(f"[closure] {name} captura -> {fsym.captures.as_debug()}")

        # ---- Cerrar scope y fijar frame_size ----
        size = self.v.scopeManager.closeFunctionScope(fsym)
        log_semantic(f"[scope] función '{name}' cerrada; frame_size={size} bytes")
        try:
            enter_quad.arg2 = str(size)
        except Exception:
            pass

        self.v.emitter.clearFlowTermination()
        log_semantic(f"[visitFunctionDeclaration] fin: {name}")
        return block_result

        