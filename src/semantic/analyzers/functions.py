from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import VoidType, ErrorType
from semantic.symbol_kinds import SymbolCategory
from semantic.registry.type_resolver import resolve_typectx, validate_known_types
from semantic.registry.closure_model import CaptureInfo
from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic


class FunctionsAnalyzer:
    def __init__(self, v):
        self.v = v

    def _make_func_label(self, name: str) -> str:
        """
        Convención de etiquetas:
          - Función libre: f_<name>
          - (Si alguna vez se declarara dentro de clase) f_<Class>_<name>
        """
        if getattr(self.v, "class_stack", None):
            owner = self.v.class_stack[-1] if self.v.class_stack else None
        else:
            owner = None
        return f"f_{owner}_{name}" if owner else f"f_{name}"

    def visitFunctionDeclaration(self, ctx: CompiscriptParser.FunctionDeclarationContext):
        name = ctx.Identifier().getText()

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

        # ---- Tipo de retorno ----
        rtype = None
        if ctx.type_():
            rtype = resolve_typectx(ctx.type_())
            validate_known_types(rtype, self.v.known_classes, ctx,
                                 f"retorno de función '{name}'", self.v.errors)

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

            # etiqueta para llamadas (TAC)
            fsym.label = self._make_func_label(name)

            log_semantic(f"[function] declarada: {name}({', '.join(param_names)}) -> {rtype if rtype else 'void?'} ; label={fsym.label}")
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))
            # Aun así visitamos el cuerpo para no perder errores
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
                log_semantic(f"[param] {pname}: {ptype}, offset={psym.offset}")
            except Exception as e:
                self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))

        # Pila de tipos esperados para 'return'
        expected_r = rtype if rtype is not None else VoidType()
        self.v.fn_stack.append(expected_r)

        # ---- Emisión TAC: prólogo de función (label + enter) ----
        # Limpiar cualquier barrera previa (por si una función anterior terminó en 'return')
        self.v.emitter.clearFlowTermination()
        # Emitimos con frame_size=0 y lo parchamos al cerrar el scope
        self.v.emitter.beginFunction(fsym.label, 0)
        enter_quad = self.v.emitter.quads[-1]  # el último es el ENTER recién emitido

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
        
        # si es void y no terminó por return/break total, emite return implícito
        if isinstance(expected_r, VoidType) and (not block_result or not block_result.get("terminated")):
            self.v.emitter.endFunctionWithReturn(None)

        # ---- Restaurar flags para no propagar al padre ----
        self.v.stmt_just_terminated = saved_term
        self.v.stmt_just_terminator_node = saved_node

        # Salir de pilas de función
        self.v.fn_stack.pop()

        fn_ctx = self.v.fn_ctx_stack.pop()
        cap_list = sorted(list(fn_ctx["captures"]), key=lambda x: x[0])
        fsym.captures = CaptureInfo(captured=[(n, t, sid) for (n, t, sid) in cap_list])
        if fsym.captures.captured:
            log_semantic(f"[closure] {name} captura -> {fsym.captures.as_debug()}")

        # ---- Cerrar scope y fijar frame_size ----
        size = self.v.scopeManager.closeFunctionScope(fsym)
        log_semantic(f"[scope] función '{name}' cerrada; frame_size={size} bytes")

        # Parchear el ENTER con el tamaño real del frame
        try:
            enter_quad.arg2 = str(size)
        except Exception:
            pass
        
        self.v.emitter.clearFlowTermination()
        return block_result
        