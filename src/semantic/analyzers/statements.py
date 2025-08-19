from semantic.symbol_kinds import SymbolCategory
from semantic.custom_types import NullType, ErrorType, ArrayType, IntegerType, VoidType, ClassType
from semantic.type_system import isAssignable, isReferenceType
from semantic.registry.type_resolver import resolve_annotated_type, validate_known_types
from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic

class StatementsAnalyzer:
    def __init__(self, v):
        self.v = v

    def visitExpressionStatement(self, ctx):
        return self.v.visit(ctx.expression())

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
                # línea/col seguras si el nodo tiene 'start'
                try:
                    line = st.start.line
                    col = st.start.column
                except Exception:
                    line = None
                    col = None
                self.v._append_err(SemanticError(
                    f"Código inalcanzable: el flujo terminó por '{terminator_reason}' antes de esta sentencia.",
                    line=line, column=col, error_type="DeadCode"))
                # Aún así, visitamos para seguir chequeando tipos/errores
                self.v.visit(st)
                continue

            # Reiniciar el flag que marcan las sentencias terminantes
            self.v._stmt_just_terminated = None
            self.v._stmt_just_terminator_node = None

            # Visitar sentencia normalmente
            result = self.v.visit(st)

            # ¿La sentencia que acabamos de visitar terminó el flujo?
            if self.v._stmt_just_terminated:
                terminated_in_block = True
                terminator_reason = self.v._stmt_just_terminated

        size = self.v.scopeManager.exitScope()
        log_semantic(f"[scope] bloque cerrado; frame_size={size} bytes")

        # Devolvemos un pequeño resultado para que estructuras como if/else
        return {
            "terminated": terminated_in_block,
            "reason": terminator_reason
        }

    def visitVariableDeclaration(self, ctx):
        name = ctx.Identifier().getText()
        ann = ctx.typeAnnotation()
        init = ctx.initializer()

        if ann is None:
            self.v._append_err(SemanticError(
                f"La variable '{name}' debe declarar un tipo (no se permite inferencia).",
                line=ctx.start.line, column=ctx.start.column))
            return

        declared_type = resolve_annotated_type(ann)
        if not validate_known_types(declared_type, self.v.known_classes, ctx, f"variable '{name}'", self.v.errors):
            return

        if isinstance(declared_type, VoidType):
            self.v._append_err(SemanticError(
                f"La variable '{name}' no puede ser de tipo void.",
                line=ctx.start.line, column=ctx.start.column))
            return

        initialized = False
        init_value_type = None
        init_note = None

        if not init:
            if isReferenceType(declared_type):
                initialized = True
                init_value_type = NullType()
                init_note = "default-null"
            else:
                # ❗ Reporta el error de falta de inicialización...
                self.v._append_err(SemanticError(
                    f"La variable '{name}' de tipo {declared_type} debe inicializarse; "
                    "null solo es asignable a tipos de referencia.",
                    line=ctx.start.line, column=ctx.start.column))

                # ...pero si estamos en un contexto de clase, igual registra el atributo
                if self.v.class_stack:
                    current_class = self.v.class_stack[-1]
                    self.v.class_handler.add_attribute(current_class, name, declared_type)
                    log_semantic(f"[class.attr] {current_class}.{name}: {declared_type} (registrado pese a init faltante)")
                return
        else:
            rhs_type = self.v.visit(init.expression())
            if rhs_type is None:
                return
            if not isAssignable(declared_type, rhs_type):
                self.v._append_err(SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_type} a {declared_type} en '{name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                if self.v.class_stack:
                    current_class = self.v.class_stack[-1]
                    self.v.class_handler.add_attribute(current_class, name, declared_type)
                    log_semantic(f"[class.attr] {current_class}.{name}: {declared_type} (registrado pese a asignación incompatible)")
                return
            initialized = True
            init_value_type = rhs_type
            init_note = "explicit"

        # Declarar el símbolo (solo si no hubo error arriba)
        try:
            sym = self.v.scopeManager.addSymbol(
                name, declared_type, category=SymbolCategory.VARIABLE,
                initialized=initialized, init_value_type=init_value_type, init_note=init_note
            )
            msg = f"Variable '{name}' declarada con tipo: {declared_type}, tamaño: {sym.width} bytes"
            if initialized: msg += f" (init={sym.init_value_type}, note={sym.init_note})"
            log_semantic(msg)
        except Exception as e:
            self.v._append_err(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))
            return

        # Registrar atributo de clase en el caso normal
        if self.v.class_stack:
            current_class = self.v.class_stack[-1]
            self.v.class_handler.add_attribute(current_class, name, declared_type)
            log_semantic(f"[class.attr] {current_class}.{name}: {declared_type}")

    def visitConstantDeclaration(self, ctx):
        name = ctx.Identifier().getText() if ctx.Identifier() else "<unnamed-const>"
        ann = ctx.typeAnnotation()
        expr_ctx = ctx.expression()

        if ann is None:
            self.v._append_err(SemanticError(
                f"La constante '{name}' debe declarar un tipo.",
                line=ctx.start.line, column=ctx.start.column))
            return

        declared_type = resolve_annotated_type(ann)
        if not validate_known_types(declared_type, self.v.known_classes, ctx, f"constante '{name}'", self.v.errors):
            return

        if isinstance(declared_type, VoidType):
            self.v._append_err(SemanticError(
                f"La constante '{name}' no puede ser de tipo void.",
                line=ctx.start.line, column=ctx.start.column))
            return

        if expr_ctx is None:
            self.v._append_err(SemanticError(
                f"Constante '{name}' sin inicializar (se requiere '= <expresión>').",
                line=ctx.start.line, column=ctx.start.column))
            return

        rhs_type = self.v.visit(expr_ctx)
        if rhs_type is None:
            return

        if not isAssignable(declared_type, rhs_type):
            self.v._append_err(SemanticError(
                f"Asignación incompatible: no se puede asignar {rhs_type} a {declared_type} en constante '{name}'.",
                line=ctx.start.line, column=ctx.start.column))
            return

        try:
            sym = self.v.scopeManager.addSymbol(name, declared_type, category=SymbolCategory.CONSTANT)
            log_semantic(f"Constante '{name}' declarada con tipo: {declared_type}, tamaño: {sym.width} bytes")
        except Exception as e:
            self.v._append_err(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))

    def visitAssignment(self, ctx):
        """
        Soporta:
        1) Identifier '=' expression ';'
        2) expression '.' Identifier '=' expression ';'   (asignación a propiedad)
        """
        exprs = list(ctx.expression())
        n = len(exprs)

        # ---- Caso 1: asignación a variable simple ----
        if n == 1 and ctx.Identifier() is not None:
            name = ctx.Identifier().getText()
            sym = self.v.scopeManager.lookup(name)
            if sym is None:
                self.v._append_err(SemanticError(
                    f"Uso de variable no declarada: '{name}'",
                    line=ctx.start.line, column=ctx.start.column))
                return
            if sym.category == SymbolCategory.CONSTANT:
                self.v._append_err(SemanticError(
                    f"No se puede modificar la constante '{name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                return

            rhs_type = self.v.visit(exprs[0])
            if rhs_type is None:
                return
            if not isAssignable(sym.type, rhs_type):
                self.v._append_err(SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_type} a {sym.type} en '{name}'.",
                    line=ctx.start.line, column=ctx.start.column))
            return

        # ---- Caso 2: asignación a propiedad obj.prop = expr ----
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
                self.v._append_err(SemanticError(
                    f"Asig. a propiedad en no-objeto: '{obj_t}'.",
                    line=ctx.start.line, column=ctx.start.column))
                return

            class_name = obj_t.name

            # Buscar tipo de propiedad (con herencia)
            prop_t = self.v.class_handler.get_attribute_type(class_name, prop_name)
            if prop_t is None:
                self.v._append_err(SemanticError(
                    f"Miembro '{prop_name}' no declarado en clase '{class_name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                return

            rhs_t = self.v.visit(rhs_exp)
            if not isAssignable(prop_t, rhs_t):
                self.v._append_err(SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_t} a {prop_t} en '{class_name}.{prop_name}'.",
                    line=ctx.start.line, column=ctx.start.column))
            return

        # ---- Fallback ----
        self.v._append_err(SemanticError(
            "Asignación a propiedad (obj.prop = ...) aún no soportada en esta fase.",
            line=ctx.start.line, column=ctx.start.column))

    def visitForeachStatement(self, ctx):
        iter_name = ctx.Identifier().getText()
        iter_expr_type = self.v.visit(ctx.expression())

        if isinstance(iter_expr_type, ArrayType):
            elem_type = iter_expr_type.elem_type
        else:
            if not isinstance(iter_expr_type, ErrorType):
                self.v._append_err(SemanticError(
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
            self.v._append_err(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))

        # El cuerpo es un bloque: su terminación no implica que el foreach sentencie
        # al bloque externo (porque el foreach por sí mismo no 'termina' el flujo).
        self.v.visit(ctx.block())
        size = self.v.scopeManager.exitScope()
        log_semantic(f"[scope] foreach cerrado; frame_size={size} bytes")
        return {"terminated": False, "reason": None}
