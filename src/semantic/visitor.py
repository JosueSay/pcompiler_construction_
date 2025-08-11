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
)
from logs.logger_semantic import log_semantic
from semantic.custom_types import NullType


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
        log_semantic("", new_session=True)

    # -------------------------
    # Entrada del programa
    # -------------------------
    def visitProgram(self, ctx: CompiscriptParser.ProgramContext):
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
            log_semantic(
                f" - {sym.name}: {sym.type} ({sym.category}), "
                f"tamaño={sym.width}, offset={sym.offset}{init_info}"
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
        Nota: Si por error de sintaxis el '=' o la expresión faltan, ctx.expression() puede ser None.
            En ese caso reportamos error semántico y continuamos sin romper el análisis.
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
        statement → assignment ';'
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

    # -------------------------
    # Expresiones
    # -------------------------
    def visitLiteralExpr(self, ctx: CompiscriptParser.LiteralExprContext):
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
