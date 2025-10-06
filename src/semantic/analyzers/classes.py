from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import ClassType, VoidType, ErrorType
from semantic.symbol_kinds import SymbolCategory
from semantic.registry.type_resolver import resolveTypeCtx, validateKnownTypes
from logs.logger import log, logFunction
from semantic.errors import SemanticError


class ClassesAnalyzer:
    """
    Analizador semántico para **clases y métodos**.

    Responsabilidades:
      - Registrar clases y su base en `ClassHandler`.
      - Crear el scope de clase (para campos) y visitar sus miembros.
      - Validar/registrar la firma de métodos (parámetros + retorno),
        incluyendo `this` como primer parámetro implícito.
      - Verificar overrides contra la jerarquía (coincidencia de firma).
      - Abrir/cerrar el scope del método y registrar parámetros.
      - Calcular y fijar el `local_frame_size` del método al cerrar el scope.

    Notas de diseño (modo semantic):
      - Las funciones públicas están en camelCase.
      - Las variables internas usan snake_case.
      - Se registran logs en el canal "semantic".
      - No se modifica la lógica funcional existente.
    """

    def __init__(self, v):
        log("===== [ClassesAnalyzer] Inicio (SEMÁNTICO) =====", channel="semantic")
        self.v = v

    @logFunction(channel="semantic")
    def visitClassDeclaration(self, ctx: CompiscriptParser.ClassDeclarationContext):
        """
        Registra la clase (y su base si existe), abre el scope de clase,
        visita sus miembros y cierra el scope.
        """
        name = ctx.Identifier(0).getText()
        base = ctx.Identifier(1).getText() if len(ctx.Identifier()) > 1 else None
        log(f"[class] definición: {name}" + (f" : {base}" if base else ""), channel="semantic")

        # Registrar en ClassHandler (pre-scan ya validó existencia de base)
        self.v.class_handler.ensureClass(name, base)

        # Scope de clase (campos)
        self.v.class_stack.append(name)
        self.v.scopeManager.enterScope()

        for mem in ctx.classMember():
            if mem.functionDeclaration():
                # Solo análisis semántico del método (sin TAC aquí)
                self.visitMethodDeclaration(mem.functionDeclaration(), current_class=name)
            else:
                # Campos/const → lo maneja el analizador de sentencias
                self.v.visit(mem)

        size = self.v.scopeManager.exitScope()
        self.v.class_stack.pop()
        log(f"[scope] clase '{name}' cerrada; frame_size={size} bytes", channel="semantic")
        return None

    @logFunction(channel="semantic")
    def visitMethodDeclaration(self, ctx_fn: CompiscriptParser.FunctionDeclarationContext, *, current_class: str):
        """
        Registra/valida la firma del método (params + retorno), verifica overrides,
        crea el scope del método con parámetros (incluido `this`), visita el cuerpo
        y fija el `local_frame_size` al cerrar.
        """
        method_name = ctx_fn.Identifier().getText()
        qname = f"{current_class}.{method_name}"
        log(f"[method] (SEM) inicio: {qname}", channel="semantic")

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
                log(f"[param] detectado: {pname}: {ptype}", channel="semantic")

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
        log(f"[method] (SEM) return type: {rtype if rtype else 'void?'}", channel="semantic")

        # --- Override check (solo semántico) ---
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
            for base in self.v.class_handler.iterBases(current_class):
                bq = f"{base}.{method_name}"
                mt = self.v.method_registry.lookupMethod(bq)
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
                    log(f"[override] firma inválida detectada en {qname}", channel="semantic")

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
            fsym.label = f"{current_class}_{method_name}"
            self.v.method_registry.registerMethod(qname, param_types, rtype)
            log(
                f"[method] (SEM) declarada: {qname}({', '.join(param_names)}) -> {rtype if rtype else 'void?'}",
                channel="semantic",
            )
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx_fn.start.line, column=ctx_fn.start.column))
            return None

        # 4) Scope del método + parámetros
        self.v.scopeManager.enterFunctionScope()
        self.v.in_method = True
        for pname, ptype in zip(param_names, param_types):
            try:
                psym = self.v.scopeManager.addSymbol(
                    pname, ptype, category=SymbolCategory.PARAMETER,
                    initialized=True, init_value_type=None, init_note="param"
                )
                log(f"[param] (SEM) {pname}: {ptype}, offset={psym.offset}", channel="semantic")
            except Exception as e:
                self.v.appendErr(SemanticError(str(e), line=ctx_fn.start.line, column=ctx_fn.start.column))

        expected_r = rtype if rtype is not None else VoidType()
        self.v.fn_stack.append(expected_r)

        # 5) Analizar cuerpo (semántico)
        block_result = self.v.visit(ctx_fn.block())

        # 6) Cierre: calcular frame real y fijarlo en el símbolo
        self.v.fn_stack.pop()
        size = self.v.scopeManager.closeFunctionScope(fsym)  # setea fsym.local_frame_size
        log(f"[scope] (SEM) método '{qname}' cerrado; frame_size={size} bytes", channel="semantic")

        self.v.in_method = False
        return block_result
