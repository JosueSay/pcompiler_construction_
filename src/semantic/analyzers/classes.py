from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import ClassType, VoidType, ErrorType
from semantic.symbol_kinds import SymbolCategory
from semantic.registry.type_resolver import resolve_typectx, validate_known_types
from logs.logger_semantic import log_semantic, log_function
from semantic.errors import SemanticError

class ClassesAnalyzer:
    def __init__(self, v):
        log_semantic("===== [Classes.py] Inicio =====")
        self.v = v

    @log_function
    def visitClassDeclaration(self, ctx: CompiscriptParser.ClassDeclarationContext):
        name = ctx.Identifier(0).getText()
        base = ctx.Identifier(1).getText() if len(ctx.Identifier()) > 1 else None
        log_semantic(f"[class] definición: {name}" + (f" : {base}" if base else ""))

        # Registrar en ClassHandler (no valida existencia de base aquí; se hizo en pre-scan)
        self.v.class_handler.ensureClass(name, base)

        self.v.class_stack.append(name)
        self.v.scopeManager.enterScope()

        for mem in ctx.classMember():
            if mem.functionDeclaration():
                self.visitMethodDeclaration(mem.functionDeclaration(), current_class=name)
            else:
                self.v.visit(mem)  # variable/const → StatementsAnalyzer

        size = self.v.scopeManager.exitScope()
        self.v.class_stack.pop()
        log_semantic(f"[scope] clase '{name}' cerrada; frame_size={size} bytes")
        return None

    @log_function
    def visitMethodDeclaration(self, ctx_fn: CompiscriptParser.FunctionDeclarationContext, *, current_class: str):
        method_name = ctx_fn.Identifier().getText()
        qname = f"{current_class}.{method_name}"
        log_semantic(f"[method] inicio: {qname}")

        # 1) params explícitos + 'this'
        param_types = [ClassType(current_class)]
        param_names = ["this"]

        if ctx_fn.parameters():
            for p in ctx_fn.parameters().parameter():
                pname = p.Identifier().getText()
                tctx = p.type_()
                if tctx is None:
                    self.v.appendErr(SemanticError(
                        f"Parámetro '{pname}' debe declarar tipo (en método {qname}).",
                        line=p.start.line, column=p.start.column))
                    ptype = ErrorType()
                else:
                    ptype = resolve_typectx(tctx)
                    validate_known_types(ptype, self.v.known_classes, p,
                                        f"parámetro '{pname}' de método {qname}", self.v.errors)
                param_names.append(pname)
                param_types.append(ptype)
                log_semantic(f"[param] detectado: {pname}: {ptype}")

        # 2) return type
        rtype = None
        if ctx_fn.type_():
            rtype = resolve_typectx(ctx_fn.type_())
            validate_known_types(rtype, self.v.known_classes, ctx_fn,
                                f"retorno de método '{qname}'", self.v.errors)
        if method_name == "constructor" and rtype is None:
            rtype = VoidType()
        log_semantic(f"[method] return type: {rtype if rtype else 'void?'}")

        # --- Override check (igual que antes) ---
        def normalize_ret(rt):
            return rt if rt is not None else VoidType()

        def signatures_equal(child_params, child_ret, base_params, base_ret):
            if len(child_params) != len(base_params):
                return False
            for a, b in zip(child_params[1:], base_params[1:]):
                if a != b:
                    return False
            return normalize_ret(child_ret) == normalize_ret(base_ret)

        if method_name != "constructor":
            found_base = None
            base_sig = None
            for base in self.v.class_handler.iter_bases(current_class):
                bq = f"{base}.{method_name}"
                mt = self.v.method_registry.lookup(bq)
                if mt is not None:
                    found_base = base
                    base_sig = mt
                    break
            if found_base is not None:
                base_params, base_ret = base_sig
                if not signatures_equal(param_types, rtype, base_params, base_ret):
                    self.v.appendErr(SemanticError(
                        f"Override inválido de '{method_name}' en '{current_class}'; "
                        f"la firma no coincide con la de la clase base '{found_base}'.",
                        line=ctx_fn.start.line, column=ctx_fn.start.column))
                    log_semantic(f"[override] firma inválida detectada en {qname}")

        # 3) Registrar símbolo + registry (igual que antes)
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
            fsym.label = f"f_{current_class}_{method_name}"
            self.v.method_registry.register(qname, param_types, rtype)
            log_semantic(f"[method] declarada: {qname}({', '.join(param_names)}) -> {rtype if rtype else 'void?'}")
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx_fn.start.line, column=ctx_fn.start.column))
            return self.v.visit(ctx_fn.block())

        # 4) Scope del método + parámetros
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
                self.v.appendErr(SemanticError(str(e), line=ctx_fn.start.line, column=ctx_fn.start.column))

        expected_r = rtype if rtype is not None else VoidType()
        self.v.fn_stack.append(expected_r)

        # --- TAC: prólogo (label + enter 0) ---
        self.v.emitter.clearFlowTermination()
        self.v.emitter.beginFunction(fsym.label, 0)
        enter_quad = self.v.emitter.quads[-1]
        log_semantic(f"[TAC] beginFunction (method): label={fsym.label}, frame_size provisional=0")

        # Guardar/limpiar flags de terminación del bloque exterior
        saved_term = self.v.stmt_just_terminated
        saved_node = getattr(self.v, "stmt_just_terminator_node", None)
        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None

        # 5) Visitar cuerpo
        try:
            block_result = self.v.visit(ctx_fn.block())
        finally:
            # Restaurar flags externos
            self.v.stmt_just_terminated = saved_term
            self.v.stmt_just_terminator_node = saved_node

        # Si es void y no terminó el flujo, return implícito
        from semantic.custom_types import VoidType as _VT  # evitar confusión local
        if isinstance(expected_r, _VT) and (not block_result or not block_result.get("terminated")):
            self.v.emitter.endFunctionWithReturn(None)
            log_semantic(f"[TAC] return implícito en método/ctor {qname}")

        # 6) Cierre de función: parchar frame_size real en 'enter'
        self.v.fn_stack.pop()
        size = self.v.scopeManager.closeFunctionScope(fsym)  # setea fsym.local_frame_size
        log_semantic(f"[scope] método '{qname}' cerrado; frame_size={size} bytes")
        try:
            enter_quad.arg2 = str(size)
        except Exception:
            pass

        self.v.in_method = False
        self.v.emitter.clearFlowTermination()
        return block_result
