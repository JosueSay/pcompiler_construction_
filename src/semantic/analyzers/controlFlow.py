from typing import Any
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import BoolType, ErrorType, ClassType
from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic, log_function


# -------------------------
# Utilidades generales
# -------------------------

@log_function
def as_list(x):
    log_semantic(f"[util] as_list({x})")
    if x is None:
        return []
    try:
        return list(x)
    except TypeError:
        return [x]


@log_function
def maybe_call(x: Any) -> Any:
    log_semantic(f"[util] maybe_call({x})")
    return x() if callable(x) else x


@log_function
def safe_attr(ctx: Any, name: str) -> Any:
    val = getattr(ctx, name, None)
    res = maybe_call(val)
    log_semantic(f"[util] safe_attr({name}) -> {res}")
    return res


@log_function
def first_expression(ctx) -> Any | None:
    e = safe_attr(ctx, "expression")
    if e is not None:
        log_semantic(f"[util] first_expression -> {e}")
        return e
    try:
        for i in range(ctx.getChildCount()):
            ch = ctx.getChild(i)
            if isinstance(ch, CompiscriptParser.ExpressionContext):
                log_semantic(f"[util] first_expression -> {ch}")
                return ch
            try:
                for j in range(ch.getChildCount()):
                    gd = ch.getChild(j)
                    if isinstance(gd, CompiscriptParser.ExpressionContext):
                        log_semantic(f"[util] first_expression -> {gd}")
                        return gd
            except Exception:
                continue
    except Exception:
        pass
    log_semantic("[util] first_expression -> None")
    return None


@log_function
def split_assignment_text(text: str) -> tuple[str | None, str | None]:
    log_semantic(f"[util] split_assignment_text('{text}')")
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
        log_semantic(f"[util] split_assignment_text -> lhs='{lhs}', rhs='{rhs}'")
        return (lhs or None, rhs or None)
    return None, None


@log_function
def is_assign_text(text: str) -> bool:
    res = text and '=' in text and ('==' not in text) and ('!=' not in text) and ('<=' not in text) and ('>=' not in text)
    log_semantic(f"[util] is_assign_text('{text}') -> {res}")
    return bool(res)


@log_function
def collect_stmt_or_block(ctx) -> list[Any]:
    log_semantic(f"[util] collect_stmt_or_block({ctx.getText()[:30]}...)")
    stmts = as_list(safe_attr(ctx, "statement"))
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
    log_semantic(f"[util] collect_stmt_or_block -> {len(out)} elementos encontrados")
    return out


@log_function
def first_switch_discriminant(ctx) -> Any | None:
    e = safe_attr(ctx, "expression")
    if e is None:
        res = first_expression(ctx)
        log_semantic(f"[util] first_switch_discriminant -> {res}")
        return res
    try:
        seq = list(e)
        if seq:
            log_semantic(f"[util] first_switch_discriminant -> {seq[0]}")
            return seq[0]
    except TypeError:
        pass
    res = first_expression(ctx)
    log_semantic(f"[util] first_switch_discriminant -> {res}")
    return res


@log_function
def has_default_clause(ctx) -> bool:
    DefaultCtx = getattr(CompiscriptParser, "DefaultClauseContext", None)
    try:
        for i in range(ctx.getChildCount()):
            ch = ctx.getChild(i)
            if DefaultCtx is not None and isinstance(ch, DefaultCtx):
                log_semantic(f"[util] has_default_clause -> True")
                return True
            if type(ch).__name__.lower().startswith("default") and type(ch).__name__.endswith("Context"):
                log_semantic(f"[util] has_default_clause -> True")
                return True
    except Exception:
        pass
    try:
        txt = ctx.getText()
        if "default" in txt:
            log_semantic(f"[util] has_default_clause -> True")
            return True
    except Exception:
        pass
    log_semantic(f"[util] has_default_clause -> False")
    return False

class ControlFlowAnalyzer:
    """
    Reglas semánticas + Emisión TAC para control de flujo:

    Semántica:
      - Condiciones de if/while/do-while/for deben ser boolean.
      - break/continue solo dentro de bucles (y break permitido en switch).
      - switch: tipos de los 'case' compatibles con el scrutinee.
      - Detección de terminación (if-else).

    TAC:
      - Corto-circuito en '&&' y '||' sin materializar booleanos.
      - Pilas de contexto para 'break' y 'continue'.
      - Etiquetas de flujo y saltos directos con condición textual.
    """

    def __init__(self, v):
        log_semantic("===== [controlFlow.py] Inicio =====")
        self.v = v
        # Para TAC
        self.loop_ctx_stack: list[dict[str, str]] = []
        self.switch_ctx_stack: list[dict[str, str]] = []

    # ---------- helpers semánticos ----------
    @log_function
    def typeOfSilent(self, expr_ctx):
        log_semantic(f"[controlFlow] typeOfSilent sobre: {expr_ctx}")
        if expr_ctx is None:
            log_semantic("[controlFlow] typeOfSilent -> ErrorType() por None")
            return ErrorType()
        old_barrier = self.v.emitter.flow_terminated
        self.v.emitter.flow_terminated = True
        try:
            t = self.v.visit(expr_ctx)
            log_semantic(f"[controlFlow] typeOfSilent -> {t}")
        finally:
            # restaurar y limpiar temporales de la sentencia de tipado
            self.v.emitter.flow_terminated = old_barrier
            self.v.emitter.temp_pool.resetPerStatement()
        return t

    @log_function
    def requireBoolean(self, cond_t, ctx, who: str):
        log_semantic(f"[controlFlow] requireBoolean para {who}, tipo detectado: {cond_t}")
        if isinstance(cond_t, ErrorType):
            return
        if not isinstance(cond_t, BoolType):
            self.v.appendErr(SemanticError(
                f"La condición de {who} debe ser boolean, no {cond_t}.",
                line=ctx.start.line, column=ctx.start.column))
            log_semantic(f"[controlFlow] requireBoolean -> ErrorType detectado")

    @log_function
    def sameType(self, a, b):
        log_semantic(f"[controlFlow] sameType comparando {a} y {b}")
        if isinstance(a, ErrorType) or isinstance(b, ErrorType):
            return True
        if type(a) is type(b):
            if isinstance(a, ClassType):
                res = a.name == b.name
                log_semantic(f"[controlFlow] sameType clase -> {res}")
                return res
            if hasattr(a, "elem_type") and hasattr(b, "elem_type"):
                res = self.sameType(a.elem_type, b.elem_type)
                log_semantic(f"[controlFlow] sameType elem_type -> {res}")
                return res
            return True
        return False

    @log_function
    def walk(self, node):
        try:
            for ch in node.getChildren():
                yield ch
                yield from self.walk(ch)
        except Exception:
            return

    @log_function
    def collectCaseExprs(self, ctx):
        log_semantic(f"[controlFlow] collectCaseExprs para {ctx}")
        exprs = []
        cb = getattr(ctx, "caseBlock", None)
        if callable(cb):
            cb = cb()
        if cb:
            caseClause = getattr(cb, "caseClause", None)
            if callable(caseClause):
                for c in as_list(caseClause()):
                    get_exprs = getattr(c, "expression", None)
                    if callable(get_exprs):
                        exprs.extend(as_list(get_exprs()))
        if not exprs:
            for n in self.walk(ctx):
                cname = n.__class__.__name__.lower()
                if "case" in cname:
                    get_exprs = getattr(n, "expression", None)
                    if callable(get_exprs):
                        exprs.extend(as_list(get_exprs()))
        log_semantic(f"[controlFlow] collectCaseExprs -> {len(exprs)} expresiones encontradas")
        return exprs
    
    @log_function
    def visitCond(self, expr_ctx, ltrue: str, lfalse: str) -> None:
        log_semantic(f"[controlFlow] visitCond sobre {expr_ctx} -> ltrue={ltrue}, lfalse={lfalse}")
        ctx_type = type(expr_ctx).__name__

        # --- Manejo robusto de '!' ---
        if ctx_type in ("UnaryExprContext", "UnaryExpressionContext"):
            op = getattr(expr_ctx, "op", None)
            if op and maybe_call(op).text == "!":
                inner = safe_attr(expr_ctx, "unaryExpr") or safe_attr(expr_ctx, "expression") or safe_attr(expr_ctx, "right")
                log_semantic("[controlFlow] visitCond: operador '!' detectado (op presente)")
                self.visitCond(inner, lfalse, ltrue)
                return
            # Caso extra: chequear hijos directos (ANTLR: '!' <expr>)
            try:
                if expr_ctx.getChildCount() >= 2 and expr_ctx.getChild(0).getText() == "!":
                    inner = expr_ctx.getChild(1)
                    log_semantic("[controlFlow] visitCond: operador '!' detectado (hijo directo)")
                    self.visitCond(inner, lfalse, ltrue)
                    return
            except Exception:
                pass

        # Fallback textual (cuando llega algo raro con texto "!...")
        try:
            cond_txt = expr_ctx.getText()
        except Exception:
            cond_txt = ""
        if cond_txt.startswith("!"):
            inner = safe_attr(expr_ctx, "unaryExpr") or safe_attr(expr_ctx, "expression")
            if inner is None:
                try:
                    inner = expr_ctx.getChild(1)  # después de '!' normalmente viene el inner
                except Exception:
                    inner = None
            if inner is not None:
                log_semantic("[controlFlow] visitCond: fallback textual '!' → intercambio de etiquetas")
                self.visitCond(inner, lfalse, ltrue)
                return

        # --- B1 || B2 ---
        if "LogicalOr" in ctx_type or getattr(expr_ctx, "op", None) and maybe_call(expr_ctx.op).text == "||":
            left = safe_attr(expr_ctx, "left") or safe_attr(expr_ctx, "expression") or safe_attr(expr_ctx, "lhs")
            right = safe_attr(expr_ctx, "right") or safe_attr(expr_ctx, "expression1") or safe_attr(expr_ctx, "rhs")
            lmid = self.v.emitter.newLabel("Lor")
            log_semantic("[controlFlow] visitCond: operador '||' detectado, creando label intermedio " + lmid)
            self.visitCond(left, ltrue, lmid)
            self.v.emitter.emitLabel(lmid)
            self.visitCond(right, ltrue, lfalse)
            return

        # --- B1 && B2 ---
        if "LogicalAnd" in ctx_type or getattr(expr_ctx, "op", None) and maybe_call(expr_ctx.op).text == "&&":
            left = safe_attr(expr_ctx, "left") or safe_attr(expr_ctx, "expression") or safe_attr(expr_ctx, "lhs")
            right = safe_attr(expr_ctx, "right") or safe_attr(expr_ctx, "expression1") or safe_attr(expr_ctx, "rhs")
            lmid = self.v.emitter.newLabel("Land")
            log_semantic("[controlFlow] visitCond: operador '&&' detectado, creando label intermedio " + lmid)
            self.visitCond(left, lmid, lfalse)
            self.v.emitter.emitLabel(lmid)
            self.visitCond(right, ltrue, lfalse)
            return

        # --- Relacionales/igualdad: emitir directo ---
        cond_text = expr_ctx.getText()
        log_semantic(f"[controlFlow] visitCond: expresión final -> emitIfGoto {cond_text} ? {ltrue} : {lfalse}")
        self.v.emitter.emitIfGoto(cond_text, ltrue)
        self.v.emitter.emitGoto(lfalse)


    # ---------- IF ----------
    @log_function
    def visitIfStatement(self, ctx: CompiscriptParser.IfStatementContext):
        log_semantic(f"[controlFlow] visitIfStatement: {ctx.getText()[:50]}...")

        # Semántica: tipo de condición (sin emitir)
        cond_ctx = first_expression(ctx)
        if cond_ctx is not None:
            ct = self.typeOfSilent(cond_ctx)
            self.requireBoolean(ct, ctx, "if")
        else:
            log_semantic("[if] no se encontró expresión de condición; se omite emisión.")
            return {"terminated": False, "reason": None}

        # TAC
        stmts = collect_stmt_or_block(ctx)
        then_stmt = stmts[0] if len(stmts) >= 1 else None
        else_stmt = stmts[1] if len(stmts) >= 2 else None

        if then_stmt is None:
            log_semantic("[if] no se encontró bloque 'then'.")
            return {"terminated": False, "reason": None}

        lthen = self.v.emitter.newLabel("Lthen")
        lend = self.v.emitter.newLabel("Lend")
        lelse = self.v.emitter.newLabel("Lelse") if else_stmt is not None else lend

        log_semantic(f"[if] etiquetas: then={lthen}, else={lelse}, end={lend}")
        self.visitCond(cond_ctx, lthen, lelse)

        # then
        self.v.emitter.emitLabel(lthen)
        then_result = self.v.visit(then_stmt) or {"terminated": False, "reason": None}

        # else (si existe)
        if else_stmt is not None:
            self.v.emitter.emitGoto(lend)
            self.v.emitter.emitLabel(lelse)
            if bool(then_result.get("terminated")):
                self.v.emitter.clearFlowTermination()
            else_result = self.v.visit(else_stmt) or {"terminated": False, "reason": None}
        else:
            else_result = {"terminated": False, "reason": None}

        self.v.emitter.emitLabel(lend)
        both_terminate = bool(then_result.get("terminated") and else_result.get("terminated"))

        if not both_terminate:
            self.v.emitter.clearFlowTermination()

        if both_terminate:
            self.v.stmt_just_terminated = "if-else"
            self.v.stmt_just_terminator_node = ctx
            log_semantic("[if] ambas ramas terminan -> marcado como 'terminated'")
            return {"terminated": True, "reason": "if-else"}

        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None
        log_semantic("[if] rama 'if' parcial -> no termina completamente")
        return {"terminated": False, "reason": None}

    # ---------- WHILE ----------
    @log_function
    def visitWhileStatement(self, ctx: CompiscriptParser.WhileStatementContext):
        log_semantic(f"[while] visitWhileStatement: {ctx.getText()[:50]}...")

        # Semántica (tipo de condición)
        cctx = safe_attr(ctx, "expression") or safe_attr(ctx, "cond") or safe_attr(ctx, "condition")
        if cctx is not None:
            cond_type = self.typeOfSilent(cctx)
            log_semantic(f"[while] tipo de condición: {cond_type}")
            self.requireBoolean(cond_type, ctx, "while")
        else:
            log_semantic("[while] no se encontró expresión de condición.")

        # TAC
        cond = cctx
        body = safe_attr(ctx, "statement") or safe_attr(ctx, "body") or safe_attr(ctx, "block")

        lstart = self.v.emitter.newLabel("Lstart")
        lbody = self.v.emitter.newLabel("Lbody")
        lend = self.v.emitter.newLabel("Lend")
        log_semantic(f"[while] etiquetas: start={lstart}, body={lbody}, end={lend}")

        # contexto de bucle
        self.loop_ctx_stack.append({"break": lend, "continue": lstart})
        self.v.loop_depth += 1
        log_semantic(f"[while] loop depth={self.v.loop_depth}, contexto stack actualizado")

        self.v.emitter.emitLabel(lstart)
        self.visitCond(cond, lbody, lend)

        self.v.emitter.emitLabel(lbody)
        self.v.visit(body)
        self.v.emitter.emitGoto(lstart)

        self.v.emitter.emitLabel(lend)
        self.v.emitter.clearFlowTermination()
        self.loop_ctx_stack.pop()
        self.v.loop_depth -= 1
        log_semantic(f"[while] bucle terminado, loop depth={self.v.loop_depth}")

        return {"terminated": False, "reason": None}

    # ---------- DO-WHILE ----------
    @log_function
    def visitDoWhileStatement(self, ctx: CompiscriptParser.DoWhileStatementContext):
        log_semantic(f"[do-while] visitDoWhileStatement: {ctx.getText()[:50]}...")

        body = safe_attr(ctx, "statement") or safe_attr(ctx, "body") or safe_attr(ctx, "block")
        cond = safe_attr(ctx, "expression") or safe_attr(ctx, "cond") or safe_attr(ctx, "condition")

        # Semántica (tipo de condición)
        if cond is not None:
            cond_type = self.typeOfSilent(cond)
            log_semantic(f"[do-while] tipo de condición: {cond_type}")
            self.requireBoolean(cond_type, ctx, "do-while")
        else:
            log_semantic("[do-while] no se encontró expresión de condición.")

        lbody = self.v.emitter.newLabel("Lbody")
        lcond = self.v.emitter.newLabel("Lcond")
        lend = self.v.emitter.newLabel("Lend")
        log_semantic(f"[do-while] etiquetas: body={lbody}, cond={lcond}, end={lend}")

        self.loop_ctx_stack.append({"break": lend, "continue": lcond})
        self.v.loop_depth += 1
        log_semantic(f"[do-while] loop depth={self.v.loop_depth}, contexto stack actualizado")

        self.v.emitter.emitLabel(lbody)
        self.v.visit(body)
        self.v.emitter.emitLabel(lcond)
        self.visitCond(cond, lbody, lend)

        self.v.emitter.emitLabel(lend)
        self.v.emitter.clearFlowTermination()
        self.loop_ctx_stack.pop()
        self.v.loop_depth -= 1
        log_semantic(f"[do-while] bucle terminado, loop depth={self.v.loop_depth}")

        return {"terminated": False, "reason": None}

    # ---------- FOR ----------
    @log_function
    def emitForStep(self, step_ctx):
        log_semantic(f"[for.step] visit emitForStep: {getattr(step_ctx, 'getText', lambda: '<None>')()}")
        try:
            if step_ctx is None:
                log_semantic("[for.step] step_ctx es None, nada que emitir.")
                return

            txt = step_ctx.getText()
            if not is_assign_text(txt):
                self.v.visit(step_ctx)
                log_semantic("[for.step] (no-assign) visit(expr) ejecutado")
                return

            lhs_node = getattr(step_ctx, "left", None) or getattr(step_ctx, "lhs", None)
            lhs_place = lhs_node.getText().strip() if lhs_node is not None else split_assignment_text(txt)[0]

            rhs_node = getattr(step_ctx, "right", None)
            if rhs_node is None:
                get_exprs = getattr(step_ctx, "expression", None)
                if callable(get_exprs):
                    exprs = list(get_exprs() or [])
                    if exprs:
                        rhs_node = exprs[-1]

            if rhs_node is None:
                for n in self.walk(step_ctx):
                    if isinstance(n, CompiscriptParser.ExpressionContext):
                        t = n.getText()
                        if t and '=' not in t:
                            rhs_node = n
                            break

            if rhs_node is None:
                _lhs_txt, rhs_text = split_assignment_text(txt)
                if lhs_place is None or rhs_text is None:
                    self.v.visit(step_ctx)
                    log_semantic("[for.step] fallback visit(expr) (no RHS detectado)")
                    return
                self.v.emitter.emitAssign(lhs_place, rhs_text)
                log_semantic(f"[for.step] fallback emit: {lhs_place} = {rhs_text}")
                return

            self.v.visit(rhs_node)
            rhs_place = getattr(rhs_node, "_place", rhs_node.getText().strip())
            self.v.emitter.emitAssign(lhs_place, rhs_place)
            log_semantic(f"[for.step] emit: {lhs_place} = {rhs_place}")

        except Exception as ex:
            log_semantic(f"[for.step] ERROR: {ex!r}")
            try:
                self.v.visit(step_ctx)
            except Exception:
                pass

    @log_function
    def visitForStatement(self, ctx: CompiscriptParser.ForStatementContext):
        log_semantic(f"[for] visitForStatement: {ctx.getText()[:50]}...")

        try:
            init = safe_attr(ctx, "forInit") or safe_attr(ctx, "init") or safe_attr(ctx, "initializer")
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

            cond = safe_attr(ctx, "forCondition") or safe_attr(ctx, "cond") or safe_attr(ctx, "condition")
            step = safe_attr(ctx, "forStep") or safe_attr(ctx, "step") or safe_attr(ctx, "increment")
            body = safe_attr(ctx, "statement") or safe_attr(ctx, "body") or safe_attr(ctx, "block")

            # Detectar expresiones del header
            exprs = []
            get_exprs = getattr(ctx, "expression", None)
            if callable(get_exprs):
                exprs = list(get_exprs() or [])

            assign_exprs = [e for e in exprs if is_assign_text(e.getText())]
            non_assign_exprs = [e for e in exprs if not is_assign_text(e.getText())]

            if cond is not None and is_assign_text(cond.getText()):
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

            # Semántica
            if cond is not None:
                cond_type = self.typeOfSilent(cond)
                log_semantic(f"[for] tipo de condición: {cond_type}")
                self.requireBoolean(cond_type, ctx, "for")

            cond_txt = cond.getText() if cond is not None else "<true>"
            step_txt = step.getText() if step is not None else "<none>"
            log_semantic(f"[for] header detectado: cond={cond_txt} | step={step_txt}")

            if init is not None:
                self.v.visit(init)  # soporta tanto decl como asignación en el header

            # TAC
            lstart = self.v.emitter.newLabel("Lstart")
            lbody = self.v.emitter.newLabel("Lbody")
            lend = self.v.emitter.newLabel("Lend")
            lstep = self.v.emitter.newLabel("Lstep") if step is not None else lstart
            log_semantic(f"[for] etiquetas: start={lstart}, body={lbody}, step={lstep}, end={lend}")

            self.loop_ctx_stack.append({"break": lend, "continue": lstep})
            self.v.loop_depth += 1
            log_semantic(f"[for] loop depth={self.v.loop_depth}, contexto stack actualizado")

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
            self.v.emitter.clearFlowTermination()
            self.loop_ctx_stack.pop()
            self.v.loop_depth -= 1
            log_semantic(f"[for] bucle terminado, loop depth={self.v.loop_depth}")

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

    # ---------- SWITCH ----------
    @log_function
    def visitSwitchStatement(self, ctx):
        log_semantic("[switch] visitSwitchStatement iniciado")

        # ---------- Semántica: validar tipos de 'case' contra el discriminante ----------
        discr = first_switch_discriminant(ctx)
        if discr is None:
            log_semantic("[switch] no se encontró expresión discriminante; se omite emisión.")
            return {"terminated": False, "reason": None}

        scrutinee_t = self.typeOfSilent(discr)
        log_semantic(f"[switch] tipo discriminante: {scrutinee_t}")

        for e in self.collectCaseExprs(ctx):
            et = self.typeOfSilent(e)
            log_semantic(f"[switch] tipo case detectado: {et}")
            if not isinstance(scrutinee_t, ErrorType) and not isinstance(et, ErrorType):
                if not self.sameType(scrutinee_t, et):
                    self.v.appendErr(SemanticError(
                        f"Tipo de 'case' ({et}) incompatible con el 'switch' ({scrutinee_t}).",
                        line=e.start.line, column=e.start.column))

        # ---------- TAC: preparar casos / default ----------
        discr_text = discr.getText()
        log_semantic(f"[switch] discriminante texto: {discr_text}")

        StmtCtx = getattr(CompiscriptParser, "StatementContext", None)
        ExprCtx = getattr(CompiscriptParser, "ExpressionContext", None)

        def gather_statements(node):
            """Devuelve lista de StatementContext dentro de node (búsqueda robusta)."""
            out = []
            if node is None:
                return out
            # API directa
            stmts = as_list(safe_attr(node, "statement"))
            if stmts:
                return stmts
            # Fallback: recorrido profundo
            try:
                for ch in self.walk(node):
                    if StmtCtx is not None and isinstance(ch, StmtCtx):
                        out.append(ch)
            except Exception:
                pass
            return out

        def first_child_expression(node):
            """Primera Expression dentro de node (para el 'case N:')."""
            if node is None:
                return None
            # API directa
            e = safe_attr(node, "expression")
            if e is not None:
                try:
                    seq = list(e)  # por si devuelve iterable
                    if seq:
                        return seq[0]
                except TypeError:
                    return e
            # Fallback
            try:
                for ch in self.walk(node):
                    if ExprCtx is not None and isinstance(ch, ExprCtx):
                        return ch
            except Exception:
                pass
            return None

        # === Camino específico a tu AST: hijos SwitchCase/DefaultCase de SwitchStatement ===
        cases: list[tuple[Any, list[Any]]] = []
        default_stmts: list[Any] | None = None

        # Itera hijos directos del switch buscando SwitchCase/DefaultCase
        for ch in getattr(ctx, "getChildren", lambda: [])():
            cname = type(ch).__name__
            if cname in ("SwitchCaseContext", "SwitchCase"):
                ce = first_child_expression(ch)
                if ce is None:
                    # seguridad: si falla, usa el discriminante (no se cumplirá jamás, pero no rompe índices)
                    log_semantic("[switch] WARNING: SwitchCase sin expresión; se usa fallback.")
                    ce = discr
                sts = gather_statements(ch)
                cases.append((ce, sts))
                log_semantic(f"[switch] caso agregado: {ce.getText()} con {len(sts)} statements")
            elif cname in ("DefaultCaseContext", "DefaultCase"):
                default_stmts = gather_statements(ch)
                log_semantic(f"[switch] default agregado con {len(default_stmts)} statements")

        # Si por alguna razón no se detectó nada, usa último fallback (exprs sin statements)
        if not cases and default_stmts is None:
            exprs = self.collectCaseExprs(ctx)
            if exprs:
                cases = [(e, []) for e in exprs]
            if has_default_clause(ctx):
                default_stmts = []
            log_semantic(f"[switch] fallback final: cases={len(cases)}, default={default_stmts is not None}")

        # ---------- Etiquetas y saltos ----------
        lend = self.v.emitter.newLabel("Lend")
        ldef = self.v.emitter.newLabel("Ldef") if default_stmts is not None else lend
        lcases = [self.v.emitter.newLabel("Lcase") for _ in cases]

        log_semantic(f"[switch] etiquetas generadas: lend={lend}, ldef={ldef}, lcases={lcases}")

        # Comparaciones: discr == caseExpr -> Lcase_i
        for (cexpr, _), lcase in zip(cases, lcases):
            cond_text = f"{discr_text} == {cexpr.getText()}"
            self.v.emitter.emitIfGoto(cond_text, lcase)
            log_semantic(f"[switch] emitIfGoto: {cond_text} -> {lcase}")
        self.v.emitter.emitGoto(ldef)
        log_semantic(f"[switch] emitGoto default/end: {ldef}")

        # Contexto para 'break' dentro del switch
        self.switch_ctx_stack.append({"break": lend, "continue": lend})
        log_semantic(f"[switch] contexto stack actualizado: break={lend}, continue={lend}")

        # Emitir cada case + sus statements (fall-through natural si no hay 'break')
        for (_, st_list), lcase in zip(cases, lcases):
            # Si la rama anterior terminó (p. ej. por 'break'), reabrimos el flujo
            self.v.emitter.clearFlowTermination()
            self.v.emitter.emitLabel(lcase)
            log_semantic(f"[switch] etiqueta caso emitida: {lcase}")
            for st in st_list:
                self.v.visit(st)


        # Default (si existe)
        if default_stmts is not None:
            # Reabrir flujo por si el último 'case' terminó
            self.v.emitter.clearFlowTermination()
            self.v.emitter.emitLabel(ldef)
            log_semantic(f"[switch] etiqueta default emitida: {ldef}")
            for st in default_stmts:
                self.v.visit(st)


        # Cierre
        self.v.emitter.emitLabel(lend)
        self.v.emitter.clearFlowTermination()
        self.switch_ctx_stack.pop()
        log_semantic("[switch] fin switch; etiquetas y contexto limpiados")

        # Limpiamos ese sello para que el bloque contenedor no crea que el flujo terminó aquí si hay un break en un case
        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None

        return {"terminated": False, "reason": None}



    # ---------- break / continue ----------
    @log_function
    def visitBreakStatement(self, ctx: CompiscriptParser.BreakStatementContext):
        log_semantic("[break] visitBreakStatement iniciado")
        target = None
        if self.loop_ctx_stack:
            target = self.loop_ctx_stack[-1]["break"]
        elif self.switch_ctx_stack:
            target = self.switch_ctx_stack[-1]["break"]

        if target is None:
            self.v.appendErr(SemanticError(
                "'break' fuera de un bucle o switch.",
                line=ctx.start.line, column=ctx.start.column))
            log_semantic("[break] ERROR: fuera de bucle o switch")
            return {"terminated": False, "reason": None}

        # TAC
        self.v.emitter.emitGoto(target)
        self.v.emitter.markFlowTerminated()
        log_semantic(f"[break] emitGoto a {target} y flujo marcado como terminado")

        # Marca terminación del flujo del bloque actual
        self.v.stmt_just_terminated = "break"
        self.v.stmt_just_terminator_node = ctx
        return {"terminated": True, "reason": "break"}

    @log_function
    def visitContinueStatement(self, ctx: CompiscriptParser.ContinueStatementContext):
        log_semantic("[continue] visitContinueStatement iniciado")
        target = self.loop_ctx_stack[-1]["continue"] if self.loop_ctx_stack else None
        if target is None:
            self.v.appendErr(SemanticError(
                "'continue' fuera de un bucle.",
                line=ctx.start.line, column=ctx.start.column))
            log_semantic("[continue] ERROR: fuera de bucle")
            return {"terminated": False, "reason": None}

        # TAC
        self.v.emitter.emitGoto(target)
        self.v.emitter.markFlowTerminated()
        log_semantic(f"[continue] emitGoto a {target} y flujo marcado como terminado")

        # Marca terminación del flujo del bloque actual
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
