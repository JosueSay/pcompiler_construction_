from antlr4.tree.Tree import TerminalNode
from typing import Any
from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger import log, logFunction
from utils.ast_utils import (
    walk, extractNotInner,
    asList, maybeCall, safeAttr, firstExpression,
    splitAssignmentText, isAssignText, collectStmtOrBlock,
    firstSwitchDiscriminant, hasDefaultClause, deepPlace
)


class TacControlFlow:
    """
    Control de flujo para la pasada TAC (sin validaciones semánticas).

    Supuestos:
      - La semántica ya resolvió tipos y símbolos.
      - `self.v` tiene:
        - emitter: primitivas TAC
        - visit(node): despache a sub-visitors
        - loop_depth: contador de anidamiento
        - stmt_just_terminated / stmt_just_terminator_node: barreras de flujo

    Stack internos:
      - loop_ctx_stack  : manejo de 'break'/'continue'
      - switch_ctx_stack: manejo de 'switch/case/default'
      - while_seq       : contador interno para while
    """

    
    def __init__(self, v):
        log("\n" + "="*80, channel="tac")
        log("[TAC_CONTROL_FLOW] Init TacControlFlow", channel="tac")
        log("="*80 + "\n", channel="tac")

        self.v = v
        self.loop_ctx_stack: list[dict[str, str]] = []
        self.switch_ctx_stack: list[dict[str, str]] = []
        self.while_seq: int = -1
        self.if_seq: int = -1

        log(f"[TAC_CONTROL_FLOW] loop_ctx_stack initialized: {self.loop_ctx_stack}", channel="tac")
        log(f"[TAC_CONTROL_FLOW] switch_ctx_stack initialized: {self.switch_ctx_stack}", channel="tac")
        log(f"[TAC_CONTROL_FLOW] while_seq initialized: {self.while_seq}\n", channel="tac")

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

    
    def visitCond(self, expr_ctx, l_true: str, l_false: str) -> None:
        """
        Emite TAC para condiciones con cortocircuito:

        Reglas:
          - !E        → invierte destinos
          - A || B .. → evalúa izquierda→derecha; si true salta a Ltrue
          - A && B .. → evalúa izquierda→derecha; si false salta a Lfalse
          - Base      → IF cond GOTO Ltrue ; GOTO Lfalse

        Args:
            expr_ctx : nodo ANTLR de la expresión
            l_true   : label de salto si la condición es verdadera
            l_false  : label de salto si la condición es falsa
        """
        # --- 0) Manejo de negación ---
        neg_inner = extractNotInner(expr_ctx)
        if neg_inner is not None:
            log(f"\n[TAC][Cond] Negation found, invert Ltrue/Lfalse -> {l_true}/{l_false}", channel="tac")
            self.visitCond(neg_inner, l_false, l_true)
            return

        node = self.unwrapCondCore(expr_ctx)

        # --- 1) OR ---
        OrCtx = getattr(CompiscriptParser, "LogicalOrExprContext", None)
        if OrCtx is not None and isinstance(node, OrCtx):
            and_terms = list(node.logicalAndExpr() or [])
            log(f"\n[TAC][Cond] OR condition: terms={len(and_terms)}, node={node.getText()}", channel="tac")

            if len(and_terms) <= 1:
                self.v.visit(node)
                p, _ = deepPlace(node)
                cond_place = p or node.getText()
                log(f"\t[TAC][Cond][OR] Single term -> IF {cond_place}>0 GOTO {l_true}; GOTO {l_false}", channel="tac")
                self.v.emitter.emitIfGoto(f"{cond_place} > 0", l_true)
                self.v.emitter.emitGoto(l_false)
                return

            # A || B || C ... → encadenar labels intermedios
            next_label = None
            for k, term in enumerate(and_terms):
                is_last = (k == len(and_terms) - 1)
                if is_last:
                    log(f"\t[TAC][Cond][OR] Last term -> Ltrue={l_true}, Lfalse={l_false}", channel="tac")
                    self.visitCond(term, l_true, l_false)
                else:
                    next_label = self.v.emitter.newLabel("Lor")
                    log(f"\t[TAC][Cond][OR] Intermediate term -> newLabel={next_label}", channel="tac")
                    self.visitCond(term, l_true, next_label)
                    self.v.emitter.emitLabel(next_label)
            return

        # --- 2) AND ---
        AndCtx = getattr(CompiscriptParser, "LogicalAndExprContext", None)
        if AndCtx is not None and isinstance(node, AndCtx):
            eq_terms = list(node.equalityExpr() or [])
            log(f"\n[TAC][Cond] AND condition: terms={len(eq_terms)}, node={node.getText()}", channel="tac")

            if len(eq_terms) <= 1:
                self.v.visit(node)
                p, _ = deepPlace(node)
                cond_place = p or node.getText()
                log(f"\t[TAC][Cond][AND] Single term -> IF {cond_place}>0 GOTO {l_true}; GOTO {l_false}", channel="tac")
                self.v.emitter.emitIfGoto(f"{cond_place} > 0", l_true)
                self.v.emitter.emitGoto(l_false)
                return

            # A && B && C ... → encadenar labels intermedios
            next_label = None
            for k, term in enumerate(eq_terms):
                is_last = (k == len(eq_terms) - 1)
                if is_last:
                    log(f"\t[TAC][Cond][AND] Last term -> Ltrue={l_true}, Lfalse={l_false}", channel="tac")
                    self.visitCond(term, l_true, l_false)
                else:
                    next_label = self.v.emitter.newLabel("Land")
                    log(f"\t[TAC][Cond][AND] Intermediate term -> newLabel={next_label}", channel="tac")
                    self.visitCond(term, next_label, l_false)
                    self.v.emitter.emitLabel(next_label)
            return

        # --- 3) Caso base ---
        self.v.visit(node)
        p, _ = deepPlace(node)
        cond_place = p or node.getText()
        log(f"\t[TAC][Cond][BASE] IF {cond_place}>0 GOTO {l_true}; GOTO {l_false}", channel="tac")
        self.v.emitter.emitIfGoto(f"{cond_place} > 0", l_true)
        self.v.emitter.emitGoto(l_false)

    # ---------------- if / else ----------------

    def visitIfStatement(self, ctx: CompiscriptParser.IfStatementContext):
        """
        Emite TAC para un if / else
        """
        cond_ctx = firstExpression(ctx)
        if cond_ctx is None:
            log("\t[TAC][if] No condition found, skipping", channel="tac")
            return {"terminated": False, "reason": None}

        stmts = collectStmtOrBlock(ctx)
        then_stmt = stmts[0] if len(stmts) >= 1 else None
        else_stmt = stmts[1] if len(stmts) >= 2 else None

        if then_stmt is None:
            log("\t[TAC][if] No then statement found, skipping", channel="tac")
            return {"terminated": False, "reason": None}

        # --- IDs y labels (formato del video) ---
        self.if_seq += 1
        iid = self.if_seq
        l_then = f"LABEL_TRUE_{iid}"
        l_end  = f"ENDIF_{iid}"
        l_else = f"LABEL_FALSE_{iid}" if else_stmt is not None else l_end

        log(f"\n[TAC][if] Labels -> then={l_then}, else={l_else}, end={l_end}", channel="tac")

        # --- Condición ---
        log(f"\t[TAC][if] Visiting condition -> {cond_ctx.getText()}", channel="tac")
        self.visitCond(cond_ctx, l_then, l_else)

        # --- Then block ---
        self.v.emitter.emitLabel(l_then)
        log(f"\t[TAC][if] Entering THEN block -> {l_then}", channel="tac")
        then_result = self.v.visit(then_stmt) or {"terminated": False, "reason": None}

        # --- Else block ---
        if else_stmt is not None:
            self.v.emitter.emitGoto(l_end)
            self.v.emitter.emitLabel(l_else)
            log(f"\t[TAC][if] Entering ELSE block -> {l_else}", channel="tac")
            if bool(then_result.get("terminated")):
                # si el THEN terminó (return/break/continue), limpiamos barrera para poder emitir el else
                self.v.emitter.clearFlowTermination()
            else_result = self.v.visit(else_stmt) or {"terminated": False, "reason": None}
        else:
            else_result = {"terminated": False, "reason": None}

        # --- End label ---
        self.v.emitter.emitLabel(l_end)
        log(f"\t[TAC][if] End IF/ELSE -> {l_end}", channel="tac")

        # --- Estado de terminación compuesto ---
        both_terminate = bool(then_result.get("terminated") and else_result.get("terminated"))
        if both_terminate:
            log(f"\t[TAC][if] Both THEN and ELSE blocks terminate", channel="tac")
            self.v.stmt_just_terminated = "if-else"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "if-else"}

        self.v.emitter.clearFlowTermination()
        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None
        return {"terminated": False, "reason": None}    


    # ---------------- while ----------------

    
    def visitWhileStatement(self, ctx: CompiscriptParser.WhileStatementContext):
        cond_ctx = safeAttr(ctx, "expression") or safeAttr(ctx, "cond") or safeAttr(ctx, "condition")
        body = safeAttr(ctx, "statement") or safeAttr(ctx, "body") or safeAttr(ctx, "block")

        self.while_seq += 1
        wid = self.while_seq
        l_start = f"STARTWHILE_{wid}"
        l_body  = f"LABEL_TRUE_{wid}"
        l_end   = f"ENDWHILE_{wid}"

        log(f"\n[TAC][while] Labels -> start={l_start}, body={l_body}, end={l_end}", channel="tac")

        self.loop_ctx_stack.append({"break": l_end, "continue": l_start})
        self.v.loop_depth += 1

        self.v.emitter.emitLabel(l_start)
        log(f"\t[TAC][while] Evaluating condition -> {cond_ctx.getText()}", channel="tac")
        self.visitCond(cond_ctx, l_body, l_end)

        self.v.emitter.emitLabel(l_body)
        log(f"\t[TAC][while] Entering body -> {l_body}", channel="tac")
        self.v.visit(body)
        self.v.emitter.emitGoto(l_start)

        self.v.emitter.emitLabel(l_end)
        log(f"\t[TAC][while] End loop -> {l_end}", channel="tac")
        self.v.emitter.clearFlowTermination()
        self.loop_ctx_stack.pop()
        self.v.loop_depth -= 1

        return {"terminated": False, "reason": None}

    # ---------------- do / while ----------------

    
    def visitDoWhileStatement(self, ctx: CompiscriptParser.DoWhileStatementContext):
        body = safeAttr(ctx, "statement") or safeAttr(ctx, "body") or safeAttr(ctx, "block")
        cond_ctx = safeAttr(ctx, "expression") or safeAttr(ctx, "cond") or safeAttr(ctx, "condition")

        l_body = self.v.emitter.newLabel("Lbody")
        l_cond = self.v.emitter.newLabel("Lcond")
        l_end = self.v.emitter.newLabel("Lend")

        log(f"\n[TAC][do] Labels -> body={l_body}, cond={l_cond}, end={l_end}", channel="tac")

        self.loop_ctx_stack.append({"break": l_end, "continue": l_cond})
        self.v.loop_depth += 1

        self.v.emitter.emitLabel(l_body)
        log(f"\t[TAC][do] Entering body -> {l_body}", channel="tac")
        self.v.visit(body)

        self.v.emitter.emitLabel(l_cond)
        log(f"\t[TAC][do] Evaluating condition -> {cond_ctx.getText()}", channel="tac")
        self.visitCond(cond_ctx, l_body, l_end)

        self.v.emitter.emitLabel(l_end)
        log(f"\t[TAC][do] End loop -> {l_end}", channel="tac")
        self.v.emitter.clearFlowTermination()
        self.loop_ctx_stack.pop()
        self.v.loop_depth -= 1

        return {"terminated": False, "reason": None}

    # ---------------- for ----------------

    
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
            log(f"\t[TAC][for] Emitting assignment-like step -> {step_ctx.getText()}", channel="tac")
            self.v.stmts.visitAssignment(step_ctx)
        else:
            log(f"\t[TAC][for] Emitting effect-only step -> {step_ctx.getText()}", channel="tac")
            self.v.visit(step_ctx)

        self.v.emitter.temp_pool.resetPerStatement()
        log(f"\t[TAC][for] Reset temporals for step", channel="tac")

    
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
            log(f"\t[TAC][for] Emitting init -> {init.getText()}", channel="tac")
            self.v.visit(init)

        l_start = self.v.emitter.newLabel("Lstart")
        l_body  = self.v.emitter.newLabel("Lbody")
        l_end   = self.v.emitter.newLabel("Lend")
        l_step  = self.v.emitter.newLabel("Lstep") if step is not None else l_start

        log(f"\n[TAC][for] Labels -> start={l_start}, body={l_body}, step={l_step}, end={l_end}", channel="tac")

        self.loop_ctx_stack.append({"break": l_end, "continue": l_step, "has_continue": False})
        self.v.loop_depth += 1

        self.v.emitter.emitLabel(l_start)
        if cond_ctx is None:
            log(f"\t[TAC][for] No condition, jumping to body -> {l_body}", channel="tac")
            self.v.emitter.emitGoto(l_body)
        else:
            log(f"\t[TAC][for] Evaluating condition -> {cond_ctx.getText()}", channel="tac")
            self.visitCond(cond_ctx, l_body, l_end)

        self.v.emitter.emitLabel(l_body)
        log(f"\t[TAC][for] Entering body -> {l_body}", channel="tac")
        if body is not None:
            self.v.visit(body)

        if step is not None:
            if self.loop_ctx_stack[-1].get("has_continue"):
                self.v.emitter.emitLabel(l_step)
            self.emitForStep(step)

        self.v.emitter.emitGoto(l_start)
        self.v.emitter.emitLabel(l_end)
        log(f"\t[TAC][for] End loop -> {l_end}", channel="tac")

        self.v.emitter.clearFlowTermination()
        self.loop_ctx_stack.pop()
        self.v.loop_depth -= 1
        return {"terminated": False, "reason": None}

    # ---------------- switch ----------------

    
    def visitSwitchStatement(self, ctx):
        discr = firstSwitchDiscriminant(ctx)
        if discr is None:
            return {"terminated": False, "reason": None}

        discr_text = discr.getText()
        log(f"\n[TAC][switch] Discriminant -> {discr_text}", channel="tac")

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

        log(f"\t[TAC][switch] Labels -> end={l_end}, default={l_def}, cases={[lbl for lbl in l_cases]}", channel="tac")

        for (case_expr, _), l_case in zip(cases, l_cases):
            cond_text = f"{discr_text} == {case_expr.getText()}"
            log(f"\t[TAC][switch] if {cond_text} goto {l_case}", channel="tac")
            self.v.emitter.emitIfGoto(cond_text, l_case)
        self.v.emitter.emitGoto(l_def)

        self.switch_ctx_stack.append({"break": l_end, "continue": l_end})

        for (_, st_list), l_case in zip(cases, l_cases):
            self.v.emitter.clearFlowTermination()
            self.v.emitter.emitLabel(l_case)
            log(f"\t[TAC][switch] Entering case -> {l_case}", channel="tac")
            for st in st_list:
                self.v.visit(st)

        if default_stmts is not None:
            self.v.emitter.clearFlowTermination()
            self.v.emitter.emitLabel(l_def)
            log(f"\t[TAC][switch] Entering default -> {l_def}", channel="tac")
            for st in default_stmts:
                self.v.visit(st)

        self.v.emitter.emitLabel(l_end)
        log(f"\t[TAC][switch] End switch -> {l_end}", channel="tac")
        self.v.emitter.clearFlowTermination()
        self.switch_ctx_stack.pop()

        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None
        return {"terminated": False, "reason": None}

    # ---------------- break / continue ----------------

    
    def visitBreakStatement(self, ctx: CompiscriptParser.BreakStatementContext):
        target = None
        if self.loop_ctx_stack:
            target = self.loop_ctx_stack[-1]["break"]
        elif self.switch_ctx_stack:
            target = self.switch_ctx_stack[-1]["break"]

        if target is None:
            return {"terminated": False, "reason": None}

        log(f"\t[TAC][break] Jump to {target}", channel="tac")
        self.v.emitter.emitGoto(target)
        self.v.emitter.markFlowTerminated()

        self.v.stmt_just_terminated = "break"
        self.v.stmt_just_terminator_node = ctx
        return {"terminated": True, "reason": "break"}

    
    def visitContinueStatement(self, ctx: CompiscriptParser.ContinueStatementContext):
        target = self.loop_ctx_stack[-1]["continue"] if self.loop_ctx_stack else None
        if target is None:
            return {"terminated": False, "reason": None}

        if self.loop_ctx_stack:
            self.loop_ctx_stack[-1]["has_continue"] = True

        log(f"\t[TAC][continue] Jump to {target}", channel="tac")
        self.v.emitter.emitGoto(target)
        self.v.emitter.markFlowTerminated()
        self.v.stmt_just_terminated = "continue"
        self.v.stmt_just_terminator_node = ctx
        return {"terminated": True, "reason": "continue"}
