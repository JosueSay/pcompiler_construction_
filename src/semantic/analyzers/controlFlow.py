from typing import Any
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

def maybeCall(x: Any) -> Any:
    """Devuelve x() si es callable; si no, x."""
    return x() if callable(x) else x

def safeAttr(ctx: Any, name: str) -> Any:
    """getattr seguro (devuelve None si no existe) y evalúa si es callable."""
    val = getattr(ctx, name, None)
    return maybeCall(val)

def firstExpression(ctx) -> Any | None:
    """
    Devuelve la primera ExpressionContext visible bajo ctx.
    Soporta ctx.expression() y, si no existe, recorre descendientes.
    """
    e = safeAttr(ctx, "expression")
    if e is not None:
        return e
    try:
        for i in range(ctx.getChildCount()):
            ch = ctx.getChild(i)
            if isinstance(ch, CompiscriptParser.ExpressionContext):
                return ch
            try:
                for j in range(ch.getChildCount()):
                    gd = ch.getChild(j)
                    if isinstance(gd, CompiscriptParser.ExpressionContext):
                        return gd
            except Exception:
                continue
    except Exception:
        return None
    return None

def splitAssignmentText(text: str) -> tuple[str | None, str | None]:
    """
    Separa 'LHS = RHS' evitando confundir '==', '!=', '<=', '>='.
    Retorna (lhs, rhs) o (None, None) si no detecta asignación simple.
    """
    if not text:
        return None, None
    for i, ch in enumerate(text):
        if ch != '=':
            continue
        prevc = text[i - 1] if i > 0 else ''
        nextc = text[i + 1] if i + 1 < len(text) else ''
        if prevc in ('=', '!', '<', '>') or nextc == '=':
            continue
        lhs = text[:i].strip()
        rhs = text[i + 1:].strip()
        return (lhs or None, rhs or None)
    return None, None

def isAssignText(text: str) -> bool:
    """True si contiene una '=' simple que no es parte de comparaciones."""
    if not text or '=' not in text:
        return False
    return ('==' not in text) and ('!=' not in text) and ('<=' not in text) and ('>=' not in text)

def collectStmtOrBlock(ctx) -> list[Any]:
    """
    Devuelve los hijos que sean StatementContext o BlockContext.
    1) ctx.statement() si existe
    2) Recorrido por hijos (StatementContext / BlockContext)
    """
    stmts = asList(safeAttr(ctx, "statement"))
    if stmts:
        return stmts

    out: list[Any] = []
    BlockCtx = getattr(CompiscriptParser, "BlockContext", None)
    try:
        for i in range(ctx.getChildCount()):
            ch = ctx.getChild(i)
            if isinstance(ch, CompiscriptParser.StatementContext):
                out.append(ch)
            elif BlockCtx is not None and isinstance(ch, BlockCtx):
                out.append(ch)
            elif type(ch).__name__.endswith("BlockContext"):
                out.append(ch)
    except Exception:
        pass
    return out

def firstSwitchDiscriminant(ctx) -> Any | None:
    """
    Obtiene la expresión del 'switch(<expr>)' evitando recoger expresiones de 'case'.
    Preferencia:
      1) primer elemento de ctx.expression() si es iterable
      2) ctx.expression() si es único
      3) fallback: firstExpression(ctx)
    """
    e = safeAttr(ctx, "expression")
    if e is None:
        return firstExpression(ctx)
    try:
        seq = list(e)
        if seq:
            return seq[0]
    except TypeError:
        return e
    return firstExpression(ctx)

def hasDefaultClause(ctx) -> bool:
    """
    True si hay 'default' (DefaultClauseContext o token 'default') en el subárbol.
    """
    DefaultCtx = getattr(CompiscriptParser, "DefaultClauseContext", None)
    try:
        for i in range(ctx.getChildCount()):
            ch = ctx.getChild(i)
            if DefaultCtx is not None and isinstance(ch, DefaultCtx):
                return True
            if type(ch).__name__.lower().startswith("default") and type(ch).__name__.endswith("Context"):
                return True
    except Exception:
        pass
    try:
        txt = ctx.getText()
        if "default" in txt:
            return True
    except Exception:
        pass
    return False


class ControlFlowAnalyzer:
    """
    Emisión TAC para estructuras de control de flujo:
    - Corto-circuito en '&&' y '||' sin materializar booleanos.
    - Pilas de contexto para 'break' y 'continue'.
    """

    def __init__(self, v):
        self.v = v
        self.loop_ctx_stack: list[dict[str, str]] = []
        self.switch_ctx_stack: list[dict[str, str]] = []

    # ---------- utilidades semánticas ----------
    def requireBoolean(self, cond_t, ctx, who: str):
        if isinstance(cond_t, ErrorType):
            return
        if not isinstance(cond_t, BoolType):
            self.v.appendErr(SemanticError(
                f"La condición de {who} debe ser boolean, no {cond_t}.",
                line=ctx.start.line, column=ctx.start.column))

    def sameType(self, a, b):
        if isinstance(a, ErrorType) or isinstance(b, ErrorType):
            return True
        if type(a) is type(b):
            if isinstance(a, ClassType):
                return a.name == b.name
            if hasattr(a, "elem_type") and hasattr(b, "elem_type"):
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

    # ---------- corto-circuito ----------
    def visitCond(self, expr_ctx, ltrue: str, lfalse: str) -> None:
        ctx_type = type(expr_ctx).__name__

        # !B
        if ctx_type in ("UnaryExprContext", "UnaryExpressionContext"):
            op = getattr(expr_ctx, "op", None)
            if op and maybeCall(op).text == "!":
                inner = safeAttr(expr_ctx, "unaryExpr") or safeAttr(expr_ctx, "expression") or safeAttr(expr_ctx, "right")
                self.visitCond(inner, lfalse, ltrue)
                return

        # B1 || B2
        if "LogicalOr" in ctx_type or getattr(expr_ctx, "op", None) and maybeCall(expr_ctx.op).text == "||":
            left = safeAttr(expr_ctx, "left") or safeAttr(expr_ctx, "expression") or safeAttr(expr_ctx, "lhs")
            right = safeAttr(expr_ctx, "right") or safeAttr(expr_ctx, "expression1") or safeAttr(expr_ctx, "rhs")
            lmid = self.v.emitter.newLabel("Lor")
            self.visitCond(left, ltrue, lmid)
            self.v.emitter.emitLabel(lmid)
            self.visitCond(right, ltrue, lfalse)
            return

        # B1 && B2
        if "LogicalAnd" in ctx_type or getattr(expr_ctx, "op", None) and maybeCall(expr_ctx.op).text == "&&":
            left = safeAttr(expr_ctx, "left") or safeAttr(expr_ctx, "expression") or safeAttr(expr_ctx, "lhs")
            right = safeAttr(expr_ctx, "right") or safeAttr(expr_ctx, "expression1") or safeAttr(expr_ctx, "rhs")
            lmid = self.v.emitter.newLabel("Land")
            self.visitCond(left, lmid, lfalse)
            self.v.emitter.emitLabel(lmid)
            self.visitCond(right, ltrue, lfalse)
            return

        # Relacionales/igualdad: emitir sobre el texto
        cond_text = expr_ctx.getText()
        self.v.emitter.emitIfGoto(cond_text, ltrue)
        self.v.emitter.emitGoto(lfalse)

    # ---------- if ----------
    def visitIfStatement(self, ctx: CompiscriptParser.IfStatementContext):
        cond = firstExpression(ctx)
        if cond is None:
            log_semantic("[if] no se encontró expresión de condición; se omite emisión.")
            return {"terminated": False, "reason": None}

        stmts = collectStmtOrBlock(ctx)
        then_stmt = stmts[0] if len(stmts) >= 1 else None
        else_stmt = stmts[1] if len(stmts) >= 2 else None

        if then_stmt is None:
            log_semantic("[if] no se encontró bloque 'then'.")
            return {"terminated": False, "reason": None}

        lthen = self.v.emitter.newLabel("Lthen")
        lend = self.v.emitter.newLabel("Lend")
        lelse = self.v.emitter.newLabel("Lelse") if else_stmt is not None else lend

        self.visitCond(cond, lthen, lelse)

        self.v.emitter.emitLabel(lthen)
        self.v.visit(then_stmt)

        if else_stmt is not None:
            self.v.emitter.emitGoto(lend)
            self.v.emitter.emitLabel(lelse)
            self.v.visit(else_stmt)

        self.v.emitter.emitLabel(lend)
        return {"terminated": False, "reason": None}

    # ---------- while ----------
    def visitWhileStatement(self, ctx: CompiscriptParser.WhileStatementContext):
        cond = safeAttr(ctx, "expression") or safeAttr(ctx, "cond") or safeAttr(ctx, "condition")
        body = safeAttr(ctx, "statement") or safeAttr(ctx, "body") or safeAttr(ctx, "block")

        lstart = self.v.emitter.newLabel("Lstart")
        lbody = self.v.emitter.newLabel("Lbody")
        lend = self.v.emitter.newLabel("Lend")

        self.loop_ctx_stack.append({"break": lend, "continue": lstart})

        self.v.emitter.emitLabel(lstart)
        self.visitCond(cond, lbody, lend)

        self.v.emitter.emitLabel(lbody)
        self.v.visit(body)
        self.v.emitter.emitGoto(lstart)

        self.v.emitter.emitLabel(lend)
        self.loop_ctx_stack.pop()
        return {"terminated": False, "reason": None}

    # ---------- do-while ----------
    def visitDoWhileStatement(self, ctx: CompiscriptParser.DoWhileStatementContext):
        body = safeAttr(ctx, "statement") or safeAttr(ctx, "body") or safeAttr(ctx, "block")
        cond = safeAttr(ctx, "expression") or safeAttr(ctx, "cond") or safeAttr(ctx, "condition")

        lbody = self.v.emitter.newLabel("Lbody")
        lcond = self.v.emitter.newLabel("Lcond")
        lend = self.v.emitter.newLabel("Lend")

        self.loop_ctx_stack.append({"break": lend, "continue": lcond})

        self.v.emitter.emitLabel(lbody)
        self.v.visit(body)
        self.v.emitter.emitLabel(lcond)
        self.visitCond(cond, lbody, lend)

        self.v.emitter.emitLabel(lend)
        self.loop_ctx_stack.pop()
        return {"terminated": False, "reason": None}

    # ---------- for ----------
    def emitForStep(self, step_ctx):
        """
        Emite el 'step' del for:
         - Si es asignación:  LHS = <place(RHS)>
         - Si no lo es:       visita por efectos colaterales.
        """
        try:
            if step_ctx is None:
                return

            txt = step_ctx.getText()
            if not isAssignText(txt):
                self.v.visit(step_ctx)
                log_semantic("[for.step] (no-assign) visit(expr)")
                return

            lhs_node = getattr(step_ctx, "left", None) or getattr(step_ctx, "lhs", None)
            if lhs_node is not None:
                lhs_place = lhs_node.getText().strip()
            else:
                lhs_place, _rhs_text = splitAssignmentText(txt)

            rhs_node = getattr(step_ctx, "right", None)
            if rhs_node is None:
                get_exprs = getattr(step_ctx, "expression", None)
                if callable(get_exprs):
                    exprs = list(get_exprs() or [])
                    if exprs:
                        rhs_node = exprs[-1]

            if rhs_node is None:
                try:
                    for n in self.walk(step_ctx):
                        if isinstance(n, CompiscriptParser.ExpressionContext):
                            t = n.getText()
                            if t and '=' not in t:
                                rhs_node = n
                except Exception:
                    rhs_node = None

            if rhs_node is None:
                _lhs_txt, rhs_text = splitAssignmentText(txt)
                if lhs_place is None or rhs_text is None:
                    self.v.visit(step_ctx)
                    log_semantic("[for.step] fallback visit(expr) (no structured RHS)")
                    return
                self.v.emitter.emitAssign(lhs_place, rhs_text)
                log_semantic(f"[for.step] fallback textual emit: {lhs_place} = {rhs_text}")
                return

            self.v.visit(rhs_node)
            rhs_place = getattr(rhs_node, "_place", rhs_node.getText().strip())

            if lhs_place is None:
                lhs_place, _ = splitAssignmentText(txt)
            if lhs_place is None:
                log_semantic("[for.step] WARNING: LHS no detectable; solo se materializó RHS.")
                return

            self.v.emitter.emitAssign(lhs_place, rhs_place)
            log_semantic(f"[for.step] emit: {lhs_place} = {rhs_place}")

        except Exception as ex:
            log_semantic(f"[for.step] ERROR: {ex!r}")
            try:
                self.v.visit(step_ctx)
            except Exception:
                pass

    def visitForStatement(self, ctx: CompiscriptParser.ForStatementContext):
        """
        for (init; cond; step) S
        - Si 'cond' falta o parece asignación → true.
        - 'continue' → Lstep (o Lstart si no hay step).
        """
        try:
            init = safeAttr(ctx, "forInit") or safeAttr(ctx, "init") or safeAttr(ctx, "initializer")
            cond = safeAttr(ctx, "forCondition") or safeAttr(ctx, "cond") or safeAttr(ctx, "condition")
            step = safeAttr(ctx, "forStep") or safeAttr(ctx, "step") or safeAttr(ctx, "increment")
            body = safeAttr(ctx, "statement") or safeAttr(ctx, "body") or safeAttr(ctx, "block")

            exprs = []
            get_exprs = getattr(ctx, "expression", None)
            if callable(get_exprs):
                exprs = list(get_exprs() or [])

            assign_exprs = [e for e in exprs if isAssignText(e.getText())]
            non_assign_exprs = [e for e in exprs if not isAssignText(e.getText())]

            if cond is not None and isAssignText(cond.getText()):
                cond = None
            if cond is None and non_assign_exprs:
                cond = non_assign_exprs[-1]

            if step is None and assign_exprs:
                step = assign_exprs[-1]

            if cond is not None and step is not None and cond.getText() == step.getText():
                replaced = False
                for e in reversed(non_assign_exprs):
                    if e.getText() != step.getText():
                        cond = e
                        replaced = True
                        break
                if not replaced:
                    cond = None

            cond_txt = cond.getText() if cond is not None else "<true>"
            step_txt = step.getText() if step is not None else "<none>"
            log_semantic(f"[for] header detectado: cond={cond_txt} | step={step_txt}")

            if init is not None:
                self.v.visit(init)

            lstart = self.v.emitter.newLabel("Lstart")
            lbody = self.v.emitter.newLabel("Lbody")
            lend = self.v.emitter.newLabel("Lend")
            lstep = self.v.emitter.newLabel("Lstep") if step is not None else lstart

            self.loop_ctx_stack.append({"break": lend, "continue": lstep})

            self.v.emitter.emitLabel(lstart)
            if cond is None:
                self.v.emitter.emitGoto(lbody)
            else:
                self.visitCond(cond, lbody, lend)

            self.v.emitter.emitLabel(lbody)
            if body is not None:
                self.v.visit(body)

            if step is not None:
                self.v.emitter.emitLabel(lstep)
                self.emitForStep(step)

            self.v.emitter.emitGoto(lstart)
            self.v.emitter.emitLabel(lend)
            self.loop_ctx_stack.pop()
            return {"terminated": False, "reason": None}

        except Exception as ex:
            log_semantic(f"[for] ERROR visitForStatement: {ex!r}")
            try:
                if init is not None: self.v.visit(init)
                if body is not None: self.v.visit(body)
                if step is not None: self.emitForStep(step)
            except Exception:
                pass
            return {"terminated": False, "reason": "error"}

    # ---------- switch ----------
    def visitSwitchStatement(self, ctx):
        expr = firstSwitchDiscriminant(ctx)
        if expr is None:
            log_semantic("[switch] no se encontró expresión discriminante; se omite emisión.")
            return {"terminated": False, "reason": None}
        discr_text = expr.getText()

        case_block = safeAttr(ctx, "caseBlock") or safeAttr(ctx, "cases") or safeAttr(ctx, "switchBlock")
        cases: list[tuple[Any, list[Any]]] = []
        default_stmts: list[Any] | None = None
        recogio_estructurado = False

        if case_block is not None:
            case_clauses = asList(safeAttr(case_block, "caseClause"))
            if case_clauses:
                recogio_estructurado = True
                for cc in case_clauses:
                    ce = safeAttr(cc, "expression") or safeAttr(cc, "caseExpr") or safeAttr(cc, "constExpr")
                    sts = asList(safeAttr(cc, "statement")) or asList(safeAttr(cc, "statements"))
                    cases.append((ce, sts))

            dcl = safeAttr(case_block, "defaultClause")
            if dcl is not None:
                recogio_estructurado = True
                default_stmts = asList(safeAttr(dcl, "statement")) or asList(safeAttr(dcl, "statements"))

        if not recogio_estructurado:
            case_exprs = self.collectCaseExprs(ctx)
            if not case_exprs and not hasDefaultClause(ctx):
                log_semantic("[switch] aviso: no se detectaron 'case' ni 'default'; no se emite TAC.")
                return {"terminated": False, "reason": None}
            cases = [(e, []) for e in case_exprs]
            default_stmts = [] if hasDefaultClause(ctx) else None

        lend = self.v.emitter.newLabel("Lend")
        ldef = self.v.emitter.newLabel("Ldef") if default_stmts is not None else lend
        lcases = [self.v.emitter.newLabel("Lcase") for _ in cases]

        for (cexpr, _), lcase in zip(cases, lcases):
            cond_text = f"{discr_text} == {cexpr.getText()}"
            self.v.emitter.emitIfGoto(cond_text, lcase)
        self.v.emitter.emitGoto(ldef)

        self.switch_ctx_stack.append({"break": lend, "continue": lend})

        for (_, st_list), lcase in zip(cases, lcases):
            self.v.emitter.emitLabel(lcase)
            for st in st_list:
                self.v.visit(st)

        if default_stmts is not None:
            self.v.emitter.emitLabel(ldef)
            for st in default_stmts:
                self.v.visit(st)

        self.v.emitter.emitLabel(lend)
        self.switch_ctx_stack.pop()
        return {"terminated": False, "reason": None}

    # ---------- break / continue ----------
    def visitBreakStatement(self, ctx: CompiscriptParser.BreakStatementContext):
        target = None
        if self.loop_ctx_stack:
            target = self.loop_ctx_stack[-1]["break"]
        elif self.switch_ctx_stack:
            target = self.switch_ctx_stack[-1]["break"]

        if target is None:
            log_semantic("[break] fuera de bucle/switch (se asume ya reportado por semántica).")
            return {"terminated": False, "reason": None}

        self.v.emitter.emitGoto(target)
        self.v.stmt_just_terminated = "break"
        self.v.stmt_just_terminator_node = ctx
        return {"terminated": True, "reason": "break"}

    def visitContinueStatement(self, ctx: CompiscriptParser.ContinueStatementContext):
        target = self.loop_ctx_stack[-1]["continue"] if self.loop_ctx_stack else None
        if target is None:
            log_semantic("[continue] fuera de bucle (se asume ya reportado por semántica).")
            return {"terminated": False, "reason": None}

        self.v.emitter.emitGoto(target)
        self.v.stmt_just_terminated = "continue"
        self.v.stmt_just_terminator_node = ctx
        return {"terminated": True, "reason": "continue"}

    # ------ alias opcionales ------
    def visitIf(self, ctx): return self.visitIfStatement(ctx)
    def visitWhile(self, ctx): return self.visitWhileStatement(ctx)
    def visitDoWhile(self, ctx): return self.visitDoWhileStatement(ctx)
    def visitFor(self, ctx): return self.visitForStatement(ctx)
    def visitSwitch(self, ctx): return self.visitSwitchStatement(ctx)
    def visitCaseStatement(self, ctx): return self.visitSwitchStatement(ctx)
    def visitBreak(self, ctx): return self.visitBreakStatement(ctx)
    def visitContinue(self, ctx): return self.visitContinueStatement(ctx)
