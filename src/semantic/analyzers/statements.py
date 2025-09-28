from semantic.symbol_kinds import SymbolCategory
from semantic.custom_types import NullType, ErrorType, ArrayType, IntegerType, VoidType, ClassType
from semantic.type_system import isAssignable, isReferenceType
from semantic.registry.type_resolver import resolve_annotated_type, validate_known_types
from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic
from ir.tac import Op


class StatementsAnalyzer:
    """
    Sentencias (declaraciones, asignaciones, bloques, foreach) con:
      - Chequeo semántico completo (como en la versión previa).
      - Emisión TAC donde corresponde (inicializadores y asignaciones).
      - Detección de 'código muerto' coherente con control de flujo.
      - Limpieza de temporales por sentencia.
    """

    def __init__(self, v):
        self.v = v

    # ------------------------------------------------------------------
    # Sentencia de expresión
    # ------------------------------------------------------------------
    def visitExpressionStatement(self, ctx):
        t = self.v.visit(ctx.expression())
        # liberar temporales creados en esta sentencia
        self.v.emitter.temp_pool.resetPerStatement()
        return t

    # ------------------------------------------------------------------
    # Bloques (con detección de código muerto)
    # ------------------------------------------------------------------
    def visitBlock(self, ctx):
        """
        Si una sentencia termina el flujo (return/break/continue o if-else donde
        ambas ramas terminan), el resto del bloque es inalcanzable (se reporta).
        """
        is_fn_body = (getattr(self.v, "_fn_body_block_ctx", None) is ctx)
        if not is_fn_body:
            self.v.scopeManager.enterScope()

        terminated_in_block = False
        terminator_reason = None

        for st in ctx.statement():
            if terminated_in_block:
                # Reportar dead code pero seguir visitando para recolectar errores
                try:
                    line = st.start.line
                    col = st.start.column
                except Exception:
                    line = None
                    col = None
                self.v.appendErr(SemanticError(
                    f"Código inalcanzable: el flujo terminó por '{terminator_reason}' antes de esta sentencia.",
                    line=line, column=col, error_type="DeadCode"))

                # activar barrera de emisión en este tramo muerto ===
                self.v.emitter.markFlowTerminated()

                self.v.visit(st)
                continue

            # Reset de flags de terminación por sentencia
            self.v.stmt_just_terminated = None
            self.v.stmt_just_terminator_node = None

            # Visitar sentencia
            self.v.visit(st)

            # ¿Terminó el flujo?
            if self.v.stmt_just_terminated:
                terminated_in_block = True
                terminator_reason = self.v.stmt_just_terminated

        if not is_fn_body:
            size = self.v.scopeManager.exitScope()
            log_semantic(f"[scope] bloque cerrado; frame_size={size} bytes")

        return {"terminated": terminated_in_block, "reason": terminator_reason}

    # ------------------------------------------------------------------
    # Declaraciones: let / const (con emisión TAC para inicializadores)
    # ------------------------------------------------------------------
    def visitVariableDeclaration(self, ctx):
        """
        let <id>: <type> [= expr]? ;
        - Reglas semánticas (tipos, asignabilidad, init opcional).
        - Atributo de clase si estamos dentro de class.
        - TAC: si hay init ->  id = <expr.place>
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

        # Sin inicializador
        if not init:
            if isReferenceType(declared_type):
                initialized = True
                init_value_type = NullType()
                init_note = "default-null"
            else:
                initialized = False
                init_value_type = None
                init_note = "uninitialized"
        else:
            # Con inicializador
            rhs_type = self.v.visit(init.expression())
            if isinstance(rhs_type, ErrorType):
                if self.v.class_stack:
                    current_class = self.v.class_stack[-1]
                    log_semantic(f"[class.attr] {current_class}.{name}: {declared_type}")
                    try:
                        self.v.scopeManager.addSymbol(
                            name, declared_type, category=SymbolCategory.VARIABLE,
                            initialized=False, init_value_type=None, init_note="init-error"
                        )
                    except Exception:
                        pass
                    self.v.class_handler.add_attribute(current_class, name, declared_type)
                else:
                    try:
                        self.v.scopeManager.addSymbol(
                            name, declared_type, category=SymbolCategory.VARIABLE,
                            initialized=False, init_value_type=None, init_note="init-error"
                        )
                    except Exception:
                        pass
                self.v.emitter.temp_pool.resetPerStatement()
                return

            
            if rhs_type is None:
                self.v.emitter.temp_pool.resetPerStatement()
                return
           
            if not isAssignable(declared_type, rhs_type):
                self.v.appendErr(SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_type} a {declared_type} en '{name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                if self.v.class_stack:
                    current_class = self.v.class_stack[-1]
                    # 1) registrar el símbolo (no inicializado) en el scope de la clase
                    try:
                        self.v.scopeManager.addSymbol(
                            name, declared_type, category=SymbolCategory.VARIABLE,
                            initialized=False, init_value_type=None, init_note="init-error"
                        )
                    except Exception:
                        pass
                    # 2) registrar el atributo en class_handler para offsets
                    self.v.class_handler.add_attribute(current_class, name, declared_type)
                self.v.emitter.temp_pool.resetPerStatement()
                return

            initialized = True
            init_value_type = rhs_type
            init_note = "explicit"

        # Declarar símbolo
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

        # Registrar atributo de clase (si procede)
        if self.v.class_stack:
            current_class = self.v.class_stack[-1]
            self.v.class_handler.add_attribute(current_class, name, declared_type)
            log_semantic(f"[class.attr] {current_class}.{name}: {declared_type}")

        # TAC del inicializador
        if init is not None:
            p, _ = self.v.exprs.deepPlace(init.expression())
            rhs_place = p or init.expression().getText()
            self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=name)

        # Limpiar temporales por sentencia
        self.v.emitter.temp_pool.resetPerStatement()

    def visitConstantDeclaration(self, ctx):
        """
        const <id>: <type> = expr ;
        - Tipo obligatorio + expr obligatoria + asignabilidad.
        - TAC: id = <expr.place>
        """
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
        if isinstance(rhs_type, ErrorType):
            try:
                self.v.scopeManager.addSymbol(name, declared_type, category=SymbolCategory.CONSTANT)
            except Exception:
                pass
            if self.v.class_stack:
                current_class = self.v.class_stack[-1]
                self.v.class_handler.add_attribute(current_class, name, declared_type)
            self.v.emitter.temp_pool.resetPerStatement()
            return


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
        
        if self.v.class_stack:
            current_class = self.v.class_stack[-1]
            self.v.class_handler.add_attribute(current_class, name, declared_type)
            log_semantic(f"[class.attr] {current_class}.{name}: {declared_type}")

        # TAC
        p, _ = self.v.exprs.deepPlace(expr_ctx)
        rhs_place = p or expr_ctx.getText()
        self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=name)

        self.v.emitter.temp_pool.resetPerStatement()

    # ------------------------------------------------------------------
    # Asignaciones: var = expr  |  obj.prop = expr
    # ------------------------------------------------------------------
    def visitAssignment(self, ctx):
        """
        Soporta:
          1) Identifier '=' expression ';'
          2) expression '.' Identifier '=' expression ';'   (asignación a propiedad)
        """
        exprs = list(ctx.expression())
        n = len(exprs)

        # (1) variable simple
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
            if isinstance(rhs_type, ErrorType):
                self.v.emitter.temp_pool.resetPerStatement()
                return

            if rhs_type is None:
                self.v.emitter.temp_pool.resetPerStatement()
                return
            if not isAssignable(sym.type, rhs_type):
                self.v.appendErr(SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_type} a {sym.type} en '{name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                self.v.emitter.temp_pool.resetPerStatement()
                return

            # TAC
            p, _ = self.v.exprs.deepPlace(exprs[0])
            rhs_place = p or exprs[0].getText()
            self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=name)
            self.v.emitter.temp_pool.resetPerStatement()
            return

        # (2) propiedad: obj.prop = expr
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
            if isinstance(rhs_t, ErrorType) or rhs_t is None:
                self.v.emitter.temp_pool.resetPerStatement()
                return

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
            q = self.v.emitter.emit(Op.FIELD_STORE, arg1=obj_place, res=rhs_place, label=prop_name)
            # hook opcional de offset (no afecta al TAC textual)
            try:
                off = self.v.class_handler.get_field_offset(class_name, prop_name)
                if q is not None and off is not None:
                    setattr(q, "_field_offset", off)       # metadata para CG
                    setattr(q, "_field_owner", class_name) # opcional
            except Exception:
                pass

            self.v.emitter.temp_pool.resetPerStatement()
            return


        # Fallback
        self.v.appendErr(SemanticError(
            "Asignación aún no soportada en esta forma por la fase actual.",
            line=ctx.start.line, column=ctx.start.column))
        self.v.emitter.temp_pool.resetPerStatement()

    # ------------------------------------------------------------------
    # foreach (semántica + scope)
    # ------------------------------------------------------------------
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

        # El cuerpo es un bloque; su terminación no implica que el foreach
        # termine el flujo en el bloque externo.
        self.v.visit(ctx.block())
        size = self.v.scopeManager.exitScope()
        log_semantic(f"[scope] foreach cerrado; frame_size={size} bytes")

        self.v.emitter.temp_pool.resetPerStatement()
        return {"terminated": False, "reason": None}
