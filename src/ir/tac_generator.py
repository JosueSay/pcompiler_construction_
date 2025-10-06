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
        log("[TacGenerator] visitProgram - empezando a generar TAC a nivel toplevel", channel="tac")

        for st in ctx.statement():
            cd = st.classDeclaration() if hasattr(st, "classDeclaration") else None
            fd = st.functionDeclaration() if hasattr(st, "functionDeclaration") else None

            if cd:
                log(f"[TacGenerator] visitProgram - clase detectada: {cd.Identifier().getText()}", channel="tac")
                self.visitClassDeclaration(cd)
            elif fd:
                log(f"[TacGenerator] visitProgram - función detectada: {fd.Identifier().getText()}", channel="tac")
                self.visitFunctionDeclaration(fd)
            else:
                log("[TacGenerator] visitProgram - statement toplevel no clase/función", channel="tac")
                self.visit(st)

        log("[TacGenerator] visitProgram - fin de generación TAC toplevel", channel="tac")
        return None

    # ---------- Clases / Funciones ----------
    @logFunction(channel="tac")
    def visitClassDeclaration(self, ctx: CompiscriptParser.ClassDeclarationContext):
        log(f"[TacGenerator] visitClassDeclaration - clase: {ctx.Identifier().getText()}", channel="tac")
        return self.tmethods.visitClassDeclaration(ctx)

    @logFunction(channel="tac")
    def visitFunctionDeclaration(self, ctx: CompiscriptParser.FunctionDeclarationContext):
        log(f"[TacGenerator] visitFunctionDeclaration - función: {ctx.Identifier().getText()}", channel="tac")
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
        log(f"[TacGenerator] visitReturnStatement - procesando return", channel="tac")
        if self.treturns is not None:
            return self.treturns.visitReturnStatement(ctx)

        expr = getattr(ctx, "expression", lambda: None)()
        if expr is None:
            log("[TacGenerator] visitReturnStatement - return sin expresión", channel="tac")
            self.emitter.endFunctionWithReturn(None)
            return {"terminated": True, "reason": "return"}

        self.visit(expr)
        place = getattr(expr, "_place", None) or expr.getText()
        log(f"[TacGenerator] visitReturnStatement - return con expresión, place={place}", channel="tac")
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
