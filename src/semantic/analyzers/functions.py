from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import VoidType, ErrorType
from semantic.symbol_kinds import SymbolCategory
from semantic.registry.type_resolver import resolve_typectx, validate_known_types
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
            log_semantic(f"[function] declarada: {name}({', '.join(param_names)}) -> {rtype if rtype else 'void?'}")
        except Exception as e:
            self.v._append_err(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))
            return self.v.visit(ctx.block())

        self.v.scopeManager.enterScope()
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
        self.v.visit(ctx.block())
        self.v.fn_stack.pop()

        size = self.v.scopeManager.exitScope()
        log_semantic(f"[scope] función '{name}' cerrada; frame_size={size} bytes")
        return None
