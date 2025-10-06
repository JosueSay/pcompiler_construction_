from antlr4.tree.Tree import TerminalNode
from typing import Any
from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger import log, logFunction
from utils.ast_utils import (
    walk, extractNotInner,
    asList, maybeCall, safeAttr, firstExpression,
    splitAssignmentText, isAssignText, collectStmtOrBlock,
    firstSwitchDiscriminant, hasDefaultClause
)


class TacControlFlow:
    """
    Control de flujo para la pasada TAC (sin validaciones semánticas).
    Este visitor asume que la fase semántica ya resolvió tipos y símbolos.

    Requisitos sobre `self.v` (visitor padre):
      - emitter:     objeto con primitivas de emisión de TAC
      - visit(node): despacha a los sub-visitors TAC
      - loop_depth:  entero que llevamos como contador de anidamiento
      - stmt_just_terminated / stmt_just_terminator_node: marcas de barrera de flujo
    """

    def __init__(self, v):
        log("===== [tac_control_flow] start =====", channel="tac")
        self.v = v
        self.loop_ctx_stack: list[dict[str, str]] = []
        self.switch_ctx_stack: list[dict[str, str]] = []

    def unwrapCondCore(self, n):
        # expression -> assignmentExpr -> conditionalExpr -> logicalOrExpr
        if isinstance(n, CompiscriptParser.ExpressionContext):
            a = n.assignmentExpr()
            if a and hasattr(a, "conditionalExpr"):
                c = a.conditionalExpr()
                return self.unwrapCondCore(c or n)
            return n
        if isinstance(n, CompiscriptParser.ConditionalExprContext):
            return n.logicalOrExpr() or n
        return n


    # ---------------- Condiciones compuestas ----------------

    @logFunction(channel="tac")
    def visitCond(self, expr_ctx, l_true: str, l_false: str) -> None:
        """
        Emite saltos con cortocircuito:
          - !E        → invierte destinos
          - A || B .. → evalúa izquierda→derecha, si true salta a Ltrue
          - A && B .. → evalúa izquierda→derecha, si false salta a Lfalse
          - Base      → IF cond GOTO Ltrue ; GOTO Lfalse
        """
        # 0) Manejo de negación unaria en cualquier profundidad razonable.
        neg_inner = extractNotInner(expr_ctx)
        if neg_inner is not None:
            self.visitCond(neg_inner, l_false, l_true)
            return

        node = self.unwrapCondCore(expr_ctx)

        # 1) OR: logicalOrExpr ::= logicalAndExpr ('||' logicalAndExpr)*
        OrCtx = getattr(CompiscriptParser, "LogicalOrExprContext", None)
        if OrCtx is not None and isinstance(node, OrCtx):
            and_terms = list(node.logicalAndExpr() or [])
            if len(and_terms) <= 1:
                # Sin '||' real → caso base
                self.v.emitter.emitIfGoto(node.getText(), l_true)
                self.v.emitter.emitGoto(l_false)
                return

            # A || B || C ...  → if A goto Ltrue; else evalúa resto
            # Vamos encadenando labels intermedios para continuar.
            next_label = None
            for k, term in enumerate(and_terms):
                is_last = (k == len(and_terms) - 1)
                if is_last:
                    # Último: decide definitivamente
                    self.visitCond(term, l_true, l_false)
                else:
                    next_label = self.v.emitter.newLabel("Lor")
                    self.visitCond(term, l_true, next_label)
                    self.v.emitter.emitLabel(next_label)
            return

        # 2) AND: logicalAndExpr ::= equalityExpr ('&&' equalityExpr)*
        AndCtx = getattr(CompiscriptParser, "LogicalAndExprContext", None)
        if AndCtx is not None and isinstance(node, AndCtx):
            eq_terms = list(node.equalityExpr() or [])
            if len(eq_terms) <= 1:
                self.v.emitter.emitIfGoto(node.getText(), l_true)
                self.v.emitter.emitGoto(l_false)
                return

            # A && B && C ... → si A false salta a Lfalse; si true evalúa resto
            next_label = None
            for k, term in enumerate(eq_terms):
                is_last = (k == len(eq_terms) - 1)
                if is_last:
                    self.visitCond(term, l_true, l_false)
                else:
                    next_label = self.v.emitter.newLabel("Land")
                    self.visitCond(term, next_label, l_false)
                    self.v.emitter.emitLabel(next_label)
            return

        # 3) Caso base: condición como texto (el backend de ejecución la evalúa).
        self.v.emitter.emitIfGoto(node.getText(), l_true)
        self.v.emitter.emitGoto(l_false)

    # ---------------- if / else ----------------

    @logFunction(channel="tac")
    def visitIfStatement(self, ctx: CompiscriptParser.IfStatementContext):
        cond_ctx = firstExpression(ctx)
        if cond_ctx is None:
            return {"terminated": False, "reason": None}

        stmts = collectStmtOrBlock(ctx)
        then_stmt = stmts[0] if len(stmts) >= 1 else None
        else_stmt = stmts[1] if len(stmts) >= 2 else None
        if then_stmt is None:
            return {"terminated": False, "reason": None}

        l_then = self.v.emitter.newLabel("Lthen")
        l_end = self.v.emitter.newLabel("Lend")
        l_else = self.v.emitter.newLabel("Lelse") if else_stmt is not None else l_end

        self.visitCond(cond_ctx, l_then, l_else)

        self.v.emitter.emitLabel(l_then)
        then_result = self.v.visit(then_stmt) or {"terminated": False, "reason": None}

        if else_stmt is not None:
            self.v.emitter.emitGoto(l_end)
            self.v.emitter.emitLabel(l_else)
            if bool(then_result.get("terminated")):
                self.v.emitter.clearFlowTermination()
            else_result = self.v.visit(else_stmt) or {"terminated": False, "reason": None}
        else:
            else_result = {"terminated": False, "reason": None}

        self.v.emitter.emitLabel(l_end)
        both_terminate = bool(then_result.get("terminated") and else_result.get("terminated"))

        if not both_terminate:
            self.v.emitter.clearFlowTermination()

        if both_terminate:
            self.v.stmt_just_terminated = "if-else"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "if-else"}

        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None
        return {"terminated": False, "reason": None}

    # ---------------- while ----------------

    @logFunction(channel="tac")
    def visitWhileStatement(self, ctx: CompiscriptParser.WhileStatementContext):
        cond_ctx = safeAttr(ctx, "expression") or safeAttr(ctx, "cond") or safeAttr(ctx, "condition")
        body = safeAttr(ctx, "statement") or safeAttr(ctx, "body") or safeAttr(ctx, "block")

        l_start = self.v.emitter.newLabel("Lstart")
        l_body = self.v.emitter.newLabel("Lbody")
        l_end = self.v.emitter.newLabel("Lend")

        self.loop_ctx_stack.append({"break": l_end, "continue": l_start})
        self.v.loop_depth += 1

        self.v.emitter.emitLabel(l_start)
        self.visitCond(cond_ctx, l_body, l_end)

        self.v.emitter.emitLabel(l_body)
        self.v.visit(body)
        self.v.emitter.emitGoto(l_start)

        self.v.emitter.emitLabel(l_end)
        self.v.emitter.clearFlowTermination()
        self.loop_ctx_stack.pop()
        self.v.loop_depth -= 1

        return {"terminated": False, "reason": None}

    # ---------------- do / while ----------------

    @logFunction(channel="tac")
    def visitDoWhileStatement(self, ctx: CompiscriptParser.DoWhileStatementContext):
        body = safeAttr(ctx, "statement") or safeAttr(ctx, "body") or safeAttr(ctx, "block")
        cond_ctx = safeAttr(ctx, "expression") or safeAttr(ctx, "cond") or safeAttr(ctx, "condition")

        l_body = self.v.emitter.newLabel("Lbody")
        l_cond = self.v.emitter.newLabel("Lcond")
        l_end = self.v.emitter.newLabel("Lend")

        self.loop_ctx_stack.append({"break": l_end, "continue": l_cond})
        self.v.loop_depth += 1

        self.v.emitter.emitLabel(l_body)
        self.v.visit(body)
        self.v.emitter.emitLabel(l_cond)
        self.visitCond(cond_ctx, l_body, l_end)

        self.v.emitter.emitLabel(l_end)
        self.v.emitter.clearFlowTermination()
        self.loop_ctx_stack.pop()
        self.v.loop_depth -= 1

        return {"terminated": False, "reason": None}

    # ---------------- for ----------------

    @logFunction(channel="tac")
    def emitForStep(self, step_ctx):
        if step_ctx is None:
            return

        AssignCtx = getattr(CompiscriptParser, "AssignExprContext", None)
        PropAssignCtx = getattr(CompiscriptParser, "PropertyAssignExprContext", None)

        def contains(node, kinds):
            try:
                for ch in node.getChildren():
                    if any(isinstance(ch, k) for k in kinds if k is not None):
                        return True
                    if contains(ch, kinds):
                        return True
            except Exception:
                pass
            return False

        is_assign_like = contains(step_ctx, (AssignCtx, PropAssignCtx))

        if is_assign_like:
            # Usa la bajada de asignaciones de statements (que ya maneja ExpressionContext)
            self.v.stmts.visitAssignment(step_ctx)
        else:
            # Efectos colaterales (p.ej., f(), i++)
            self.v.visit(step_ctx)

        # Vida de temporales del “step”
        self.v.emitter.temp_pool.resetPerStatement()


    @logFunction(channel="tac")
    def visitForStatement(self, ctx: CompiscriptParser.ForStatementContext):
        # init
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

        # cond / step / body
        cond_ctx = safeAttr(ctx, "forCondition") or safeAttr(ctx, "cond") or safeAttr(ctx, "condition")
        step = safeAttr(ctx, "forStep") or safeAttr(ctx, "step") or safeAttr(ctx, "increment")
        body = safeAttr(ctx, "statement") or safeAttr(ctx, "body") or safeAttr(ctx, "block")

        # Heurística para gramáticas alternativas
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

        if init is not None:
            self.v.visit(init)

        l_start = self.v.emitter.newLabel("Lstart")
        l_body  = self.v.emitter.newLabel("Lbody")
        l_end   = self.v.emitter.newLabel("Lend")
        l_step  = self.v.emitter.newLabel("Lstep") if step is not None else l_start

        # 🔧 registrar si alguien usa 'continue' hacia el step
        self.loop_ctx_stack.append({"break": l_end, "continue": l_step, "has_continue": False})
        self.v.loop_depth += 1

        self.v.emitter.emitLabel(l_start)
        if cond_ctx is None:
            self.v.emitter.emitGoto(l_body)
        else:
            self.visitCond(cond_ctx, l_body, l_end)

        self.v.emitter.emitLabel(l_body)
        if body is not None:
            self.v.visit(body)

        if step is not None:
            # 🔧 sólo etiqueta si hay 'continue' real hacia el step
            if self.loop_ctx_stack[-1].get("has_continue"):
                self.v.emitter.emitLabel(l_step)
            self.emitForStep(step)

        self.v.emitter.emitGoto(l_start)
        self.v.emitter.emitLabel(l_end)
        self.v.emitter.clearFlowTermination()
        self.loop_ctx_stack.pop()
        self.v.loop_depth -= 1
        return {"terminated": False, "reason": None}

    # ---------------- switch ----------------

    @logFunction(channel="tac")
    def visitSwitchStatement(self, ctx):
        discr = firstSwitchDiscriminant(ctx)
        if discr is None:
            return {"terminated": False, "reason": None}

        discr_text = discr.getText()

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

        # fallback por gramáticas más laxas
        if not cases and default_stmts is None:
            exprs = []
            get_exprs = getattr(ctx, "expression", None)
            if callable(get_exprs):
                exprs = list(get_exprs() or [])
            if exprs:
                cases = [(e, []) for e in exprs]
            if hasDefaultClause(ctx):
                default_stmts = []

        l_end = self.v.emitter.newLabel("Lend")
        l_def = self.v.emitter.newLabel("Ldef") if default_stmts is not None else l_end
        l_cases = [self.v.emitter.newLabel("Lcase") for _ in cases]

        for (case_expr, _), l_case in zip(cases, l_cases):
            cond_text = f"{discr_text} == {case_expr.getText()}"
            self.v.emitter.emitIfGoto(cond_text, l_case)
        self.v.emitter.emitGoto(l_def)

        self.switch_ctx_stack.append({"break": l_end, "continue": l_end})

        for (_, st_list), l_case in zip(cases, l_cases):
            self.v.emitter.clearFlowTermination()
            self.v.emitter.emitLabel(l_case)
            for st in st_list:
                self.v.visit(st)

        if default_stmts is not None:
            self.v.emitter.clearFlowTermination()
            self.v.emitter.emitLabel(l_def)
            for st in default_stmts:
                self.v.visit(st)

        self.v.emitter.emitLabel(l_end)
        self.v.emitter.clearFlowTermination()
        self.switch_ctx_stack.pop()

        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None
        return {"terminated": False, "reason": None}

    # ---------------- break / continue ----------------

    @logFunction(channel="tac")
    def visitBreakStatement(self, ctx: CompiscriptParser.BreakStatementContext):
        target = None
        if self.loop_ctx_stack:
            target = self.loop_ctx_stack[-1]["break"]
        elif self.switch_ctx_stack:
            target = self.switch_ctx_stack[-1]["break"]

        if target is None:
            return {"terminated": False, "reason": None}

        self.v.emitter.emitGoto(target)
        self.v.emitter.markFlowTerminated()

        self.v.stmt_just_terminated = "break"
        self.v.stmt_just_terminator_node = ctx
        return {"terminated": True, "reason": "break"}

    @logFunction(channel="tac")
    def visitContinueStatement(self, ctx: CompiscriptParser.ContinueStatementContext):
        target = self.loop_ctx_stack[-1]["continue"] if self.loop_ctx_stack else None
        if target is None:
            return {"terminated": False, "reason": None}

        if self.loop_ctx_stack:
            self.loop_ctx_stack[-1]["has_continue"] = True

        self.v.emitter.emitGoto(target)
        self.v.emitter.markFlowTerminated()
        self.v.stmt_just_terminated = "continue"
        self.v.stmt_just_terminator_node = ctx
        return {"terminated": True, "reason": "continue"}
