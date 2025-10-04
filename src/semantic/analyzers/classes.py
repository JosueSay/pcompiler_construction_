from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import ClassType, VoidType, ErrorType
from semantic.symbol_kinds import SymbolCategory
from semantic.registry.type_resolver import resolveTypeCtx, validateKnownTypes
from logs.logger_semantic import log_semantic, log_function
from semantic.errors import SemanticError


class ClassesAnalyzer:
    def __init__(self, v):
        log_semantic("===== [Classes.py] Inicio (SEMÁNTICO) =====")
        self.v = v

    @log_function
    def visitClassDeclaration(self, ctx: CompiscriptParser.ClassDeclarationContext):
        name = ctx.Identifier(0).getText()
        base = ctx.Identifier(1).getText() if len(ctx.Identifier()) > 1 else None
        log_semantic(f"[class] definición: {name}" + (f" : {base}" if base else ""))

        # Registrar en ClassHandler (pre-scan ya validó existencia de base)
        self.v.class_handler.ensureClass(name, base)

        # Scope de clase (para campos)
        self.v.class_stack.append(name)
        self.v.scopeManager.enterScope()

        for mem in ctx.classMember():
            if mem.functionDeclaration():
                # Solo análisis semántico del método (sin TAC)
                self.visitMethodDeclaration(mem.functionDeclaration(), current_class=name)
            else:
                # Campos/const → StatementsAnalyzer (semántico)
                self.v.visit(mem)

        size = self.v.scopeManager.exitScope()
        self.v.class_stack.pop()
        log_semantic(f"[scope] clase '{name}' cerrada; frame_size={size} bytes")
        return None

    @log_function
    def visitMethodDeclaration(self, ctx_fn: CompiscriptParser.FunctionDeclarationContext, *, current_class: str):
        method_name = ctx_fn.Identifier().getText()
        qname = f"{current_class}.{method_name}"
        log_semantic(f"[method] (SEM) inicio: {qname}")

        # 1) parámetros explícitos + 'this'
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
                    ptype = resolveTypeCtx(tctx)
                    validateKnownTypes(
                        ptype, self.v.known_classes, p,
                        f"parámetro '{pname}' de método {qname}", self.v.errors
                    )
                param_names.append(pname)
                param_types.append(ptype)
                log_semantic(f"[param] detectado: {pname}: {ptype}")

        # 2) tipo de retorno
        rtype = None
        if ctx_fn.type_():
            rtype = resolveTypeCtx(ctx_fn.type_())
            validateKnownTypes(
                rtype, self.v.known_classes, ctx_fn,
                f"retorno de método '{qname}'", self.v.errors
            )
        if method_name == "constructor" and rtype is None:
            rtype = VoidType()
        log_semantic(f"[method] (SEM) return type: {rtype if rtype else 'void?'}")

        # --- Override check (solo semántico) ---
        def normalizeRet(rt):
            return rt if rt is not None else VoidType()

        def signaturesEqual(child_params, child_ret, base_params, base_ret):
            if len(child_params) != len(base_params):
                return False
            for a, b in zip(child_params[1:], base_params[1:]):
                if a != b:
                    return False
            return normalizeRet(child_ret) == normalizeRet(base_ret)

        if method_name != "constructor":
            found_base = None
            base_sig = None
            for base in self.v.class_handler.iterBases(current_class):
                bq = f"{base}.{method_name}"
                mt = self.v.method_registry.lookupMethod(bq)
                if mt is not None:
                    found_base = base
                    base_sig = mt
                    break
            if found_base is not None:
                base_params, base_ret = base_sig
                if not signaturesEqual(param_types, rtype, base_params, base_ret):
                    self.v.appendErr(SemanticError(
                        f"Override inválido de '{method_name}' en '{current_class}'; "
                        f"la firma no coincide con la de la clase base '{found_base}'.",
                        line=ctx_fn.start.line, column=ctx_fn.start.column))
                    log_semantic(f"[override] firma inválida detectada en {qname}")

        # 3) Registrar símbolo + registry (sin TAC)
        try:
            fsym = self.v.scopeManager.addSymbolGlobal(
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
            self.v.method_registry.registerMethod(qname, param_types, rtype)
            log_semantic(
                f"[method] (SEM) declarada: {qname}({', '.join(param_names)}) -> {rtype if rtype else 'void?'}"
            )
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx_fn.start.line, column=ctx_fn.start.column))
            return None


        # 4) Scope del método + parámetros (semántico)
        self.v.scopeManager.enterScope()
        self.v.in_method = True
        for pname, ptype in zip(param_names, param_types):
            try:
                psym = self.v.scopeManager.addSymbol(
                    pname, ptype, category=SymbolCategory.PARAMETER,
                    initialized=True, init_value_type=None, init_note="param"
                )
                log_semantic(f"[param] (SEM) {pname}: {ptype}, offset={psym.offset}")
            except Exception as e:
                self.v.appendErr(SemanticError(str(e), line=ctx_fn.start.line, column=ctx_fn.start.column))

        expected_r = rtype if rtype is not None else VoidType()
        self.v.fn_stack.append(expected_r)

        # 5) Analizar cuerpo (semántico)
        block_result = self.v.visit(ctx_fn.block())

        # 6) Cierre de función: calcular frame real (semántico)
        self.v.fn_stack.pop()
        size = self.v.scopeManager.closeFunctionScope(fsym)  # setea fsym.local_frame_size
        log_semantic(f"[scope] (SEM) método '{qname}' cerrado; frame_size={size} bytes")

        self.v.in_method = False
        return block_result
