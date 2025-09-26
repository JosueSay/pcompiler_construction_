from semantic.symbol_kinds import SymbolCategory
from semantic.custom_types import NullType, ErrorType, ArrayType, IntegerType, VoidType, ClassType
from semantic.type_system import isAssignable, isReferenceType
from semantic.registry.type_resolver import resolve_annotated_type, validate_known_types
from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic
from ir.tac import Op

class StatementsAnalyzer:
    def __init__(self, v):
        self.v = v

    def visitExpressionStatement(self, ctx):
        t = self.v.visit(ctx.expression())
        self.v.emitter.temp_pool.resetPerStatement()
        return t

    def visitBlock(self, ctx):
        """
        Bloque con detección de 'código muerto':
        - Si una sentencia termina el flujo (return/break/continue o if-else donde
          ambas ramas terminan), se marca el resto como inalcanzable.
        - Reportamos el diagnóstico pero seguimos visitando para no perder otros errores.
        """
        self.v.scopeManager.enterScope()

        terminated_in_block = False
        terminator_reason = None

        for st in ctx.statement():
            # Si ya sabemos que el flujo terminó antes de esta sentencia => dead code
            if terminated_in_block:
                
                try:# línea/col seguras si el nodo tiene 'start'
                    line = st.start.line
                    col = st.start.column
                except Exception:
                    line = None
                    col = None
                self.v.appendErr(SemanticError(
                    f"Código inalcanzable: el flujo terminó por '{terminator_reason}' antes de esta sentencia.",
                    line=line, column=col, error_type="DeadCode"))
                # Aún así, visitamos para seguir chequeando tipos/errores
                self.v.visit(st)
                continue

            # Reiniciar el flag que marcan las sentencias terminantes
            self.v.stmt_just_terminated = None
            self.v.stmt_just_terminator_node = None

            # Visitar sentencia normalmente
            result = self.v.visit(st)

            # ¿La sentencia que acabamos de visitar terminó el flujo?
            if self.v.stmt_just_terminated:
                terminated_in_block = True
                terminator_reason = self.v.stmt_just_terminated

        size = self.v.scopeManager.exitScope()
        log_semantic(f"[scope] bloque cerrado; frame_size={size} bytes")

        # Devolvemos un pequeño resultado para que estructuras como if/else
        return {
            "terminated": terminated_in_block,
            "reason": terminator_reason
        }

    def visitVariableDeclaration(self, ctx):
        """
        Declara variables con **init opcional**.

        Reglas:
        - Debe existir anotación de tipo (no hay inferencia).
        - `void` no es válido como tipo de variable.
        - Si NO hay inicializador:
            * Tipos de **referencia** (clase / arreglos / function): se inicializan a **null**
            (initialized=True, init_value_type=NullType, init_note="default-null").
            * Tipos **valor** (integer, boolean, string): se permiten **sin inicializar**
            (initialized=False, init_value_type=None, init_note="uninitialized").
            > Nota: El uso previo a asignación deberá marcarse como error en el visit de identificadores.
        - Si hay inicializador:
            * Se valida asignabilidad `declared_type ← rhs_type`.
            * Se marca initialized=True, con `init_value_type=rhs_type`.

        Además:
        - Se registra el símbolo en la tabla (o error si hay colisión).
        - Si estamos dentro de una **clase**, se registra el **atributo** con su tipo declarado.
        """
        name = ctx.Identifier().getText()
        ann = ctx.typeAnnotation()
        init = ctx.initializer()

        if ann is None:
            self.v.appendErr(SemanticError(
                f"La variable '{name}' debe declarar un tipo (no se permite inferencia).",
                line=ctx.start.line, column=ctx.start.column))
            self.v.emitter.temp_pool.resetPerStatement()
            return

        declared_type = resolve_annotated_type(ann)
        if not validate_known_types(declared_type, self.v.known_classes, ctx, f"variable '{name}'", self.v.errors):
            self.v.emitter.temp_pool.resetPerStatement()
            return

        if isinstance(declared_type, VoidType):
            self.v.appendErr(SemanticError(
                f"La variable '{name}' no puede ser de tipo void.",
                line=ctx.start.line, column=ctx.start.column))
            self.v.emitter.temp_pool.resetPerStatement()
            return

        initialized = False
        init_value_type = None
        init_note = None

        # --- Sin inicializador: permitir declaración laxa ---
        if not init:
            if isReferenceType(declared_type):
                # Referencias: default a null
                initialized = True
                init_value_type = NullType()
                init_note = "default-null"
            else:
                # Tipos valor: permitido sin inicializar
                initialized = False
                init_value_type = None
                init_note = "uninitialized"
        else:
            # --- Con inicializador: validar asignabilidad ---
            rhs_type = self.v.visit(init.expression())
            if rhs_type is None:
                self.v.emitter.temp_pool.resetPerStatement()
                return
            if not isAssignable(declared_type, rhs_type):
                self.v.appendErr(SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_type} a {declared_type} en '{name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                # En contexto de clase, aún registramos el atributo con el tipo declarado
                if self.v.class_stack:
                    current_class = self.v.class_stack[-1]
                    self.v.class_handler.add_attribute(current_class, name, declared_type)
                    log_semantic(f"[class.attr] {current_class}.{name}: {declared_type} (registrado pese a asignación incompatible)")
                self.v.emitter.temp_pool.resetPerStatement()
                return
            initialized = True
            init_value_type = rhs_type
            init_note = "explicit"

        # --- Declarar símbolo ---
        try:
            sym = self.v.scopeManager.addSymbol(
                name, declared_type, category=SymbolCategory.VARIABLE,
                initialized=initialized, init_value_type=init_value_type, init_note=init_note
            )
            msg = f"Variable '{name}' declarada con tipo: {declared_type}, tamaño: {sym.width} bytes"
            msg += f" (initialized={sym.initialized}"
            msg += f", init_value_type={sym.init_value_type}" if sym.init_value_type is not None else ""
            msg += f", note={sym.init_note}" if sym.init_note else ""
            msg += ")"
            log_semantic(msg)
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))
            self.v.emitter.temp_pool.resetPerStatement()
            return

        # --- Atributo de clase (si aplica) ---
        if self.v.class_stack:
            current_class = self.v.class_stack[-1]
            self.v.class_handler.add_attribute(current_class, name, declared_type)
            log_semantic(f"[class.attr] {current_class}.{name}: {declared_type}")
        
        # --- Emisión TAC del inicializador ---
        if init is not None:
            p, _ = self.v.exprs.deepPlace(init.expression())
            rhs_place = p or init.expression().getText()
            self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=name)

        # Reinicio de temporales por sentencia
        self.v.emitter.temp_pool.resetPerStatement()


    def visitConstantDeclaration(self, ctx):
        name = ctx.Identifier().getText() if ctx.Identifier() else "<unnamed-const>"
        ann = ctx.typeAnnotation()
        expr_ctx = ctx.expression()

        if ann is None:
            self.v.appendErr(SemanticError(
                f"La constante '{name}' debe declarar un tipo.",
                line=ctx.start.line, column=ctx.start.column))
            self.v.emitter.temp_pool.resetPerStatement()
            return

        declared_type = resolve_annotated_type(ann)
        if not validate_known_types(declared_type, self.v.known_classes, ctx, f"constante '{name}'", self.v.errors):
            self.v.emitter.temp_pool.resetPerStatement()
            return

        if isinstance(declared_type, VoidType):
            self.v.appendErr(SemanticError(
                f"La constante '{name}' no puede ser de tipo void.",
                line=ctx.start.line, column=ctx.start.column))
            self.v.emitter.temp_pool.resetPerStatement()
            return

        if expr_ctx is None:
            self.v.appendErr(SemanticError(
                f"Constante '{name}' sin inicializar (se requiere '= <expresión>').",
                line=ctx.start.line, column=ctx.start.column))
            self.v.emitter.temp_pool.resetPerStatement()
            return

        rhs_type = self.v.visit(expr_ctx)
        if rhs_type is None:
            self.v.emitter.temp_pool.resetPerStatement()
            return

        if not isAssignable(declared_type, rhs_type):
            self.v.appendErr(SemanticError(
                f"Asignación incompatible: no se puede asignar {rhs_type} a {declared_type} en constante '{name}'.",
                line=ctx.start.line, column=ctx.start.column))
            self.v.emitter.temp_pool.resetPerStatement()
            return

        try:
            sym = self.v.scopeManager.addSymbol(name, declared_type, category=SymbolCategory.CONSTANT)
            log_semantic(f"Constante '{name}' declarada con tipo: {declared_type}, tamaño: {sym.width} bytes")
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))
            self.v.emitter.temp_pool.resetPerStatement()
            return
        
        # Emisión TAC: k = <expr.place>
        p, _ = self.v.exprs.deepPlace(expr_ctx)
        rhs_place = p or expr_ctx.getText()
        self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=name)



        # Reinicio de temporales por sentencia
        self.v.emitter.temp_pool.resetPerStatement()

    def visitAssignment(self, ctx):
        """
        Soporta:
        1) Identifier '=' expression ';'
        2) expression '.' Identifier '=' expression ';'   (asignación a propiedad)
        """
        exprs = list(ctx.expression())
        n = len(exprs)

        # Caso 1: asignación a variable simple
        if n == 1 and ctx.Identifier() is not None:
            name = ctx.Identifier().getText()
            sym = self.v.scopeManager.lookup(name)
            if sym is None:
                self.v.appendErr(SemanticError(
                    f"Uso de variable no declarada: '{name}'",
                    line=ctx.start.line, column=ctx.start.column))
                self.v.emitter.temp_pool.resetPerStatement()
                return
            if sym.category == SymbolCategory.CONSTANT:
                self.v.appendErr(SemanticError(
                    f"No se puede modificar la constante '{name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                self.v.emitter.temp_pool.resetPerStatement()
                return

            rhs_type = self.v.visit(exprs[0])
            if rhs_type is None:
                self.v.emitter.temp_pool.resetPerStatement()
                return
            if not isAssignable(sym.type, rhs_type):
                self.v.appendErr(SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_type} a {sym.type} en '{name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                self.v.emitter.temp_pool.resetPerStatement()
                return

            # TAC: name = <expr.place>
            p, _ = self.v.exprs.deepPlace(exprs[0])
            rhs_place = p or exprs[0].getText()
            self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=name)
            self.v.emitter.temp_pool.resetPerStatement()
            return


        # Caso 2: obj.prop = expr
        if n == 2:
            lhs_obj = exprs[0]
            rhs_exp = exprs[1]

            prop_tok = ctx.Identifier()
            try:
                prop_name = prop_tok.getText()
            except Exception:
                prop_name = prop_tok[0].getText() if prop_tok else "<prop>"

            obj_t = self.v.visit(lhs_obj)
            if not isinstance(obj_t, ClassType):
                self.v.appendErr(SemanticError(
                    f"Asig. a propiedad en no-objeto: '{obj_t}'.",
                    line=ctx.start.line, column=ctx.start.column))
                self.v.emitter.temp_pool.resetPerStatement()
                return

            class_name = obj_t.name
            prop_t = self.v.class_handler.get_attribute_type(class_name, prop_name)
            if prop_t is None:
                self.v.appendErr(SemanticError(
                    f"Miembro '{prop_name}' no declarado en clase '{class_name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                self.v.emitter.temp_pool.resetPerStatement()
                return

            rhs_t = self.v.visit(rhs_exp)
            if not isAssignable(prop_t, rhs_t):
                self.v.appendErr(SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_t} a {prop_t} en '{class_name}.{prop_name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                self.v.emitter.temp_pool.resetPerStatement()
                return

            # TAC: obj.prop = <rhs.place>
            p_obj, _ = self.v.exprs.deepPlace(lhs_obj)
            obj_place = p_obj or lhs_obj.getText()
            p_rhs, _ = self.v.exprs.deepPlace(rhs_exp)
            rhs_place = p_rhs or rhs_exp.getText()
            self.v.emitter.emit(Op.FIELD_STORE, arg1=obj_place, res=rhs_place, label=prop_name)
            self.v.emitter.temp_pool.resetPerStatement()
            return


        # Fallback
        self.v.appendErr(SemanticError(
            "Asignación aún no soportada en esta forma por la fase actual.",
            line=ctx.start.line, column=ctx.start.column))
        self.v.emitter.temp_pool.resetPerStatement()

    def visitForeachStatement(self, ctx):
        iter_name = ctx.Identifier().getText()
        iter_expr_type = self.v.visit(ctx.expression())

        if isinstance(iter_expr_type, ArrayType):
            elem_type = iter_expr_type.elem_type
        else:
            if not isinstance(iter_expr_type, ErrorType):
                self.v.appendErr(SemanticError(
                    f"foreach requiere un arreglo; se encontró {iter_expr_type}.",
                    line=ctx.start.line, column=ctx.start.column))
            elem_type = ErrorType()

        self.v.scopeManager.enterScope()
        try:
            sym = self.v.scopeManager.addSymbol(
                iter_name, elem_type, category=SymbolCategory.VARIABLE,
                initialized=True, init_value_type=elem_type, init_note="foreach-var"
            )
            log_semantic(f"Foreach var '{iter_name}' declarada con tipo: {elem_type}, tamaño: {sym.width} bytes (note=foreach-var)")
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))

        self.v.visit(ctx.block())
        size = self.v.scopeManager.exitScope()
        log_semantic(f"[scope] foreach cerrado; frame_size={size} bytes")

        self.v.emitter.temp_pool.resetPerStatement()
        return {"terminated": False, "reason": None}