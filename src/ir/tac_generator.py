from antlr_gen.CompiscriptVisitor import CompiscriptVisitor
from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger import log, logFunction

from ir.tac_lvalues import TacLValues
from ir.tac_expressions import TacExpressions
from ir.tac_control_flow import TacControlFlow
from ir.tac_functions import TacFunctions
from ir.tac_methods import TacMethods
from ir.tac_returns import TacReturns
from ir.tac_statements import TacStatements


class TacGenerator(CompiscriptVisitor):
    """
    Pasada TAC (3AC) sin validaciones semánticas.
    Reutiliza símbolos, clases y métodos ya construidos por la pasada semántica.
    Emite quads a través de `self.emitter`.
    """

    @logFunction(channel="tac")
    def __init__(self, base_semantic_visitor, emitter=None):
        log("[TacGenerator] init", channel="tac")

        # Contexto heredado de la pasada semántica
        self.scopeManager    = base_semantic_visitor.scopeManager
        self.method_registry = base_semantic_visitor.method_registry
        self.class_handler   = base_semantic_visitor.class_handler
        self.known_classes   = getattr(base_semantic_visitor, "known_classes", set())

        # Estado auxiliar para coordinar sub-visitors TAC
        self.loop_depth = 0
        self.stmt_just_terminated = None
        self.stmt_just_terminator_node = None
        self.fn_stack = []
        self.in_method = False

        # Emitter (puede venir del visitor semántico o inyectarse)
        self.emitter = emitter if emitter is not None else getattr(base_semantic_visitor, "emitter")

        # Ensamblado de sub-visitors TAC
        self.lvalues  = TacLValues(self)
        self.exprs    = TacExpressions(self, self.lvalues)
        self.ctrl     = TacControlFlow(self)
        self.tfuncs   = TacFunctions(self)
        self.tmethods = TacMethods(self)
        self.treturns = TacReturns(self) if TacReturns is not None else None
        self.stmts    = TacStatements(self)

    # ---------- Raíz ----------
    @logFunction(channel="tac")
    def visitProgram(self, ctx: CompiscriptParser.ProgramContext):
        log("[TacGenerator] visitProgram", channel="tac")

        # Emitimos TAC solo de funciones y clases a nivel toplevel.
        for st in ctx.statement():
            cd = st.classDeclaration() if hasattr(st, "classDeclaration") else None
            fd = st.functionDeclaration() if hasattr(st, "functionDeclaration") else None

            if cd:
                self.visitClassDeclaration(cd)
            elif fd:
                self.visitFunctionDeclaration(fd)
            else:
                self.visit(st)

        return None

    # ---------- Clases / Funciones ----------
    @logFunction(channel="tac")
    def visitClassDeclaration(self, ctx: CompiscriptParser.ClassDeclarationContext):
        return self.tmethods.visitClassDeclaration(ctx)

    @logFunction(channel="tac")
    def visitFunctionDeclaration(self, ctx: CompiscriptParser.FunctionDeclarationContext):
        return self.tfuncs.visitFunctionDeclaration(ctx)

    # ---------- Control de flujo ----------
    def visitIfStatement(self, ctx):        return self.ctrl.visitIfStatement(ctx)
    def visitWhileStatement(self, ctx):     return self.ctrl.visitWhileStatement(ctx)
    def visitDoWhileStatement(self, ctx):   return self.ctrl.visitDoWhileStatement(ctx)
    def visitForStatement(self, ctx):       return self.ctrl.visitForStatement(ctx)
    def visitSwitchStatement(self, ctx):    return self.ctrl.visitSwitchStatement(ctx)
    def visitBreakStatement(self, ctx):     return self.ctrl.visitBreakStatement(ctx)
    def visitContinueStatement(self, ctx):  return self.ctrl.visitContinueStatement(ctx)

    # ---------- Returns ----------
    @logFunction(channel="tac")
    def visitReturnStatement(self, ctx):
        if self.treturns is not None:
            return self.treturns.visitReturnStatement(ctx)

        # Fallback mínimo si no hay módulo de returns:
        expr = getattr(ctx, "expression", lambda: None)()
        if expr is None:
            self.emitter.endFunctionWithReturn(None)
            return {"terminated": True, "reason": "return"}
        self.visit(expr)  # asegura que exista _place
        place = getattr(expr, "_place", None) or expr.getText()
        self.emitter.endFunctionWithReturn(place)
        return {"terminated": True, "reason": "return"}

    # ---------- Expresiones ----------
    def visitExpression(self, ctx):           return self.exprs.visitExpression(ctx)
    def visitExprNoAssign(self, ctx):         return self.exprs.visitExprNoAssign(ctx)
    def visitPrimaryExpr(self, ctx):          return self.exprs.visitPrimaryExpr(ctx)
    def visitLiteralExpr(self, ctx):          return self.exprs.visitLiteralExpr(ctx)
    def visitIdentifierExpr(self, ctx):       return self.exprs.visitIdentifierExpr(ctx)
    def visitArrayLiteral(self, ctx):         return self.exprs.visitArrayLiteral(ctx)
    def visitThisExpr(self, ctx):             return self.exprs.visitThisExpr(ctx)
    def visitAdditiveExpr(self, ctx):         return self.exprs.visitAdditiveExpr(ctx)
    def visitMultiplicativeExpr(self, ctx):   return self.exprs.visitMultiplicativeExpr(ctx)
    def visitRelationalExpr(self, ctx):       return self.exprs.visitRelationalExpr(ctx)
    def visitEqualityExpr(self, ctx):         return self.exprs.visitEqualityExpr(ctx)
    def visitLogicalAndExpr(self, ctx):       return self.exprs.visitLogicalAndExpr(ctx)
    def visitLogicalOrExpr(self, ctx):        return self.exprs.visitLogicalOrExpr(ctx)
    def visitUnaryExpr(self, ctx):            return self.exprs.visitUnaryExpr(ctx)
    def visitNewExpr(self, ctx):              return self.exprs.visitNewExpr(ctx)
    def visitLeftHandSide(self, ctx):         return self.exprs.visitLeftHandSide(ctx)

    # ---------- Statements ----------
    def visitExpressionStatement(self, ctx):  return self.stmts.visitExpressionStatement(ctx)
    def visitVariableDeclaration(self, ctx):  return self.stmts.visitVariableDeclaration(ctx)
    def visitConstantDeclaration(self, ctx):  return self.stmts.visitConstantDeclaration(ctx)
    def visitAssignment(self, ctx):           return self.stmts.visitAssignment(ctx)
    def visitForeachStatement(self, ctx):     return self.stmts.visitForeachStatement(ctx)
    def visitBlock(self, ctx):                return self.stmts.visitBlock(ctx)
