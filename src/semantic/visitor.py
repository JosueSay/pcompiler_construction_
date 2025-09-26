from antlr_gen.CompiscriptVisitor import CompiscriptVisitor
from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger_semantic import log_semantic

from semantic.scope_manager import ScopeManager
from semantic.diagnostics import Diagnostics
from semantic.registry.method_registry import MethodRegistry
from semantic.class_handler import ClassHandler

# IR
from ir.emitter import Emitter

# Analyzers
from semantic.analyzers.lvalues import LValuesAnalyzer
from semantic.analyzers.expressions import ExpressionsAnalyzer
from semantic.analyzers.statements import StatementsAnalyzer
from semantic.analyzers.functions import FunctionsAnalyzer
from semantic.analyzers.classes import ClassesAnalyzer
from semantic.analyzers.returns import ReturnsAnalyzer
from semantic.analyzers.controlFlow import ControlFlowAnalyzer

from semantic.errors import SemanticError

class VisitorCPS(CompiscriptVisitor):
    def __init__(self, emitter: Emitter | None = None):
        self.errors = []
        self.diag = Diagnostics()
        self.scopeManager = ScopeManager()
        self.method_registry = MethodRegistry()
        self.class_handler = ClassHandler()
        
        self.emitter: Emitter = emitter or Emitter()

        self.known_classes = set()
        self.class_stack = []
        self.in_method = False
        self.fn_stack = []
        self.fn_ctx_stack = []
        self.loop_depth = 0

        # Flags internos para detección de terminación por sentencia
        self.stmt_just_terminated = None        # "return" | "break" | "continue" | "if-else" | None
        self.stmt_just_terminator_node = None   # nodo ANTLR de la sentencia terminante (opcional)

        self.lvals = LValuesAnalyzer(self)
        self.exprs = ExpressionsAnalyzer(self, self.lvals)
        self.stmts = StatementsAnalyzer(self)
        self.funcs = FunctionsAnalyzer(self)
        self.classes = ClassesAnalyzer(self)
        self.returns = ReturnsAnalyzer(self)
        self.ctrl = ControlFlowAnalyzer(self)

        log_semantic("")

    def appendErr(self, err):
        self.errors.append(err)
        return self.diag.extend(err)

    def visitProgram(self, ctx: CompiscriptParser.ProgramContext):
        # --- Pre-scan: registrar nombres de clases (y base, si existe) ---
        for st in ctx.statement():
            cd = st.classDeclaration() if hasattr(st, "classDeclaration") else None
            if cd:
                cname = cd.Identifier(0).getText()
                base = cd.Identifier(1).getText() if len(cd.Identifier()) > 1 else None

                if cname in self.known_classes:
                    self.appendErr(SemanticError(
                        f"Clase '{cname}' ya declarada.",
                        line=cd.start.line, column=cd.start.column))
                else:
                    self.known_classes.add(cname)
                    self.class_handler.ensure_class(cname, base)
                    if base:
                        log_semantic(f"[class] (pre-scan) declarada: {cname} : {base}")
                    else:
                        log_semantic(f"[class] (pre-scan) declarada: {cname}")

                if base and base not in self.known_classes:
                    self.appendErr(SemanticError(
                        f"Clase base '{base}' no declarada para '{cname}'.",
                        line=cd.start.line, column=cd.start.column))

        # --- Recorrido normal ---
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
        return None

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
    # Control de flujo
    # -------------------------
    def visitIfStatement(self, ctx):         return self.ctrl.visitIfStatement(ctx)
    def visitWhileStatement(self, ctx):      return self.ctrl.visitWhileStatement(ctx)
    def visitDoWhileStatement(self, ctx):    return self.ctrl.visitDoWhileStatement(ctx)
    def visitForStatement(self, ctx):        return self.ctrl.visitForStatement(ctx)
    def visitSwitchStatement(self, ctx):     return self.ctrl.visitSwitchStatement(ctx)
    def visitSwitchStmt(self, ctx):          return self.ctrl.visitSwitchStatement(ctx)  # alias
    def visitSwitch(self, ctx):              return self.ctrl.visitSwitchStatement(ctx)  # alias
    def visitCaseStatement(self, ctx):       return self.ctrl.visitSwitchStatement(ctx)  # alias
    def visitBreakStatement(self, ctx):      return self.ctrl.visitBreakStatement(ctx)
    def visitContinueStatement(self, ctx):   return self.ctrl.visitContinueStatement(ctx)

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

    def visitExpression(self, ctx):          return self.exprs.visitExpression(ctx)
    def visitExprNoAssign(self, ctx):        return self.exprs.visitExprNoAssign(ctx)
    def visitPrimaryExpr(self, ctx):         return self.exprs.visitPrimaryExpr(ctx)
