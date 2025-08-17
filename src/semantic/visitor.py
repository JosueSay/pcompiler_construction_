from antlr_gen.CompiscriptVisitor import CompiscriptVisitor
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.validators.literal import validateLiteral
from semantic.symbol_kinds import SymbolCategory
from semantic.scope_manager import ScopeManager
from semantic.errors import SemanticError
from semantic.type_system import (
    isAssignable,
    resolveAnnotatedType,
    isReferenceType,
    resultArithmetic,
    resultModulo,
    resultRelational,
    resultEquality,
    resultLogical,
    resultUnaryMinus,
    resultUnaryNot,
)
from logs.logger_semantic import log_semantic
from semantic.custom_types import NullType, ErrorType, ClassType, ArrayType, IntegerType, BoolType, StringType, FloatType
class VisitorCPS(CompiscriptVisitor):
    """
    Visitor semántico principal. Recorre el AST y valida:
      - Declaraciones (variables y constantes)
      - Uso de identificadores
      - Asignaciones (como statement y como expresión)
      - Tipos de literales
    Integra ScopeManager para manejo de ámbitos y tabla de símbolos.
    """

    def __init__(self):
        self.errors = []
        self.scopeManager = ScopeManager()
        self.known_classes = set()
        self.class_stack = []
        self.in_method = False
        log_semantic("", new_session=True)

    # -------------------------
    # Entrada del programa
    # -------------------------
    def visitProgram(self, ctx: CompiscriptParser.ProgramContext):
        # 1) Pre-scan: recolectar clases (para permitir referencias adelantadas)
        for st in ctx.statement():
            cd = st.classDeclaration() if hasattr(st, "classDeclaration") else None
            if cd:
                name = cd.Identifier(0).getText()
                if name in self.known_classes:
                    err = SemanticError(
                        f"Clase '{name}' ya declarada.",
                        line=cd.start.line, column=cd.start.column
                    )
                    self.errors.append(err)
                    log_semantic(f"ERROR: {err}")
                else:
                    self.known_classes.add(name)
                    log_semantic(f"[class] (pre-scan) declarada: {name}")

        # 2) Visita normal de statements (tipos anotados ya pueden validarse)
        for stmt in ctx.statement():
            self.visit(stmt)

        if self.errors:
            log_semantic("Semantic Errors:")
            for error in self.errors:
                log_semantic(f" - {error}")
        else:
            log_semantic("Type checking passed.")

        log_semantic("Símbolos declarados:")
        for sym in self.scopeManager.allSymbols():
            init_info = (
                f", initialized={sym.initialized}"
                + (f", init_value_type={sym.init_value_type}" if sym.init_value_type else "")
                + (f", init_note={sym.init_note}" if sym.init_note else "")
            )
            storage_info = f", storage={sym.storage}, is_ref={sym.is_ref}"
            log_semantic(
                f" - {sym.name}: {sym.type} ({sym.category}), "
                f"tamaño={sym.width}, offset={sym.offset}{storage_info}{init_info}"
            )

    # -------------------------
    # Statements
    # -------------------------
    def visitExpressionStatement(self, ctx: CompiscriptParser.ExpressionStatementContext):
        """
        Fuerza la evaluación/validación de una expresión usada como statement.
        Ej: x = 3; o 42;
        """
        return self.visit(ctx.expression())

    def visitVariableDeclaration(self, ctx: CompiscriptParser.VariableDeclarationContext):
        """
        Reglas:
        - La variable debe declarar tipo (no se permite inferencia).
        - Si NO hay inicializador:
            * Si el tipo declarado es de referencia => se asume 'null' y se acepta.
            * Si NO es de referencia => error (null no asignable).
        - Si hay inicializador:
            * El tipo del valor (RHS) debe ser asignable al tipo declarado.
        """
        name = ctx.Identifier().getText()
        ann = ctx.typeAnnotation()
        init = ctx.initializer()

        # 1) Tipo obligatorio (no hay inferencia)
        if ann is None:
            err = SemanticError(
                f"La variable '{name}' debe declarar un tipo (no se permite inferencia).",
                line=ctx.start.line,
                column=ctx.start.column
            )
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")
            return

        declared_type = resolveAnnotatedType(ann)
        self._validate_known_types(declared_type, ctx, f"variable '{name}'")

        if declared_type is None:
            err = SemanticError(
                f"Tipo anotado inválido o no soportado en la variable '{name}'.",
                line=ctx.start.line,
                column=ctx.start.column
            )
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")
            return
        
        initialized = False
        init_value_type = None
        init_note = None

        # 2) Si NO hay inicializador
        if not init:
            if isReferenceType(declared_type):
                initialized = True
                init_value_type = NullType()
                init_note = "default-null"
            else:
                err = SemanticError(
                    f"La variable '{name}' de tipo {declared_type} debe inicializarse; "
                    "null solo es asignable a tipos de referencia.",
                    line=ctx.start.line, column=ctx.start.column
                )
                self.errors.append(err)
                log_semantic(f"ERROR: {err}")
                return
        else:
            # 3) Si hay inicializador, evaluamos y validamos
            rhs_type = self.visit(init.expression())
            if rhs_type is None:
                # El RHS ya produjo error, no seguimos
                return
            if not isAssignable(declared_type, rhs_type):
                err = SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_type} a {declared_type} en '{name}'.",
                    line=ctx.start.line,
                    column=ctx.start.column
                )
                self.errors.append(err)
                log_semantic(f"ERROR: {err}")
                return
            initialized = True
            init_value_type = rhs_type
            init_note = "explicit"

        # 4) Registrar símbolo en el alcance actual
        try:
            sym = self.scopeManager.addSymbol(
                name,
                declared_type,
                category=SymbolCategory.VARIABLE,
                initialized=initialized,
                init_value_type=init_value_type,
                init_note=init_note
            )
            msg = (
                f"Variable '{name}' declarada con tipo: {declared_type}, tamaño: {sym.width} bytes"
                + (f" (init={sym.init_value_type}, note={sym.init_note})" if initialized else "")
            )
            log_semantic(msg)
        except Exception as e:
            err = SemanticError(str(e), line=ctx.start.line, column=ctx.start.column)
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")


    def visitConstantDeclaration(self, ctx: CompiscriptParser.ConstantDeclarationContext):
        """
        Reglas:
        - Constantes SIEMPRE se inicializan.
        - Se exige tipo declarado (sin inferencia).
        - El valor debe ser asignable al tipo declarado.
        """
        name = ctx.Identifier().getText() if ctx.Identifier() else "<unnamed-const>"
        ann = ctx.typeAnnotation()
        expr_ctx = ctx.expression()  # Puede venir None si hubo error sintáctico

        # Tipo obligatorio para const (alineado con no-inferencia)
        if ann is None:
            err = SemanticError(
                f"La constante '{name}' debe declarar un tipo.",
                line=ctx.start.line,
                column=ctx.start.column
            )
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")
            return

        declared_type = resolveAnnotatedType(ann)
        self._validate_known_types(declared_type, ctx, f"constante '{name}'")
        
        if declared_type is None:
            err = SemanticError(
                f"Tipo anotado inválido o no soportado en la constante '{name}'.",
                line=ctx.start.line,
                column=ctx.start.column
            )
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")
            return

        # Si por error de sintaxis no hay '=' o no hay expresión, expr_ctx será None.
        if expr_ctx is None:
            err = SemanticError(
                f"Constante '{name}' sin inicializar (se requiere '= <expresión>').",
                line=ctx.start.line,
                column=ctx.start.column
            )
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")
            # Aún así intentamos registrar la constante para no encadenar más errores por 'no declarada'.
            try:
                self.scopeManager.addSymbol(name, declared_type, category=SymbolCategory.CONSTANT)
                log_semantic(f"Constante '{name}' declarada (con error de inicialización).")
            except Exception as e:
                # Si también hay redeclaración, lo anotamos pero seguimos.
                e2 = SemanticError(str(e), line=ctx.start.line, column=ctx.start.column)
                self.errors.append(e2)
                log_semantic(f"ERROR: {e2}")
            return

        # Camino normal: hay expresión; validamos asignabilidad
        rhs_type = self.visit(expr_ctx)
        if rhs_type is None:
            # La visita del RHS ya generó error(es); no duplicamos.
            return

        if not isAssignable(declared_type, rhs_type):
            err = SemanticError(
                f"Asignación incompatible: no se puede asignar {rhs_type} a {declared_type} en constante '{name}'.",
                line=ctx.start.line,
                column=ctx.start.column
            )
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")
            # Registramos la constante igual (con error) para evitar cascada de 'no declarada'
            try:
                self.scopeManager.addSymbol(name, declared_type, category=SymbolCategory.CONSTANT)
                log_semantic(f"Constante '{name}' declarada (con error de tipo en inicialización).")
            except Exception as e:
                e2 = SemanticError(str(e), line=ctx.start.line, column=ctx.start.column)
                self.errors.append(e2)
                log_semantic(f"ERROR: {e2}")
            return

        # Registrar símbolo cuando todo está correcto
        try:
            sym = self.scopeManager.addSymbol(name, declared_type, category=SymbolCategory.CONSTANT)
            log_semantic(f"Constante '{name}' declarada con tipo: {declared_type}, tamaño: {sym.width} bytes")
        except Exception as e:
            err = SemanticError(str(e), line=ctx.start.line, column=ctx.start.column)
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")


    def visitAssignment(self, ctx: CompiscriptParser.AssignmentContext):
        """
        statement -> assignment ';'
        Reglas:
          - LHS debe existir.
          - No se permite modificar constantes.
          - Tipos deben ser asignables.
          - Soporte actual: asignación simple a identificador.
            Asignación a propiedad (expr '.' id) se marca como no soportada aún.
        """
        # Alternativa 1: Identifier '=' expression ';'
        if ctx.Identifier() is not None:
            name = ctx.Identifier().getText()
            sym = self.scopeManager.lookup(name)
            if sym is None:
                err = SemanticError(
                    f"Uso de variable no declarada: '{name}'",
                    line=ctx.start.line,
                    column=ctx.start.column
                )
                self.errors.append(err)
                log_semantic(f"ERROR: {err}")
                return

            if sym.category == SymbolCategory.CONSTANT:
                err = SemanticError(
                    f"No se puede modificar la constante '{name}'.",
                    line=ctx.start.line,
                    column=ctx.start.column
                )
                self.errors.append(err)
                log_semantic(f"ERROR: {err}")
                return

            rhs_type = self.visit(ctx.expression())
            if rhs_type is None:
                return

            if not isAssignable(sym.type, rhs_type):
                err = SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_type} a {sym.type} en '{name}'.",
                    line=ctx.start.line,
                    column=ctx.start.column
                )
                self.errors.append(err)
                log_semantic(f"ERROR: {err}")
            return

        # Alternativa 2: expression '.' Identifier '=' expression ';' (no soportada aún)
        err = SemanticError(
            "Asignación a propiedad (obj.prop = ...) aún no soportada en esta fase.",
            line=ctx.start.line,
            column=ctx.start.column
        )
        self.errors.append(err)
        log_semantic(f"ERROR: {err}")

    def visitBlock(self, ctx: CompiscriptParser.BlockContext):
        self.scopeManager.enterScope()
        for st in ctx.statement():
            self.visit(st)
        size = self.scopeManager.exitScope()
        log_semantic(f"[scope] bloque cerrado; frame_size={size} bytes")
        return None

    def visitFunctionDeclaration(self, ctx: CompiscriptParser.FunctionDeclarationContext):
        """
        functionDeclaration: 'function' Identifier '(' parameters? ')' (':' type)? block;
        - Declara símbolo de función en el scope actual.
        - Abre un nuevo scope para los parámetros y el cuerpo.
        - Registra parámetros como símbolos category=PARAMETER.
        """
        name = ctx.Identifier().getText()

        # 1) Tipos de parámetros
        param_types = []
        param_names = []
        if ctx.parameters():
            for p in ctx.parameters().parameter():
                pname = p.Identifier().getText()
                tctx = p.type_()  # puede ser None en la gramática, pero aquí exigimos tipo
                if tctx is None:
                    err = SemanticError(
                        f"Parámetro '{pname}' debe declarar tipo.",
                        line=p.start.line, column=p.start.column
                    )
                    self.errors.append(err)
                    log_semantic(f"ERROR: {err}")
                    # Seguimos, pero con ErrorType para evitar cascada
                    ptype = ErrorType()
                else:
                    ptype = self._resolve_type_from_typectx(tctx)
                    self._validate_known_types(ptype, p, f"parámetro '{pname}'")
                param_names.append(pname)
                param_types.append(ptype)

        # 2) Tipo de retorno (opcional por ahora)
        rtype = None
        if ctx.type_():
            rtype = self._resolve_type_from_typectx(ctx.type_())
            self._validate_known_types(rtype, ctx, f"retorno de función '{name}'")

        # 3) Declarar símbolo de función en el scope actual (evita duplicados en el mismo scope)
        
        try:
            fsym = self.scopeManager.addSymbol(
                name,
                rtype if rtype is not None else NullType(),
                category=SymbolCategory.FUNCTION,
                initialized=True,
                init_value_type=None,
                init_note="decl"
            )
            # Guardar metadatos de firma en el símbolo
            fsym.param_types = param_types
            fsym.return_type = rtype
            log_semantic(f"[function] declarada: {name}({', '.join(param_names)}) -> {rtype if rtype else 'void?'}")
        except Exception as e:
            err = SemanticError(str(e), line=ctx.start.line, column=ctx.start.column)
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")
            # Si no se pudo declarar la función, igual visitamos el bloque para continuar análisis
            # pero sin abrir un scope de params vinculado (evitamos más ruido).
            return self.visit(ctx.block())

        # 4) Abrir scope de función y registrar parámetros
        self.scopeManager.enterScope()
        for pname, ptype in zip(param_names, param_types):
            try:
                psym = self.scopeManager.addSymbol(
                    pname,
                    ptype,
                    category=SymbolCategory.PARAMETER,
                    initialized=True,
                    init_value_type=None,
                    init_note="param"
                )
                log_semantic(f"[param] {pname}: {ptype}, offset={psym.offset}")
            except Exception as e:
                e2 = SemanticError(str(e), line=ctx.start.line, column=ctx.start.column)
                self.errors.append(e2)
                log_semantic(f"ERROR: {e2}")

        # 5) Visitar el cuerpo de la función dentro de su scope
        self.visit(ctx.block())
        size = self.scopeManager.exitScope()
        log_semantic(f"[scope] función '{name}' cerrada; frame_size={size} bytes")
        return None

    # -------------------------
    # Expresiones
    # -------------------------
    def visitLiteralExpr(self, ctx: CompiscriptParser.LiteralExprContext):
        """
        literalExpr
        : Literal
        | arrayLiteral
        | 'null'
        | 'true'
        | 'false'
        """
        # arreglos -> delegar a visitArrayLiteral
        if hasattr(ctx, "arrayLiteral") and ctx.arrayLiteral() is not None:
            return self.visit(ctx.arrayLiteral())

        # Para integer, string, true/false, null se usa validateLiteral
        value = ctx.getText()
        log_semantic(f"Literal detected: {value}")
        return validateLiteral(value, self.errors, ctx)

    def visitIdentifierExpr(self, ctx: CompiscriptParser.IdentifierExprContext):
        """
        Uso de identificador en expresión.
        """
        name = ctx.getText()
        log_semantic(f"Identifier used: {name}")
        sym = self.scopeManager.lookup(name)
        if sym is None:
            error = SemanticError(
                f"Identificador '{name}' no está declarado.",
                line=ctx.start.line,
                column=ctx.start.column
            )
            self.errors.append(error)
            log_semantic(f"ERROR: {error}")
            return None
        return sym.type

    def visitAssignExpr(self, ctx: CompiscriptParser.AssignExprContext):
        """
        assignmentExpr: lhs=leftHandSide '=' assignmentExpr
        Soporte actual: LHS debe ser un identificador simple.
        """
        # Resolver LHS: esperamos que leftHandSide comience con primaryAtom -> IdentifierExpr
        lhs = ctx.lhs
        # Caso simple: el texto del LHS es un identificador sin sufijos
        lhs_text = lhs.getText()
        sym = self.scopeManager.lookup(lhs_text)
        if sym is None:
            err = SemanticError(
                f"Uso de variable no declarada: '{lhs_text}'",
                line=ctx.start.line,
                column=ctx.start.column
            )
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")
            return None

        if sym.category == SymbolCategory.CONSTANT:
            err = SemanticError(
                f"No se puede modificar la constante '{lhs_text}'.",
                line=ctx.start.line,
                column=ctx.start.column
            )
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")
            return None

        rhs_type = self.visit(ctx.assignmentExpr())
        if rhs_type is None:
            return None

        if not isAssignable(sym.type, rhs_type):
            err = SemanticError(
                f"Asignación incompatible: no se puede asignar {rhs_type} a {sym.type} en '{lhs_text}'.",
                line=ctx.start.line,
                column=ctx.start.column
            )
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")
            return None

        # El valor de una asignación como expresión es el tipo del RHS (convención común)
        return rhs_type

    # Fallback por si ANTLR llama visit a otras alternativas sin método específico
    def visitExprNoAssign(self, ctx: CompiscriptParser.ExprNoAssignContext):
        return self.visitChildren(ctx)
    
    def visitArrayLiteral(self, ctx: CompiscriptParser.ArrayLiteralContext):
        """
        arrayLiteral: '[' (expression (',' expression)*)? ']'
        Regla: todos los elementos deben ser del mismo tipo (o error).
        Resultado: ArrayType(elem_type).
        """
        expr_ctxs = list(ctx.expression())
        if not expr_ctxs:
            err = SemanticError(
                "Arreglo vacío sin tipo explícito no soportado aún.",
                line=ctx.start.line, column=ctx.start.column
            )
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")
            return ErrorType()

        elem_types = [self.visit(e) for e in expr_ctxs]
        if any(t is None for t in elem_types):
            return ErrorType()

        first = elem_types[0]
        same = all(type(t) is type(first) for t in elem_types)
        if not same:
            err = SemanticError(
                f"Elementos de arreglo con tipos inconsistentes: {[str(t) for t in elem_types]}",
                line=ctx.start.line, column=ctx.start.column
            )
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")
            return ErrorType()

        return ArrayType(first)

    def visitThisExpr(self, ctx: CompiscriptParser.ThisExprContext):
        """
        'this' solo válido dentro de métodos; retorna ClassType(clase actual).
        """
        from semantic.custom_types import ClassType, ErrorType
        if not self.in_method or not self.class_stack:
            err = SemanticError(
                "'this' solo puede usarse dentro de métodos de clase.",
                line=ctx.start.line, column=ctx.start.column
            )
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")
            return ErrorType()
        return ClassType(self.class_stack[-1])

    # ------------------------------------------------
    # Expresiones compuestas (operadores binarios/unarios)
    # ------------------------------------------------

    def visitAdditiveExpr(self, ctx: CompiscriptParser.AdditiveExprContext):
        """
        additiveExpr
        : multiplicativeExpr (('+' | '-') multiplicativeExpr)*
        """
        children = list(ctx.getChildren())
        if not children:
            return None
        t = self.visit(children[0])  # primer operando
        i = 1
        while i < len(children):
            op = children[i].getText()         # '+' o '-'
            rhs = self.visit(children[i+1])    # siguiente operando

            # Pasamos el operador a resultArithmetic para soportar
            # tanto aritmética como concatenación string + string
            res = resultArithmetic(t, rhs, op)

            if isinstance(res, ErrorType):
                err = SemanticError(
                    f"Operación aritmética inválida: {t} {op} {rhs}",
                    line=ctx.start.line,
                    column=ctx.start.column
                )
                self.errors.append(err)
                log_semantic(f"ERROR: {err}")
                t = ErrorType()
            else:
                t = res
            i += 2
        return t


    def visitMultiplicativeExpr(self, ctx: CompiscriptParser.MultiplicativeExprContext):
        """
        multiplicativeExpr
        : unaryExpr (('*' | '/' | '%') unaryExpr)*
        """
        children = list(ctx.getChildren())
        if not children:
            return None
        t = self.visit(children[0])
        i = 1
        while i < len(children):
            op = children[i].getText()       # '*', '/', o '%'
            rhs = self.visit(children[i+1])

            if op == '%':
                res = resultModulo(t, rhs)
            else:
                # pasar el operador a resultArithmetic
                res = resultArithmetic(t, rhs, op)

            if isinstance(res, ErrorType):
                err = SemanticError(
                    f"Operación multiplicativa inválida: {t} {op} {rhs}",
                    line=ctx.start.line, column=ctx.start.column
                )
                self.errors.append(err)
                log_semantic(f"ERROR: {err}")
                t = ErrorType()
            else:
                t = res
            i += 2
        return t


    def visitRelationalExpr(self, ctx: CompiscriptParser.RelationalExprContext):
        """
        relationalExpr
          : additiveExpr (('<' | '<=' | '>' | '>=') additiveExpr)*
        """
        children = list(ctx.getChildren())
        if not children:
            return None
        # Estructura encadenada, el resultado siempre es boolean si las comparaciones son válidas.
        # Evaluamos por pares; si alguna da error, propagamos ErrorType.
        left_type = self.visit(children[0])
        i = 1
        final_type = None
        while i < len(children):
            op = children[i].getText()
            right_type = self.visit(children[i+1])
            res = resultRelational(left_type, right_type)
            if isinstance(res, ErrorType):
                err = SemanticError(
                    f"Comparación no válida: {left_type} {op} {right_type}",
                    line=ctx.start.line, column=ctx.start.column
                )
                self.errors.append(err)
                log_semantic(f"ERROR: {err}")
                final_type = ErrorType()
            else:
                final_type = res  # BoolType
            left_type = right_type
            i += 2
        # Si no hubo operadores, retorna el tipo del lado izquierdo (caso de un solo operando).
        return final_type if final_type is not None else left_type

    def visitEqualityExpr(self, ctx: CompiscriptParser.EqualityExprContext):
        """
        equalityExpr
          : relationalExpr (('==' | '!=') relationalExpr)*
        """
        children = list(ctx.getChildren())
        if not children:
            return None
        left_type = self.visit(children[0])
        i = 1
        final_type = None
        while i < len(children):
            op = children[i].getText()
            right_type = self.visit(children[i+1])
            res = resultEquality(left_type, right_type)
            if isinstance(res, ErrorType):
                err = SemanticError(
                    f"Igualdad no válida: {left_type} {op} {right_type}",
                    line=ctx.start.line, column=ctx.start.column
                )
                self.errors.append(err)
                log_semantic(f"ERROR: {err}")
                final_type = ErrorType()
            else:
                final_type = res  # BoolType
            left_type = right_type
            i += 2
        return final_type if final_type is not None else left_type

    def visitLogicalAndExpr(self, ctx: CompiscriptParser.LogicalAndExprContext):
        """
        logicalAndExpr
          : equalityExpr ('&&' equalityExpr)*
        """
        children = list(ctx.getChildren())
        if not children:
            return None
        t = self.visit(children[0])
        i = 1
        while i < len(children):
            op = children[i].getText()  # '&&'
            rhs = self.visit(children[i+1])
            res = resultLogical(t, rhs)
            if isinstance(res, ErrorType):
                err = SemanticError(
                    f"Operación lógica inválida: {t} {op} {rhs}",
                    line=ctx.start.line, column=ctx.start.column
                )
                self.errors.append(err)
                log_semantic(f"ERROR: {err}")
                t = ErrorType()
            else:
                t = res  # BoolType
            i += 2
        return t

    def visitLogicalOrExpr(self, ctx: CompiscriptParser.LogicalOrExprContext):
        """
        logicalOrExpr
          : logicalAndExpr ('||' logicalAndExpr)*
        """
        children = list(ctx.getChildren())
        if not children:
            return None
        t = self.visit(children[0])
        i = 1
        while i < len(children):
            op = children[i].getText()  # '||'
            rhs = self.visit(children[i+1])
            res = resultLogical(t, rhs)
            if isinstance(res, ErrorType):
                err = SemanticError(
                    f"Operación lógica inválida: {t} {op} {rhs}",
                    line=ctx.start.line, column=ctx.start.column
                )
                self.errors.append(err)
                log_semantic(f"ERROR: {err}")
                t = ErrorType()
            else:
                t = res
            i += 2
        return t

    def visitUnaryExpr(self, ctx: CompiscriptParser.UnaryExprContext):
        """
        unaryExpr
          : ('-' | '!') unaryExpr
          | primaryExpr
        """
        # Si tiene 2 hijos, es unario; si no, delega a primary
        if ctx.getChildCount() == 2:
            op = ctx.getChild(0).getText()
            inner = self.visit(ctx.unaryExpr())
            if op == '-':
                res = resultUnaryMinus(inner)
                if isinstance(res, ErrorType):
                    err = SemanticError(
                        f"Operador '-' inválido sobre tipo {inner}",
                        line=ctx.start.line, column=ctx.start.column
                    )
                    self.errors.append(err)
                    log_semantic(f"ERROR: {err}")
                return res
            elif op == '!':
                res = resultUnaryNot(inner)
                if isinstance(res, ErrorType):
                    err = SemanticError(
                        f"Operador '!' inválido sobre tipo {inner}",
                        line=ctx.start.line, column=ctx.start.column
                    )
                    self.errors.append(err)
                    log_semantic(f"ERROR: {err}")
                return res
            else:
                # operador desconocido (no debería suceder)
                return ErrorType()
        else:
            return self.visit(ctx.primaryExpr())

    def visitNewExpr(self, ctx: CompiscriptParser.NewExprContext):
        """
        'new' Identifier '(' arguments? ')'
        Retorna ClassType(Identifier). Valida que la clase exista.
        """
        class_name = ctx.Identifier().getText()
        if class_name not in self.known_classes:
            err = SemanticError(
                f"Clase '{class_name}' no declarada.",
                line=ctx.start.line, column=ctx.start.column
            )
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")
            # devolvemos el tipo igualmente para seguir el análisis de tipos
        return ClassType(class_name)


    def _validate_known_types(self, t, ctx, where:str):
        """
        Verifica que cualquier ClassType presente (directo o dentro de ArrayType)
        exista en self.known_classes. Si no existe, reporta error.
        """
        
        # desempacar arrays hasta el base
        base = t
        while isinstance(base, ArrayType):
            base = base.elem_type
        if isinstance(base, ClassType):
            if base.name not in self.known_classes:
                err = SemanticError(
                    f"Tipo de clase no declarado: '{base.name}' usado en {where}.",
                    line=ctx.start.line, column=ctx.start.column
                )
                self.errors.append(err)
                log_semantic(f"ERROR: {err}")

    def _resolve_type_from_typectx(self, type_ctx):
        """
        Resuelve un CompiscriptParser.TypeContext -> Type semántico.
        Soporta baseType + '[]'*  (p.ej., Animal[][]).
        """
        if type_ctx is None:
            return None

        base_txt = type_ctx.baseType().getText()
        # Import local para evitar ciclos

        if base_txt == "integer":
            t = IntegerType()
        elif base_txt == "string":
            t = StringType()
        elif base_txt == "boolean":
            t = BoolType()
        else:
            # Es un nombre de clase
            t = ClassType(base_txt)

        # Contar '[]' a partir de los hijos ('baseType', '[', ']', '[', ']', ...)
        dims = (type_ctx.getChildCount() - 1) // 2
        for _ in range(dims):
            t = ArrayType(t)
        return t

    def visitLeftHandSide(self, ctx: CompiscriptParser.LeftHandSideContext):
        """
        leftHandSide: primaryAtom (suffixOp)* ;
        Aplica en orden los sufijos sobre el tipo del primaryAtom.
        - Indexación: base debe ser ArrayType(T) e índice integer -> resultado T.
        - Acceso a propiedad: soporte básico cuando la base es ClassType de la clase actual
        (p. ej., `this.prop` dentro del método). Busca el miembro en el scope de clase.
        - Llamadas: aún no soportadas en esta fase.
        """

        # tipo del 'primario' (identificador, new, this, etc.)
        t = self.visit(ctx.primaryAtom())

        # aplicar todos los sufijos en orden
        for suf in ctx.suffixOp():
            # --------------------
            # IndexExpr: '[' expression ']'
            # --------------------
            if isinstance(suf, CompiscriptParser.IndexExprContext):
                # validar base arreglo
                if not isinstance(t, ArrayType):
                    err = SemanticError(
                        f"Indexación sobre un valor no-arreglo: {t}",
                        line=ctx.start.line, column=ctx.start.column
                    )
                    self.errors.append(err)
                    log_semantic(f"ERROR: {err}")
                    t = ErrorType()
                    continue

                idx_t = self.visit(suf.expression())
                if not isinstance(idx_t, IntegerType):
                    err = SemanticError(
                        f"Índice no entero en acceso de arreglo: se encontró {idx_t}",
                        line=ctx.start.line, column=ctx.start.column
                    )
                    self.errors.append(err)
                    log_semantic(f"ERROR: {err}")
                    t = ErrorType()
                    continue

                # tipo resultante es el tipo de elemento
                t = t.elem_type
                continue

            # --------------------
            # CallExpr: '(' args? ')'
            # --------------------
            if isinstance(suf, CompiscriptParser.CallExprContext):
                err = SemanticError(
                    "Llamadas a función/método aún no soportadas en esta fase.",
                    line=ctx.start.line, column=ctx.start.column
                )
                self.errors.append(err)
                log_semantic(f"ERROR: {err}")
                t = ErrorType()
                continue

            # --------------------
            # PropertyAccessExpr: '.' Identifier
            # --------------------
            if isinstance(suf, CompiscriptParser.PropertyAccessExprContext):
                prop_name = suf.Identifier().getText()

                # Soporte MVP: si la base es un objeto de la misma clase del método actual,
                # resolvemos el miembro buscándolo en el scope visible (clase abierta debajo del método).
                if isinstance(t, ClassType) and self.class_stack:
                    current_cls = self.class_stack[-1]
                    if t.name == current_cls:
                        sym = self.scopeManager.lookup(prop_name)
                        if sym is None:
                            err = SemanticError(
                                f"Miembro '{prop_name}' no declarado en clase '{current_cls}'.",
                                line=ctx.start.line, column=ctx.start.column
                            )
                            self.errors.append(err)
                            log_semantic(f"ERROR: {err}")
                            t = ErrorType()
                        else:
                            # El tipo del acceso a propiedad es el tipo del miembro
                            t = sym.type
                        continue

                # Cualquier otro caso todavía no soportado
                err = SemanticError(
                    "Acceso a propiedades (obj.prop) aún no soportado en esta fase.",
                    line=ctx.start.line, column=ctx.start.column
                )
                self.errors.append(err)
                log_semantic(f"ERROR: {err}")
                t = ErrorType()
                continue

        return t

    def visitClassDeclaration(self, ctx: CompiscriptParser.ClassDeclarationContext):
        """
        classDeclaration: 'class' Identifier (':' Identifier)? '{' classMember* '}'
        - Abre *scope de clase*.
        - Registra/visita miembros: campos (var/const) y métodos (function).
        - No resolvemos aún herencia (':' Identifier) ni acceso a propiedades.
        """
        name = ctx.Identifier(0).getText()
        log_semantic(f"[class] definición: {name}")

        # Abrir scope de clase
        self.class_stack.append(name)
        self.scopeManager.enterScope()

        # Visitar miembros
        for mem in ctx.classMember():
            if mem.functionDeclaration():
                self._visitMethodDeclaration(mem.functionDeclaration(), current_class=name)
            else:
                # variableDeclaration | constantDeclaration
                self.visit(mem)

        size = self.scopeManager.exitScope()
        self.class_stack.pop()
        log_semantic(f"[scope] clase '{name}' cerrada; frame_size={size} bytes")
        return None

    def _visitMethodDeclaration(self, ctx_fn: CompiscriptParser.FunctionDeclarationContext, *, current_class: str):
        """
        Declara un *método* dentro de una clase:
        - Mangle de nombre: ClassName.method
        - Inyecta parámetro implícito 'this: ClassType(ClassName)'
        - Abre scope propio para params + cuerpo
        """
        from semantic.custom_types import ClassType, ErrorType, NullType, ArrayType
        method_name = ctx_fn.Identifier().getText()
        qname = f"{current_class}.{method_name}"

        # 1) Param types (explícitos) + inyección de 'this'
        param_types = [ClassType(current_class)]
        param_names = ["this"]

        if ctx_fn.parameters():
            for p in ctx_fn.parameters().parameter():
                pname = p.Identifier().getText()
                tctx = p.type_()
                if tctx is None:
                    err = SemanticError(
                        f"Parámetro '{pname}' debe declarar tipo (en método {qname}).",
                        line=p.start.line, column=p.start.column
                    )
                    self.errors.append(err)
                    log_semantic(f"ERROR: {err}")
                    ptype = ErrorType()
                else:
                    ptype = self._resolve_type_from_typectx(tctx)
                    self._validate_known_types(ptype, p, f"parámetro '{pname}' de método {qname}")
                param_names.append(pname)
                param_types.append(ptype)

        # 2) Return type (opcional)
        rtype = None
        if ctx_fn.type_():
            rtype = self._resolve_type_from_typectx(ctx_fn.type_())
            self._validate_known_types(rtype, ctx_fn, f"retorno de método '{qname}'")

        # 3) Declarar símbolo de *método* (category=FUNCTION) en scope de clase
        try:
            fsym = self.scopeManager.addSymbol(
                qname,
                rtype if rtype is not None else NullType(),
                category=SymbolCategory.FUNCTION,
                initialized=True,
                init_value_type=None,
                init_note="decl"
            )
            fsym.param_types = param_types
            fsym.return_type = rtype
            log_semantic(f"[method] declarada: {qname}({', '.join(param_names)}) -> {rtype if rtype else 'void?'}")
        except Exception as e:
            err = SemanticError(str(e), line=ctx_fn.start.line, column=ctx_fn.start.column)
            self.errors.append(err)
            log_semantic(f"ERROR: {err}")
            # Igual visitar el cuerpo para continuar análisis
            return self.visit(ctx_fn.block())

        # 4) Abrir scope de método y registrar parámetros (incluye 'this')
        self.scopeManager.enterScope()
        self.in_method = True
        for pname, ptype in zip(param_names, param_types):
            try:
                psym = self.scopeManager.addSymbol(
                    pname,
                    ptype,
                    category=SymbolCategory.PARAMETER,
                    initialized=True,
                    init_value_type=None,
                    init_note="param"
                )
                log_semantic(f"[param] {pname}: {ptype}, offset={psym.offset}")
            except Exception as e:
                e2 = SemanticError(str(e), line=ctx_fn.start.line, column=ctx_fn.start.column)
                self.errors.append(e2)
                log_semantic(f"ERROR: {e2}")

        # 5) Cuerpo
        self.visit(ctx_fn.block())
        size = self.scopeManager.exitScope()
        self.in_method = False
        log_semantic(f"[scope] método '{qname}' cerrado; frame_size={size} bytes")
        return None


