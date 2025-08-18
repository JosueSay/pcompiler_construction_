from antlr_gen.CompiscriptVisitor import CompiscriptVisitor
from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger_semantic import log_semantic

from semantic.scope_manager import ScopeManager
from semantic.diagnostics import Diagnostics
from semantic.registry.method_registry import MethodRegistry

# Analyzers
from semantic.analyzers.lvalues import LValuesAnalyzer
from semantic.analyzers.expressions import ExpressionsAnalyzer
from semantic.analyzers.statements import StatementsAnalyzer
from semantic.analyzers.functions import FunctionsAnalyzer
from semantic.analyzers.classes import ClassesAnalyzer
from semantic.analyzers.returns import ReturnsAnalyzer

class VisitorCPS(CompiscriptVisitor):
    """
    Visitor semántico orquestador que delega en módulos.
    """
    def __init__(self):
        self.errors = []                # retro-compat para tus logs existentes
        self.diag = Diagnostics()       # wrapper nuevo (aún no usado en todos lados)
        self.scopeManager = ScopeManager()
        self.method_registry = MethodRegistry()

        self.known_classes = set()
        self.class_stack = []
        self.in_method = False
        self.fn_stack = []

        # submódulos
        self.lvals = LValuesAnalyzer(self)
        self.exprs = ExpressionsAnalyzer(self, self.lvals)
        self.stmts = StatementsAnalyzer(self)
        self.funcs = FunctionsAnalyzer(self)
        self.classes = ClassesAnalyzer(self)
        self.returns = ReturnsAnalyzer(self)

        log_semantic("", new_session=True)

    # Utilidad para añadir errores (se mantiene lista "errors" por compat)
    def _append_err(self, err):
        self.errors.append(err)
        return self.diag.extend(err)

    # -------------------------
    # Programa
    # -------------------------
    def visitProgram(self, ctx: CompiscriptParser.ProgramContext):
        # Pre-scan de clases
        for st in ctx.statement():
            cd = st.classDeclaration() if hasattr(st, "classDeclaration") else None
            if cd:
                name = cd.Identifier(0).getText()
                if name in self.known_classes:
                    self._append_err(SemanticError(
                        f"Clase '{name}' ya declarada.",
                        line=cd.start.line, column=cd.start.column))
                else:
                    self.known_classes.add(name)
                    log_semantic(f"[class] (pre-scan) declarada: {name}")

        # Visita normal
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
    # Delegaciones (STATEMENTS)
    # -------------------------
    def visitExpressionStatement(self, ctx): return self.stmts.visitExpressionStatement(ctx)
    def visitBlock(self, ctx):               return self.stmts.visitBlock(ctx)
    def visitVariableDeclaration(self, ctx): return self.stmts.visitVariableDeclaration(ctx)
    def visitConstantDeclaration(self, ctx): return self.stmts.visitConstantDeclaration(ctx)
    def visitAssignment(self, ctx):          return self.stmts.visitAssignment(ctx)
    def visitForeachStatement(self, ctx):    return self.stmts.visitForeachStatement(ctx)

    # -------------------------
    # Funciones / Métodos
    # -------------------------
    def visitFunctionDeclaration(self, ctx): return self.funcs.visitFunctionDeclaration(ctx)
    def visitClassDeclaration(self, ctx):    return self.classes.visitClassDeclaration(ctx)
    def visitReturnStatement(self, ctx):     return self.returns.visitReturnStatement(ctx)

    # -------------------------
    # Expresiones
    # -------------------------
    def visitLiteralExpr(self, ctx):         return self.exprs.visitLiteralExpr(ctx)
    def visitIdentifierExpr(self, ctx):      return self.exprs.visitIdentifierExpr(ctx)
    def visitArrayLiteral(self, ctx):        return self.exprs.visitArrayLiteral(ctx)
    def visitThisExpr(self, ctx):            return self.exprs.visitThisExpr(ctx)
    def visitAdditiveExpr(self, ctx):        return self.exprs.visitAdditiveExpr(ctx)
    def visitMultiplicativeExpr(self, ctx):  return self.exprs.visitMultiplicativeExpr(ctx)
    def visitRelationalExpr(self, ctx):      return self.exprs.visitRelationalExpr(ctx)
    def visitEqualityExpr(self, ctx):        return self.exprs.visitEqualityExpr(ctx)
    def visitLogicalAndExpr(self, ctx):      return self.exprs.visitLogicalAndExpr(ctx)
    def visitLogicalOrExpr(self, ctx):       return self.exprs.visitLogicalOrExpr(ctx)
    def visitUnaryExpr(self, ctx):           return self.exprs.visitUnaryExpr(ctx)
    def visitNewExpr(self, ctx):             return self.exprs.visitNewExpr(ctx)
    def visitLeftHandSide(self, ctx):        return self.exprs.visitLeftHandSide(ctx)

    # Fallback
    def visitExprNoAssign(self, ctx):        return self.visitChildren(ctx)


# Import al final para evitar loop
from semantic.errors import SemanticError
