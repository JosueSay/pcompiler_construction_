from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import ClassType, VoidType, ErrorType
from semantic.symbol_kinds import SymbolCategory
from semantic.registry.type_resolver import resolve_typectx, validate_known_types
from logs.logger_semantic import log_semantic
from semantic.errors import SemanticError
from semantic.custom_types import FunctionType, VoidType as _VoidType

class ClassesAnalyzer:
    def __init__(self, v):
        self.v = v

    def visitClassDeclaration(self, ctx: CompiscriptParser.ClassDeclarationContext):
        name = ctx.Identifier(0).getText()
        base = ctx.Identifier(1).getText() if len(ctx.Identifier()) > 1 else None
        log_semantic(f"[class] definición: {name}" + (f" : {base}" if base else ""))

        # Registrar en ClassHandler (no valida existencia de base aquí; se hizo en pre-scan)
        self.v.class_handler.ensure_class(name, base)

        self.v.class_stack.append(name)
        self.v.scopeManager.enterScope()

        for mem in ctx.classMember():
            if mem.functionDeclaration():
                self._visitMethodDeclaration(mem.functionDeclaration(), current_class=name)
            else:
                self.v.visit(mem)  # variable/const → StatementsAnalyzer

        size = self.v.scopeManager.exitScope()
        self.v.class_stack.pop()
        log_semantic(f"[scope] clase '{name}' cerrada; frame_size={size} bytes")
        return None

    def _visitMethodDeclaration(self, ctx_fn: CompiscriptParser.FunctionDeclarationContext, *, current_class: str):
        method_name = ctx_fn.Identifier().getText()
        qname = f"{current_class}.{method_name}"

        # 1) params explícitos + 'this'
        param_types = [ClassType(current_class)]
        param_names = ["this"]

        if ctx_fn.parameters():
            for p in ctx_fn.parameters().parameter():
                pname = p.Identifier().getText()
                tctx = p.type_()
                if tctx is None:
                    self.v._append_err(SemanticError(
                        f"Parámetro '{pname}' debe declarar tipo (en método {qname}).",
                        line=p.start.line, column=p.start.column))
                    ptype = ErrorType()
                else:
                    ptype = resolve_typectx(tctx)
                    validate_known_types(ptype, self.v.known_classes, p,
                                         f"parámetro '{pname}' de método {qname}", self.v.errors)
                param_names.append(pname)
                param_types.append(ptype)

        # 2) return type
        rtype = None
        if ctx_fn.type_():
            rtype = resolve_typectx(ctx_fn.type_())
            validate_known_types(rtype, self.v.known_classes, ctx_fn,
                                 f"retorno de método '{qname}'", self.v.errors)

        # valirar OVERRIDE con la primera base que tenga el método
        def normalize_ret(rt):
            return rt if rt is not None else VoidType()

        def signatures_equal(child_params, child_ret, base_params, base_ret):
            """
            Compara firmas incluyendo 'this', PERO permite que 'this' sea ClassType distinto
            (Perro vs Animal). Exige igualdad posicional en el resto y en el retorno.
            """
            if len(child_params) != len(base_params):
                return False
            # comparar params desde 1 (ignorar 'this' nominalmente distinto)
            for a, b in zip(child_params[1:], base_params[1:]):
                if a != b:
                    return False
            return normalize_ret(child_ret) == normalize_ret(base_ret)

        # buscar método en la jerarquía de bases
        found_base = None
        base_sig = None
        for base in self.v.class_handler.iter_bases(current_class):
            bq = f"{base}.{method_name}"
            mt = self.v.method_registry.lookup(bq)
            if mt is not None:
                found_base = base
                base_sig = mt  # (param_types, return_type)
                break

        if found_base is not None:
            base_params, base_ret = base_sig
            if not signatures_equal(param_types, rtype, base_params, base_ret):
                self.v._append_err(SemanticError(
                    f"Override inválido de '{method_name}' en '{current_class}'; "
                    f"la firma no coincide con la de la clase base '{found_base}'.",
                    line=ctx_fn.start.line, column=ctx_fn.start.column))

        # 3) registrar símbolo y en registry
        try:
            fsym = self.v.scopeManager.addSymbol(
                qname,
                rtype if rtype is not None else VoidType(),
                category=SymbolCategory.FUNCTION,
                initialized=True,
                init_value_type=None,
                init_note="decl"
            )
            fsym.param_types = param_types
            fsym.return_type = rtype

            self.v.method_registry.register(qname, param_types, rtype)

            log_semantic(f"[method] declarada: {qname}({', '.join(param_names)}) -> {rtype if rtype else 'void?'}")
        except Exception as e:
            self.v._append_err(SemanticError(str(e), line=ctx_fn.start.line, column=ctx_fn.start.column))
            return self.v.visit(ctx_fn.block())

        # 4) scope de método + params
        self.v.scopeManager.enterScope()
        self.v.in_method = True
        for pname, ptype in zip(param_names, param_types):
            try:
                psym = self.v.scopeManager.addSymbol(
                    pname, ptype, category=SymbolCategory.PARAMETER,
                    initialized=True, init_value_type=None, init_note="param"
                )
                log_semantic(f"[param] {pname}: {ptype}, offset={psym.offset}")
            except Exception as e:
                self.v._append_err(SemanticError(str(e), line=ctx_fn.start.line, column=ctx_fn.start.column))

        expected_r = rtype if rtype is not None else VoidType()
        self.v.fn_stack.append(expected_r)
        self.v.visit(ctx_fn.block())
        self.v.fn_stack.pop()

        size = self.v.scopeManager.exitScope()
        self.v.in_method = False
        log_semantic(f"[scope] método '{qname}' cerrado; frame_size={size} bytes")
        return None
