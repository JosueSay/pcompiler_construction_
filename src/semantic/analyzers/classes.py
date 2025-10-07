from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import ClassType, VoidType, ErrorType
from semantic.symbol_kinds import SymbolCategory
from semantic.registry.type_resolver import resolveTypeCtx, validateKnownTypes
from logs.logger import log, logFunction
from semantic.errors import SemanticError


class ClassesAnalyzer:
    """
    Analizador semántico para clases y métodos con logs estilo TAC.
    """

    def __init__(self, v):
        log("\n" + "="*80, channel="semantic")
        log("===== [ClassesAnalyzer] Inicio SEMÁNTICO =====", channel="semantic")
        log("="*80 + "\n", channel="semantic")
        self.v = v

    def visitClassDeclaration(self, ctx: CompiscriptParser.ClassDeclarationContext):
        name = ctx.Identifier(0).getText()
        base = ctx.Identifier(1).getText() if len(ctx.Identifier()) > 1 else None
        log(f"[class] definición: {name}" + (f" : {base}" if base else ""), channel="semantic")

        self.v.class_handler.ensureClass(name, base)

        self.v.class_stack.append(name)
        self.v.scopeManager.enterScope()

        for mem in ctx.classMember():
            if mem.functionDeclaration():
                self.visitMethodDeclaration(mem.functionDeclaration(), current_class=name)
            else:
                self.v.visit(mem)

        size = self.v.scopeManager.exitScope()
        self.v.class_stack.pop()
        log(f"[scope] clase '{name}' cerrada; frame_size={size} bytes", channel="semantic")
        return None

    def visitMethodDeclaration(self, ctx_fn: CompiscriptParser.FunctionDeclarationContext, *, current_class: str):
        method_name = ctx_fn.Identifier().getText()
        qname = f"{current_class}.{method_name}"
        log("\n" + "-"*80, channel="semantic")
        log(f"[method] inicio: {qname}", channel="semantic")

        # Parámetros (incluye 'this')
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
                log(f"\t[param] detectado: {pname}: {ptype}", channel="semantic")

        # Tipo de retorno
        rtype = resolveTypeCtx(ctx_fn.type_()) if ctx_fn.type_() else None
        if method_name == "constructor" and rtype is None:
            rtype = VoidType()
        log(f"\t[method] tipo retorno: {rtype if rtype else 'void?'}", channel="semantic")

        # Registrar función en el scope global
        try:
            fsym = self.v.scopeManager.addSymbolGlobal(
                qname,
                rtype if rtype is not None else VoidType(),
                category=SymbolCategory.FUNCTION,
                initialized=True, init_value_type=None, init_note="decl"
            )
            fsym.param_types = param_types
            fsym.return_type = rtype
            fsym.label = f"{current_class}_{method_name}"
            self.v.method_registry.registerMethod(qname, param_types, rtype)
            log(f"\t[method] registrada: {qname}({', '.join(param_names)})", channel="semantic")
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx_fn.start.line, column=ctx_fn.start.column))
            return None

        # Scope del método
        fn_scope_id = self.v.scopeManager.enterFunctionScope()  # devuelve el ID real del scope
        setattr(fsym, "func_scope_id", fn_scope_id)            # nuevo atributo para scope de ejecución
        log(f"[SEM] set {qname}.func_scope_id={fn_scope_id}", channel="semantic")
     
        
        
        self.v.in_method = True
        for pname, ptype in zip(param_names, param_types):
            try:
                psym = self.v.scopeManager.addSymbol(
                    pname, ptype, category=SymbolCategory.PARAMETER,
                    initialized=True, init_value_type=None, init_note="param"
                )
                log(f"\t[param] registrado: {pname}: {ptype}, offset={psym.offset}", channel="semantic")
            except Exception as e:
                self.v.appendErr(SemanticError(str(e), line=ctx_fn.start.line, column=ctx_fn.start.column))

        self.v.fn_stack.append(rtype if rtype else VoidType())
        # --- marcar el cuerpo del método para que NO abra un scope extra ---
        _prev_body = getattr(self.v, "_fn_body_block_ctx", None)
        self.v._fn_body_block_ctx = ctx_fn.block()
        try:
            block_result = self.v.visit(ctx_fn.block())
        finally:
            # restaurar siempre
            self.v._fn_body_block_ctx = _prev_body
            self.v.fn_stack.pop()

        size = self.v.scopeManager.closeFunctionScope(fsym)
        log(f"[scope] método '{qname}' cerrado; frame_size={size} bytes", channel="semantic")
        if fn_scope_id is not None:
            log(f"[SEM] set {qname}.fn_scope_id={fn_scope_id}; frame={size}", channel="semantic")
            
        self.v.in_method = False
        log("-"*80 + "\n", channel="semantic")

        return block_result
