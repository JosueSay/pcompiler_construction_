from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import BoolType, ErrorType, ClassType, ArrayType
from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic

def asList(x):
    if x is None:
        return []
    try:
        return list(x)
    except TypeError:
        return [x]

class ControlFlowAnalyzer:
    """
    Reglas semánticas de control de flujo:
      - Condiciones de if/while/do-while/for/switch deben ser boolean.
      - break/continue solo dentro de bucles.
      - switch: tipos de los 'case' compatibles con el scrutinee.
    También colabora con la detección de terminación para 'if/else'.
    """

    def __init__(self, v):
        self.v = v  # VisitorCPS

    def requireBoolean(self, cond_t, ctx, who: str):
        if isinstance(cond_t, ErrorType):
            return
        if not isinstance(cond_t, BoolType):
            self.v.appendErr(SemanticError(
                f"La condición de {who} debe ser boolean, no {cond_t}.",
                line=ctx.start.line, column=ctx.start.column))

    def sameType(self, a, b):
        if isinstance(a, ErrorType) or isinstance(b, ErrorType):
            return True  # evitar cascada
        if type(a) is type(b):
            if isinstance(a, ClassType):
                return a.name == b.name
            if hasattr(a, "elem_type") and hasattr(b, "elem_type"):  # arrays
                return self.sameType(a.elem_type, b.elem_type)
            return True
        return False

    def walk(self, node):
        try:
            for ch in node.getChildren():
                yield ch
                yield from self.walk(ch)
        except Exception:
            return

    def collectCaseExprs(self, ctx):
        exprs = []
        cb = getattr(ctx, "caseBlock", None)
        if callable(cb):
            cb = cb()
        if cb:
            caseClause = getattr(cb, "caseClause", None)
            if callable(caseClause):
                for c in asList(caseClause()):
                    get_exprs = getattr(c, "expression", None)
                    if callable(get_exprs):
                        exprs.extend(asList(get_exprs()))
        if not exprs:
            for n in self.walk(ctx):
                cname = n.__class__.__name__.lower()
                if "case" in cname:
                    get_exprs = getattr(n, "expression", None)
                    if callable(get_exprs):
                        exprs.extend(asList(get_exprs()))
        return exprs

    # if
    def visitIfStatement(self, ctx: CompiscriptParser.IfStatementContext):
        cond_t = self.v.visit(ctx.expression())
        self.requireBoolean(cond_t, ctx, "if")

        # Bloque then
        then_result = {"terminated": False, "reason": None}
        if ctx.block(0):
            then_result = self.v.visit(ctx.block(0)) or then_result

        # Bloque else (si existe)
        else_result = {"terminated": False, "reason": None}
        if ctx.block(1):
            else_result = self.v.visit(ctx.block(1)) or else_result

        # Un 'if' es terminante SOLO si ambas ramas terminan.
        both_terminate = bool(then_result.get("terminated") and else_result.get("terminated"))
        if both_terminate:
            self.v.stmt_just_terminated = "if-else"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "if-else"}

        # IMPORTANTe: limpiar cualquier terminación "interna" que no aplique al 'if' completo
        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None
        return {"terminated": False, "reason": None}


    # while
    def visitWhileStatement(self, ctx: CompiscriptParser.WhileStatementContext):
        cond_t = self.v.visit(ctx.expression())
        self.requireBoolean(cond_t, ctx, "while")
        self.v.loop_depth += 1
        self.v.visit(ctx.block())
        self.v.loop_depth -= 1
        # Un while no se considera terminante de forma estática
        return {"terminated": False, "reason": None}

    # do-while
    def visitDoWhileStatement(self, ctx: CompiscriptParser.DoWhileStatementContext):
        self.v.loop_depth += 1
        self.v.visit(ctx.block())
        self.v.loop_depth -= 1
        cond_t = self.v.visit(ctx.expression())
        self.requireBoolean(cond_t, ctx, "do-while")
        return {"terminated": False, "reason": None}

    # for
    def visitForStatement(self, ctx: CompiscriptParser.ForStatementContext):
        if getattr(ctx, "forInitializer", None) and ctx.forInitializer():
            self.v.visit(ctx.forInitializer())

        cond_expr = None
        if hasattr(ctx, "condition") and ctx.condition():
            cond_expr = ctx.condition()
        else:
            exprs = asList(getattr(ctx, "expression", lambda: None)())
            cond_expr = exprs[0] if exprs else None

        if cond_expr is not None:
            cond_t = self.v.visit(cond_expr)
            self.requireBoolean(cond_t, ctx, "for")

        if getattr(ctx, "forUpdate", None) and ctx.forUpdate():
            self.v.visit(ctx.forUpdate())

        self.v.loop_depth += 1
        self.v.visit(ctx.block())
        self.v.loop_depth -= 1
        return {"terminated": False, "reason": None}

    # break / continue
    def visitBreakStatement(self, ctx: CompiscriptParser.BreakStatementContext):
        if self.v.loop_depth <= 0:
            self.v.appendErr(SemanticError(
                "'break' fuera de un bucle.",
                line=ctx.start.line, column=ctx.start.column))
        # Marca que esta sentencia termina el flujo normal del bloque actual
        self.v.stmt_just_terminated = "break"
        self.v.stmt_just_terminator_node = ctx
        return {"terminated": True, "reason": "break"}

    def visitContinueStatement(self, ctx: CompiscriptParser.ContinueStatementContext):
        if self.v.loop_depth <= 0:
            self.v.appendErr(SemanticError(
                "'continue' fuera de un bucle.",
                line=ctx.start.line, column=ctx.start.column))
        # También termina el flujo "hacia sentencias siguientes" en el bloque actual
        self.v.stmt_just_terminated = "continue"
        self.v.stmt_just_terminator_node = ctx
        return {"terminated": True, "reason": "continue"}

    # switch
    def visitSwitchStatement(self, ctx):
        # 1) primer tipo
        get_expr = getattr(ctx, "expression", None)
        scrutinee_ctx = None
        if callable(get_expr):
            exprs = asList(get_expr())
            scrutinee_ctx = exprs[0] if exprs else None
        scrutinee_t = self.v.visit(scrutinee_ctx) if scrutinee_ctx else ErrorType()

        # 2) Validar tipos de 'case'
        for c in asList(getattr(ctx, "switchCase", lambda: None)()):
            for e in asList(c.expression()):
                et = self.v.visit(e)
                if not isinstance(scrutinee_t, ErrorType) and not isinstance(et, ErrorType):
                    if not self.sameType(scrutinee_t, et):
                        self.v.appendErr(SemanticError(
                            f"Tipo de 'case' ({et}) incompatible con el 'switch' ({scrutinee_t}).",
                            line=e.start.line, column=e.start.column))

        # 3) Visitar SOLO los statements de cada case/default
        for c in asList(getattr(ctx, "switchCase", lambda: None)()):
            for st in asList(c.statement()):
                self.v.visit(st)

        d = getattr(ctx, "defaultCase", None)
        d = d() if callable(d) else None
        if d:
            for st in asList(d.statement()):
                self.v.visit(st)

        return {"terminated": False, "reason": None}

    # ------ ALIAS ------
    def visitSwitchStmt(self, ctx):
        return self.visitSwitchStatement(ctx)

    def visitSwitch(self, ctx):
        return self.visitSwitchStatement(ctx)

    def visitCaseStatement(self, ctx):
        return self.visitSwitchStatement(ctx)
