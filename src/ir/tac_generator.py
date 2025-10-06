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


    # Devuelve el primer nodo si la llamada retorna lista; si no, el propio valor
    def h_First(self, ctx, name):
        m = getattr(ctx, name, None)
        if not callable(m):
            return None
        r = m()
        if isinstance(r, list):
            return r[0] if r else None
        return r

    # Devuelve el texto del primer Identifier (soporta lista o único)
    def h_IdentText(self, ctx):
        idm = getattr(ctx, "Identifier", None)
        if not callable(idm):
            return "<anon>"
        
        try:
            tok = idm(0)          # si la signatura soporta índice
            if tok is not None:
                return tok.getText()
        except TypeError:
            pass
        # Fallback: sin índice puede devolver lista o único
        r = idm()
        if isinstance(r, list):
            r = r[0] if r else None
        return r.getText() if r is not None else "<anon>"

    # ---------- Raíz ----------
    def visitProgram(self, ctx: CompiscriptParser.ProgramContext):
        log("[TacGenerator] visitProgram - empezando a generar TAC a nivel toplevel", channel="tac")

        for st in ctx.statement():
            cd = self.h_First(st, "classDeclaration")
            fd = self.h_First(st, "functionDeclaration")

            if cd is not None:
                log(f"[TacGenerator] visitProgram - clase detectada: {self.h_IdentText(cd)}", channel="tac")
                self.visitClassDeclaration(cd)
            elif fd is not None:
                log(f"[TacGenerator] visitProgram - función detectada: {self.h_IdentText(fd)}", channel="tac")
                self.visitFunctionDeclaration(fd)
            else:
                log("[TacGenerator] visitProgram - statement toplevel no clase/función", channel="tac")
                self.visit(st)

        log("[TacGenerator] visitProgram - fin de generación TAC toplevel", channel="tac")
        return None

    # ---------- Clases / Funciones ----------
    def visitClassDeclaration(self, ctx: CompiscriptParser.ClassDeclarationContext):
        log(f"[TacGenerator] visitClassDeclaration - clase: {self.h_IdentText(ctx)}", channel="tac")
        return self.tmethods.visitClassDeclaration(ctx)

    def visitFunctionDeclaration(self, ctx: CompiscriptParser.FunctionDeclarationContext):
        log(f"[TacGenerator] visitFunctionDeclaration - función: {self.h_IdentText(ctx)}", channel="tac")
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
