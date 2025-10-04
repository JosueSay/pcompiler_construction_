from typing import Any
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import BoolType, ErrorType, ClassType
from semantic.errors import SemanticError
from logs.logger import log, logFunction

from utils.ast_utils import (
    asList,
    walk,
    safeAttr,
    firstExpression,
    isAssignText,
    firstSwitchDiscriminant,
    hasDefaultClause,
)


class ControlFlowAnalyzer:
    """
    Análisis **semántico** del control de flujo (sin emitir TAC).

    Reglas que valida:
      - Condiciones de `if`, `while`, `do-while`, `for` deben ser de tipo boolean.
      - `break`/`continue` solo dentro de bucles (y `break` permitido en `switch`).
      - En `switch`, los `case` deben ser compatibles con el tipo del discriminante.
    """

    def __init__(self, v):
        log("===== [controlFlow.py] Inicio (SEM) =====", channel="semantic")
        self.v = v
        self.switch_depth = 0  # contexto para validar 'break' en switch

    # ---------- helpers semánticos ----------
    @logFunction(channel="semantic")
    def typeOfSilent(self, expr_ctx):
        """
        Evalúa el tipo de una expresión **sin** generar TAC.
        Lo hace activando temporalmente una barrera en el emitter.
        """
        if expr_ctx is None:
            return ErrorType()

        old_barrier = getattr(self.v, "emitter", None).flow_terminated if hasattr(self.v, "emitter") else None
        if hasattr(self.v, "emitter"):
            self.v.emitter.flow_terminated = True
        try:
            t = self.v.visit(expr_ctx)
        finally:
            if hasattr(self.v, "emitter"):
                self.v.emitter.flow_terminated = old_barrier
                try:
                    self.v.emitter.temp_pool.resetPerStatement()
                except Exception:
                    pass
        return t

    @logFunction(channel="semantic")
    def requireBoolean(self, cond_t, ctx, who: str):
        """Reporta error si `cond_t` no es boolean (ignorando ErrorType para evitar cascadas)."""
        if isinstance(cond_t, ErrorType):
            return
        if not isinstance(cond_t, BoolType):
            self.v.appendErr(SemanticError(
                f"La condición de {who} debe ser boolean, no {cond_t}.",
                line=ctx.start.line, column=ctx.start.column))

    @logFunction(channel="semantic")
    def sameType(self, a, b):
        """
        Equivalencia de tipos para `switch`:
        - Propaga True si alguno es ErrorType (evita ruido).
        - Clases: compara por nombre.
        - Arreglos: compara recursivamente `elem_type`.
        - Caso general: misma clase de tipo.
        """
        if isinstance(a, ErrorType) or isinstance(b, ErrorType):
            return True
        if type(a) is type(b):
            if isinstance(a, ClassType):
                return a.name == b.name
            if hasattr(a, "elem_type") and hasattr(b, "elem_type"):
                return self.sameType(a.elem_type, b.elem_type)
            return True
        return False

    @logFunction(channel="semantic")
    def collectCaseExprs(self, ctx):
        """
        Recolecta las expresiones de los `case` de un `switch` (robusta a variaciones del parser).
        """
        exprs = []
        cb = getattr(ctx, "caseBlock", None)
        if callable(cb):
            cb = cb()
        if cb:
            case_clause = getattr(cb, "caseClause", None)
            if callable(case_clause):
                for c in asList(case_clause()):
                    get_exprs = getattr(c, "expression", None)
                    if callable(get_exprs):
                        exprs.extend(asList(get_exprs()))
        if not exprs:
            for n in walk(ctx):
                cname = n.__class__.__name__.lower()
                if "case" in cname:
                    get_exprs = getattr(n, "expression", None)
                    if callable(get_exprs):
                        exprs.extend(asList(get_exprs()))
        return exprs

    # ---------- IF ----------
    @logFunction(channel="semantic")
    def visitIfStatement(self, ctx: CompiscriptParser.IfStatementContext):
        cond_ctx = firstExpression(ctx)
        if cond_ctx is not None:
            cond_t = self.typeOfSilent(cond_ctx)
            self.requireBoolean(cond_t, ctx, "if")

        stmts = self.collectStmtOrBlock(ctx)
        then_stmt = stmts[0] if len(stmts) >= 1 else None
        else_stmt = stmts[1] if len(stmts) >= 2 else None

        old_barrier = getattr(self.v, "emitter", None).flow_terminated if hasattr(self.v, "emitter") else None
        if hasattr(self.v, "emitter"):
            self.v.emitter.flow_terminated = True
        try:
            if then_stmt is not None:
                self.v.visit(then_stmt)
            if else_stmt is not None:
                self.v.visit(else_stmt)
        finally:
            if hasattr(self.v, "emitter"):
                self.v.emitter.flow_terminated = old_barrier

        return {"terminated": False, "reason": None}

    # ---------- WHILE ----------
    @logFunction(channel="semantic")
    def visitWhileStatement(self, ctx: CompiscriptParser.WhileStatementContext):
        cond_ctx = safeAttr(ctx, "expression") or safeAttr(ctx, "cond") or safeAttr(ctx, "condition")
        if cond_ctx is not None:
            cond_t = self.typeOfSilent(cond_ctx)
            self.requireBoolean(cond_t, ctx, "while")

        body = safeAttr(ctx, "statement") or safeAttr(ctx, "body") or safeAttr(ctx, "block")

        self.v.loop_depth += 1
        old_barrier = getattr(self.v, "emitter", None).flow_terminated if hasattr(self.v, "emitter") else None
        if hasattr(self.v, "emitter"):
            self.v.emitter.flow_terminated = True
        try:
            if body is not None:
                self.v.visit(body)
        finally:
            if hasattr(self.v, "emitter"):
                self.v.emitter.flow_terminated = old_barrier
            self.v.loop_depth -= 1

        return {"terminated": False, "reason": None}

    # ---------- DO-WHILE ----------
    @logFunction(channel="semantic")
    def visitDoWhileStatement(self, ctx: CompiscriptParser.DoWhileStatementContext):
        body = safeAttr(ctx, "statement") or safeAttr(ctx, "body") or safeAttr(ctx, "block")
        cond_ctx = safeAttr(ctx, "expression") or safeAttr(ctx, "cond") or safeAttr(ctx, "condition")

        if cond_ctx is not None:
            cond_t = self.typeOfSilent(cond_ctx)
            self.requireBoolean(cond_t, ctx, "do-while")

        self.v.loop_depth += 1
        old_barrier = getattr(self.v, "emitter", None).flow_terminated if hasattr(self.v, "emitter") else None
        if hasattr(self.v, "emitter"):
            self.v.emitter.flow_terminated = True
        try:
            if body is not None:
                self.v.visit(body)
        finally:
            if hasattr(self.v, "emitter"):
                self.v.emitter.flow_terminated = old_barrier
            self.v.loop_depth -= 1

        return {"terminated": False, "reason": None}

    # ---------- FOR ----------
    @logFunction(channel="semantic")
    def visitForStatement(self, ctx: CompiscriptParser.ForStatementContext):
        init = safeAttr(ctx, "forInit") or safeAttr(ctx, "init") or safeAttr(ctx, "initializer")
        if init is None:
            try:
                vdecl = getattr(ctx, "variableDeclaration", None)
                if callable(vdecl):
                    init = vdecl()
            except Exception:
                pass
        if init is None:
            try:
                assign = getattr(ctx, "assignment", None)
                if callable(assign):
                    init = assign()
            except Exception:
                pass

        cond_ctx = safeAttr(ctx, "forCondition") or safeAttr(ctx, "cond") or safeAttr(ctx, "condition")
        step = safeAttr(ctx, "forStep") or safeAttr(ctx, "step") or safeAttr(ctx, "increment")
        body = safeAttr(ctx, "statement") or safeAttr(ctx, "body") or safeAttr(ctx, "block")

        get_exprs = getattr(ctx, "expression", None)
        exprs = list(get_exprs() or []) if callable(get_exprs) else []
        assign_exprs = [e for e in exprs if isAssignText(e.getText())]
        non_assign_exprs = [e for e in exprs if not isAssignText(e.getText())]

        if cond_ctx is not None and isAssignText(cond_ctx.getText()):
            cond_ctx = None
        if cond_ctx is None and non_assign_exprs:
            cond_ctx = non_assign_exprs[-1]
        if step is None and assign_exprs:
            step = assign_exprs[-1]
        if cond_ctx is not None and step is not None and cond_ctx.getText() == step.getText():
            replaced = False
            for e in reversed(non_assign_exprs):
                if e.getText() != step.getText():
                    cond_ctx = e
                    replaced = True
                    break
            if not replaced:
                cond_ctx = None

        if cond_ctx is not None:
            cond_t = self.typeOfSilent(cond_ctx)
            self.requireBoolean(cond_t, ctx, "for")

        old_barrier = getattr(self.v, "emitter", None).flow_terminated if hasattr(self.v, "emitter") else None
        if hasattr(self.v, "emitter"):
            self.v.emitter.flow_terminated = True
        try:
            if init is not None:
                self.v.visit(init)
            self.v.loop_depth += 1
            if body is not None:
                self.v.visit(body)
            if step is not None:
                self.v.visit(step)
        finally:
            self.v.loop_depth -= 1
            if hasattr(self.v, "emitter"):
                self.v.emitter.flow_terminated = old_barrier

        return {"terminated": False, "reason": None}

    # ---------- SWITCH ----------
    @logFunction(channel="semantic")
    def visitSwitchStatement(self, ctx):
        discr = firstSwitchDiscriminant(ctx)
        if discr is None:
            return {"terminated": False, "reason": None}

        scrutinee_t = self.typeOfSilent(discr)

        for e in self.collectCaseExprs(ctx):
            et = self.typeOfSilent(e)
            if not isinstance(scrutinee_t, ErrorType) and not isinstance(et, ErrorType):
                if not self.sameType(scrutinee_t, et):
                    self.v.appendErr(SemanticError(
                        f"Tipo de 'case' ({et}) incompatible con el 'switch' ({scrutinee_t}).",
                        line=e.start.line, column=e.start.column))

        # Recolectar statements por caso y default (independiente del layout del parser)
        stmt_ctx = getattr(CompiscriptParser, "StatementContext", None)
        expr_ctx = getattr(CompiscriptParser, "ExpressionContext", None)

        def gatherStatements(node):
            out = []
            if node is None:
                return out
            stmts = asList(safeAttr(node, "statement"))
            if stmts:
                return stmts
            try:
                for ch in walk(node):
                    if stmt_ctx is not None and isinstance(ch, stmt_ctx):
                        out.append(ch)
            except Exception:
                pass
            return out

        def firstChildExpression(node):
            if node is None:
                return None
            e = safeAttr(node, "expression")
            if e is not None:
                try:
                    seq = list(e)
                    if seq:
                        return seq[0]
                except TypeError:
                    return e
            try:
                for ch in walk(node):
                    if expr_ctx is not None and isinstance(ch, expr_ctx):
                        return ch
            except Exception:
                pass
            return None

        cases: list[tuple[Any, list[Any]]] = []
        default_stmts: list[Any] | None = None

        for ch in getattr(ctx, "getChildren", lambda: [])():
            cname = type(ch).__name__
            if cname in ("SwitchCaseContext", "SwitchCase"):
                ce = firstChildExpression(ch) or discr
                sts = gatherStatements(ch)
                cases.append((ce, sts))
            elif cname in ("DefaultCaseContext", "DefaultCase"):
                default_stmts = gatherStatements(ch)

        if not cases and default_stmts is None:
            exprs = self.collectCaseExprs(ctx)
            if exprs:
                cases = [(e, []) for e in exprs]
            if hasDefaultClause(ctx):
                default_stmts = []

        self.switch_depth += 1
        old_barrier = getattr(self.v, "emitter", None).flow_terminated if hasattr(self.v, "emitter") else None
        if hasattr(self.v, "emitter"):
            self.v.emitter.flow_terminated = True
        try:
            for _, st_list in cases:
                for st in st_list:
                    self.v.visit(st)
            if default_stmts is not None:
                for st in default_stmts:
                    self.v.visit(st)
        finally:
            if hasattr(self.v, "emitter"):
                self.v.emitter.flow_terminated = old_barrier
            self.switch_depth -= 1

        return {"terminated": False, "reason": None}

    # ---------- break / continue ----------
    @logFunction(channel="semantic")
    def visitBreakStatement(self, ctx: CompiscriptParser.BreakStatementContext):
        if self.v.loop_depth <= 0 and self.switch_depth <= 0:
            self.v.appendErr(SemanticError(
                "'break' fuera de un bucle o switch.",
                line=ctx.start.line, column=ctx.start.column))
        return {"terminated": False, "reason": None}

    @logFunction(channel="semantic")
    def visitContinueStatement(self, ctx: CompiscriptParser.ContinueStatementContext):
        if self.v.loop_depth <= 0:
            self.v.appendErr(SemanticError(
                "'continue' fuera de un bucle.",
                line=ctx.start.line, column=ctx.start.column))
        return {"terminated": False, "reason": None}

    # ---------- util interno ----------
    def collectStmtOrBlock(self, ctx):
        """
        Versión local y mínima de `collectStmtOrBlock`:
        prioriza `ctx.statement()` y luego busca bloques/Statements sencillos.
        """
        stmts = asList(safeAttr(ctx, "statement"))
        if stmts:
            return stmts

        out = []
        block_ctx = getattr(CompiscriptParser, "BlockContext", None)
        try:
            for i in range(ctx.getChildCount()):
                ch = ctx.getChild(i)
                if isinstance(ch, CompiscriptParser.StatementContext):
                    out.append(ch)
                elif block_ctx is not None and isinstance(ch, block_ctx):
                    out.append(ch)
                elif type(ch).__name__.endswith("BlockContext"):
                    out.append(ch)
        except Exception:
            pass
        return out
