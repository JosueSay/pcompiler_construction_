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

    def visitFunctionDeclaration(self, ctx: CompiscriptParser.FunctionDeclarationContext):
        name = ctx.Identifier().getText()

        param_types, param_names = [], []
        if ctx.parameters():
            for p in ctx.parameters().parameter():
                pname = p.Identifier().getText()
                tctx = p.type_()
                if tctx is None:
                    self.v._append_err(SemanticError(
                        f"Parámetro '{pname}' debe declarar tipo.",
                        line=p.start.line, column=p.start.column))
                    ptype = ErrorType()
                else:
                    ptype = resolve_typectx(tctx)
                    if isinstance(ptype, VoidType):
                        self.v._append_err(SemanticError(
                            f"Parámetro '{pname}' no puede ser de tipo void.",
                            line=p.start.line, column=p.start.column))
                        ptype = ErrorType()
                    elif not validate_known_types(ptype, self.v.known_classes, p,
                                                  f"parámetro '{pname}'", self.v.errors):
                        ptype = ErrorType()
                param_names.append(pname)
                param_types.append(ptype)

        rtype = None
        if ctx.type_():
            rtype = resolve_typectx(ctx.type_())
            validate_known_types(rtype, self.v.known_classes, ctx,
                                 f"retorno de función '{name}'", self.v.errors)

        # Declaración del símbolo de la función en el scope actual
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
            log_semantic(f"[function] declarada: {name}({', '.join(param_names)}) -> {rtype if rtype else 'void?'}")
        except Exception as e:
            self.v._append_err(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))
            return self.v.visit(ctx.block())

        # Abrir scope de función y registrar parámetros
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
                self.v._append_err(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))

        expected_r = rtype if rtype is not None else VoidType()
        self.v.fn_stack.append(expected_r)
        
        
        # --- guardar flags de terminación del bloque exterior ---
        saved_term = self.v._stmt_just_terminated
        saved_node = self.v._stmt_just_terminator_node
        self.v._stmt_just_terminated = None
        self.v._stmt_just_terminator_node = None
        
        
        block_result = self.v.visit(ctx.block())  # cuerpo de la función

        
        
        # --- restaurar flags para que NO se propaguen al padre ---
        self.v._stmt_just_terminated = saved_term
        self.v._stmt_just_terminator_node = saved_node
        
        self.v.fn_stack.pop()

        fn_ctx = self.v.fn_ctx_stack.pop()
        cap_list = sorted(list(fn_ctx["captures"]), key=lambda x: x[0])
        fsym.captures = CaptureInfo(captured=[(n, t, sid) for (n, t, sid) in cap_list])
        if fsym.captures.captured:
            log_semantic(f"[closure] {name} captura -> {fsym.captures.as_debug()}")

        size = self.v.scopeManager.exitScope()
        log_semantic(f"[scope] función '{name}' cerrada; frame_size={size} bytes")

        return block_result
