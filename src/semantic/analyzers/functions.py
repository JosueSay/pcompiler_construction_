from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import VoidType, ErrorType
from semantic.symbol_kinds import SymbolCategory
from semantic.registry.type_resolver import resolveTypeCtx, validateKnownTypes
from semantic.registry.closure_model import CaptureInfo
from semantic.errors import SemanticError
from logs.logger import log, logFunction


class FunctionsAnalyzer:
    """
    Análisis **semántico** de funciones (solo tipos; sin emisión de TAC).
    - Resuelve tipos de parámetros y del retorno.
    - Declara el símbolo de la función en el scope y fija su `label`.
    - Abre scope para parámetros, analiza el cuerpo bajo barrera (sin TAC).
    - Registra capturas para funciones anidadas (closures).
    - Cierra el scope fijando `local_frame_size` en el símbolo.
    """

    @logFunction(channel="semantic")
    def __init__(self, v):
        log("===== [Functions.py] Inicio (SEMÁNTICO) =====", channel="semantic")
        self.v = v

    @logFunction(channel="semantic")
    def makeFuncLabel(self, name: str) -> str:
        """
        Convención de etiquetas:
          - Función libre:  f_<name>
          - (Si está anidada en clase) f_<Class>_<name>
        """
        owner = self.v.class_stack[-1] if getattr(self.v, "class_stack", None) else None
        label = f"{owner}_{name}" if owner else f"{name}"
        log(f"[makeFuncLabel] name='{name}', owner='{owner}' -> label='{label}'", channel="semantic")
        return label

    @logFunction(channel="semantic")
    def visitFunctionDeclaration(self, ctx: CompiscriptParser.FunctionDeclarationContext):
        name = ctx.Identifier().getText()
        log(f"[function] (SEM) inicio: {name}", channel="semantic")

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
                    ptype = resolveTypeCtx(tctx)
                    if isinstance(ptype, VoidType):
                        self.v.appendErr(SemanticError(
                            f"Parámetro '{pname}' no puede ser de tipo void.",
                            line=p.start.line, column=p.start.column))
                        ptype = ErrorType()
                    elif not validateKnownTypes(
                        ptype, self.v.known_classes, p,
                        f"parámetro '{pname}'", self.v.errors
                    ):
                        ptype = ErrorType()
                param_names.append(pname)
                param_types.append(ptype)
                log(f"[param] (SEM) {pname}: {ptype}", channel="semantic")

        # ---- Tipo de retorno ----
        rtype = None
        if ctx.type_():
            rtype = resolveTypeCtx(ctx.type_())
            validateKnownTypes(rtype, self.v.known_classes, ctx,
                               f"retorno de función '{name}'", self.v.errors)
        log(f"[return] (SEM) tipo: {rtype if rtype else 'void'}", channel="semantic")

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
            log(f"[function] (SEM) declarada: {name}({', '.join(param_names)}) -> {rtype if rtype else 'void'} ; label={fsym.label}", channel="semantic")
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))
            # Continuar con análisis semántico del cuerpo bajo barrera (sin TAC)
            old_barrier = getattr(self.v, "emitter", None).flow_terminated if hasattr(self.v, "emitter") else None
            if hasattr(self.v, "emitter"):
                self.v.emitter.flow_terminated = True
            try:
                return self.v.visit(ctx.block())
            finally:
                if hasattr(self.v, "emitter"):
                    self.v.emitter.flow_terminated = old_barrier

        # ---- Abrir scope de función y registrar parámetros ----
        self.v.scopeManager.enterScope()
        curr_fn_scope_id = self.v.scopeManager.currentScopeId()
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
                log(f"[scope.param] (SEM) {pname}: {ptype}, offset={psym.offset}", channel="semantic")
            except Exception as e:
                self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))

        expected_r = rtype if rtype is not None else VoidType()
        self.v.fn_stack.append(expected_r)

        # ---- Analizar cuerpo bajo barrera (sin TAC) ----
        old_barrier = getattr(self.v, "emitter", None).flow_terminated if hasattr(self.v, "emitter") else None
        if hasattr(self.v, "emitter"):
            self.v.emitter.flow_terminated = True
        try:
            prev_fn_body_ctx = getattr(self.v, "_fn_body_block_ctx", None)
            self.v._fn_body_block_ctx = ctx.block()
            block_result = self.v.visit(ctx.block())
            self.v._fn_body_block_ctx = prev_fn_body_ctx
        finally:
            if hasattr(self.v, "emitter"):
                self.v.emitter.flow_terminated = old_barrier

        self.v.fn_stack.pop()

        # ---- Capturas (closures) ----
        fn_ctx = self.v.fn_ctx_stack.pop()
        cap_list = sorted(list(fn_ctx["captures"]), key=lambda x: x[0])
        fsym.captures = CaptureInfo(captured=[(n, t, sid) for (n, t, sid) in cap_list])
        if fsym.captures.captured:
            log(f"[closure] (SEM) {name} captura -> {fsym.captures.asDebug()}", channel="semantic")

        # ---- Cerrar scope y fijar frame_size ----
        size = self.v.scopeManager.closeFunctionScope(fsym)
        log(f"[scope] (SEM) función '{name}' cerrada; frame_size={size} bytes", channel="semantic")

        log(f"[function] (SEM) fin: {name}", channel="semantic")
        return block_result
