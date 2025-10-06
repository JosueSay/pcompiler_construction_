from antlr4.tree.Tree import TerminalNode
from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger import log, logFunction
from utils.ast_utils import deepPlace, isAssignText
from ir.tac import Op
from ir.addr_format import place_of_symbol


class TacStatements:
    """
    TAC puro para sentencias:
      - Declaraciones con inicializador.
      - Asignaciones (id=expr, a[i]=expr, obj.prop=expr, obj.chain[i]=expr).
      - Sentencias de expresión (por efectos).
    Sin validaciones semánticas: eso ya ocurrió antes.
    """

    @logFunction(channel="tac")
    def __init__(self, v):
        log("[tac_statements] init", channel="tac")
        self.v = v

    # ---------- helpers AST ----------
    @logFunction(channel="tac")
    def findDesc(self, node, klass):
        try:
            for ch in node.getChildren():
                if isinstance(ch, klass):
                    return ch
                sub = self.findDesc(ch, klass)
                if sub is not None:
                    return sub
        except Exception:
            return None
        return None

    @logFunction(channel="tac")
    def expressionsFromCTX(self, ctx):
        try:
            exprs = ctx.getRuleContexts(CompiscriptParser.ExpressionContext)
            if exprs:
                return list(exprs)
        except Exception:
            pass
        try:
            raw = ctx.expression()
            if raw is None:
                return []
            if isinstance(raw, (list, tuple)):
                return list(raw)
            return [raw]
        except Exception:
            pass
        res = []
        try:
            for ch in ctx.getChildren():
                if isinstance(ch, CompiscriptParser.ExpressionContext):
                    res.append(ch)
        except Exception:
            pass
        return res

    @logFunction(channel="tac")
    def rhsOfAssignExpr(self, expr_ctx):
        try:
            assign = self.findDesc(expr_ctx, CompiscriptParser.AssignExprContext)
            if assign is not None:
                try:
                    rhs = assign.exprNoAssign()
                    if isinstance(rhs, (list, tuple)):
                        rhs = rhs[-1] if rhs else None
                except Exception:
                    rhs = None
                if rhs is not None:
                    return rhs

                n = assign.getChildCount()
                saw_eq = False
                for i in range(n):
                    ch = assign.getChild(i)
                    if isinstance(ch, TerminalNode) and ch.getText() == '=':
                        saw_eq = True
                        continue
                    if saw_eq and (isinstance(ch, CompiscriptParser.ExprNoAssignContext) or
                                   isinstance(ch, CompiscriptParser.ExpressionContext)):
                        return ch
        except Exception:
            pass

        try:
            n = expr_ctx.getChildCount()
            kids = [expr_ctx.getChild(i) for i in range(n)]
            saw_eq = False
            for ch in kids:
                if isinstance(ch, TerminalNode) and ch.getText() == '=':
                    saw_eq = True
                    continue
                if saw_eq and (isinstance(ch, CompiscriptParser.ExprNoAssignContext) or
                               isinstance(ch, CompiscriptParser.ExpressionContext)):
                    return ch
        except Exception:
            pass
        return None

    @logFunction(channel="tac")
    def matchSimpleIndexAssign(self, lhs_or_expr_node):
        lhs_ctx = self.findDesc(lhs_or_expr_node, CompiscriptParser.LeftHandSideContext)
        if lhs_ctx is None:
            return None
        try:
            lhs_txt = lhs_ctx.getText()
        except Exception:
            return None
        brk = lhs_txt.find('[')
        if brk <= 0:
            return None
        base_txt = lhs_txt[:brk]
        if base_txt == 'this' or '.' in base_txt:
            return None
        idx_node = self.findDesc(lhs_ctx, CompiscriptParser.IndexExprContext)
        if idx_node is None:
            return None
        return (base_txt, idx_node)

    @logFunction(channel="tac")
    def matchPropertyIndexAssign(self, lhs_or_expr_node):
        lhs_ctx = self.findDesc(lhs_or_expr_node, CompiscriptParser.LeftHandSideContext)
        if lhs_ctx is None:
            return None
        try:
            lhs_txt = lhs_ctx.getText()
        except Exception:
            return None
        brk = lhs_txt.find('[')
        if brk <= 0:
            return None
        base_txt = lhs_txt[:brk]
        if '.' not in base_txt:
            return None
        parts = base_txt.split('.')
        if len(parts) < 2:
            return None
        obj_txt = parts[0]
        prop_chain = parts[1:]
        idx_node = self.findDesc(lhs_ctx, CompiscriptParser.IndexExprContext)
        if idx_node is None:
            return None
        return (obj_txt, prop_chain, idx_node)

    # ----------------------------------
    # Sentencia de expresión
    # ----------------------------------
    @logFunction(channel="tac")
    def visitExpressionStatement(self, ctx):
        if getattr(self.v.emitter, "flow_terminated", False):
            return None
        get_asgn = getattr(ctx, "assignment", None)
        if callable(get_asgn):
            asg = get_asgn()
            if asg is not None:
                self.visitAssignment(asg)
                self.v.emitter.temp_pool.resetPerStatement()
                return None

        expr = ctx.expression()
        txt = getattr(expr, "getText", lambda: "")()
        is_assign = isAssignText(txt) or isAssignText(getattr(ctx, "getText", lambda: "")())

        if is_assign:
            m = self.matchSimpleIndexAssign(expr)
            if m is not None:
                base_name, idx_node = m
                rhs_node = self.rhsOfAssignExpr(expr)
                if rhs_node is not None:
                    # idx
                    self.v.visit(idx_node.expression() if hasattr(idx_node, "expression") else idx_node)
                    p_idx, it_idx = deepPlace(idx_node if not hasattr(idx_node, "expression") else idx_node.expression())
                    idx_place = p_idx or (idx_node.expression().getText() if hasattr(idx_node, "expression") else idx_node.getText())

                    # rhs
                    self.v.visit(rhs_node)
                    p_rhs, it_rhs = deepPlace(rhs_node)
                    rhs_place = p_rhs or rhs_node.getText()

                    t_len, _ = self.v.emitter.emitBoundsCheck(idx_place, base_name)
                    self.v.emitter.emit(Op.INDEX_STORE, arg1=base_name, res=rhs_place, label=idx_place)
                    if it_idx:
                        self.v.emitter.temp_pool.free(idx_place, "*")
                    if it_rhs:
                        self.v.emitter.temp_pool.free(rhs_place, "*")
                    if t_len:
                        self.v.emitter.temp_pool.free(t_len, "*")

                    self.v.emitter.temp_pool.resetPerStatement()
                    return None

            mp = self.matchPropertyIndexAssign(expr)
            if mp is not None:
                obj_txt, prop_chain, idx_node = mp
                rhs_node = self.rhsOfAssignExpr(expr)
                if rhs_node is not None:
                    # cargar cadena de propiedades con FIELD_LOAD
                    curr_place = 'this' if obj_txt == 'this' else obj_txt
                    temp_to_free = None
                    for prop_name in prop_chain:
                        t_next = self.v.emitter.temp_pool.newTemp("*")
                        q = self.v.emitter.emit(Op.FIELD_LOAD, arg1=curr_place, res=t_next, label=prop_name)
                        if temp_to_free and temp_to_free != 'this':
                            self.v.emitter.temp_pool.free(temp_to_free, "*")
                        temp_to_free = t_next
                        curr_place = t_next

                    # idx y rhs
                    idx_expr = idx_node.expression() if hasattr(idx_node, "expression") else idx_node
                    self.v.visit(idx_expr)
                    p_idx, it_idx = deepPlace(idx_expr)
                    idx_place = p_idx or idx_expr.getText()

                    self.v.visit(rhs_node)
                    p_rhs, it_rhs = deepPlace(rhs_node)
                    rhs_place = p_rhs or rhs_node.getText()

                    t_len, _ = self.v.emitter.emitBoundsCheck(idx_place, curr_place)
                    self.v.emitter.emit(Op.INDEX_STORE, arg1=curr_place, res=rhs_place, label=idx_place)

                    if t_len:
                        self.v.emitter.temp_pool.free(t_len, "*")

                    if it_idx:
                        self.v.emitter.temp_pool.free(idx_place, "*")
                    if it_rhs:
                        self.v.emitter.temp_pool.free(rhs_place, "*")
                    if temp_to_free and temp_to_free != 'this':
                        self.v.emitter.temp_pool.free(temp_to_free, "*")

                    self.v.emitter.temp_pool.resetPerStatement()
                    return None

            # Fallback: delegar a visitAssignment (maneja var = expr y obj.prop = expr)
            self.visitAssignment(expr)
            self.v.emitter.temp_pool.resetPerStatement()
            return None

        # No asignación: evaluar por efectos
        self.v.visit(expr)
        self.v.emitter.temp_pool.resetPerStatement()
        return None

    # ----------------------------------
    # Bloques (barrera de flujo)
    # ----------------------------------
    @logFunction(channel="tac")
    def visitBlock(self, ctx):
        terminated = False
        reason = None

        for st in ctx.statement():
            # Si ya terminó el flujo, no sigas visitando nada del bloque.
            if terminated or getattr(self.v.emitter, "flow_terminated", False):
                break

            # Limpia banderas por sentencia
            self.v.stmt_just_terminated = None
            self.v.stmt_just_terminator_node = None

            # Visita la sentencia
            self.v.visit(st)

            # ¿Esta sentencia terminó el flujo? (return, break emitido como terminador, etc.)
            if self.v.stmt_just_terminated:
                terminated = True
                reason = self.v.stmt_just_terminated
                # Avísale al emitter para que otros visitors (por si acaso) sepan que ya no deben emitir.
                if hasattr(self.v.emitter, "markFlowTerminated"):
                    self.v.emitter.markFlowTerminated()
                break

        # Devolver estado de terminación del bloque
        return {
            "terminated": terminated or bool(getattr(self.v.emitter, "flow_terminated", False)),
            "reason": reason or getattr(self.v, "stmt_just_terminated", None),
        }


    # ----------------------------------
    # Declaraciones (solo inicializador)
    # ----------------------------------
    @logFunction(channel="tac")
    def visitVariableDeclaration(self, ctx):
        if getattr(self.v.emitter, "flow_terminated", False):
            return None        
        init = ctx.initializer()
        name = ctx.Identifier().getText()
        if init is not None:
            self.v.visit(init.expression())
            p, _ = deepPlace(init.expression())
            rhs_place = p or init.expression().getText()
            self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=name)
        self.v.emitter.temp_pool.resetPerStatement()
        return None

    @logFunction(channel="tac")
    def visitConstantDeclaration(self, ctx):
        if getattr(self.v.emitter, "flow_terminated", False):
            return None
        name = ctx.Identifier().getText() if ctx.Identifier() else "<unnamed-const>"
        expr_ctx = ctx.expression()
        if expr_ctx is not None:
            self.v.visit(expr_ctx)
            p, _ = deepPlace(expr_ctx)
            rhs_place = p or expr_ctx.getText()
            self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=name)
        self.v.emitter.temp_pool.resetPerStatement()
        return None

    # ----------------------------------
    # Asignaciones
    # ----------------------------------
    @logFunction(channel="tac")
    def visitAssignment(self, ctx):
        if getattr(self.v.emitter, "flow_terminated", False):
            return None
        is_expr_ctx = isinstance(ctx, CompiscriptParser.ExpressionContext)
        exprs = self.expressionsFromCTX(ctx)
        n = len(exprs)

        if is_expr_ctx:
            if n == 2:
                # v[i] = expr
                m = self.matchSimpleIndexAssign(exprs[0])
                if m is not None:
                    base_name, idx_node = m
                    rhs_node = exprs[1]

                    idx_expr = idx_node.expression() if hasattr(idx_node, "expression") else idx_node
                    self.v.visit(idx_expr)
                    p_idx, it_idx = deepPlace(idx_expr)
                    idx_place = p_idx or idx_expr.getText()

                    self.v.visit(rhs_node)
                    p_rhs, it_rhs = deepPlace(rhs_node)
                    rhs_place = p_rhs or rhs_node.getText()

                    t_len, _ = self.v.emitter.emitBoundsCheck(idx_place, base_name)
                    self.v.emitter.emit(Op.INDEX_STORE, arg1=base_name, res=rhs_place, label=idx_place)
                    if it_idx:
                        self.v.emitter.temp_pool.free(idx_place, "*")
                    if it_rhs:
                        self.v.emitter.temp_pool.free(rhs_place, "*")
                    if t_len:
                        self.v.emitter.temp_pool.free(t_len, "*")
                    return None

                # id = expr
                name = None
                lhs_ctx = self.findDesc(exprs[0], CompiscriptParser.LeftHandSideContext)
                if lhs_ctx is not None:
                    has_suffix = False
                    try:
                        sufs = lhs_ctx.suffixOp()
                        has_suffix = (sufs is not None) and (len(sufs) > 0)
                    except Exception:
                        pass
                    if not has_suffix:
                        try:
                            name = lhs_ctx.primaryAtom().getText()
                        except Exception:
                            name = None
                        if not name:
                            try:
                                ident = self.findDesc(lhs_ctx, CompiscriptParser.IdentifierExprContext)
                                if ident is not None:
                                    name = ident.getText()
                            except Exception:
                                pass
                if name:
                    self.v.visit(exprs[1])
                    p, it = deepPlace(exprs[1])
                    rhs_place = p or exprs[1].getText()

                    # destino = dirección del símbolo (fp[...], gp[...])
                    try:
                        sym = self.v.scopeManager.lookup(name)
                        dst_place = place_of_symbol(sym) if sym is not None else name
                    except Exception:
                        dst_place = name

                    self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=dst_place)
                    if it:
                        self.v.emitter.temp_pool.free(rhs_place, "*")
                return None

            return None

        # AssignmentContext formal

        # (var) name = expr
        if n == 1 and ctx.Identifier() is not None:
            name = ctx.Identifier().getText()
            self.v.visit(exprs[0])
            p, it = deepPlace(exprs[0])
            rhs_place = p or exprs[0].getText()
            self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=name)
            if it:
                self.v.emitter.temp_pool.free(rhs_place, "*")
            return None

        # (index) v[i] = expr
        if n == 2:
            m = self.matchSimpleIndexAssign(exprs[0])
            if m is not None:
                base_name, idx_node = m
                rhs_node = exprs[1]

                idx_expr = idx_node.expression() if hasattr(idx_node, "expression") else idx_node
                self.v.visit(idx_expr)
                p_idx, it_idx = deepPlace(idx_expr)
                idx_place = p_idx or idx_expr.getText()

                self.v.visit(rhs_node)
                p_rhs, it_rhs = deepPlace(rhs_node)
                rhs_place = p_rhs or rhs_node.getText()

                t_len, _ = self.v.emitter.emitBoundsCheck(idx_place, base_name)
                self.v.emitter.emit(Op.INDEX_STORE, arg1=base_name, res=rhs_place, label=idx_place)
                if it_idx:
                    self.v.emitter.temp_pool.free(idx_place, "*")
                if it_rhs:
                    self.v.emitter.temp_pool.free(rhs_place, "*")
                if t_len:
                    self.v.emitter.temp_pool.free(t_len, "*")
                return None

            # (prop) obj.prop = expr
            lhs_obj = exprs[0]
            rhs_exp = exprs[1]
            prop_tok = getattr(ctx, "Identifier", lambda: None)()
            try:
                prop_name = prop_tok.getText() if prop_tok is not None else "<prop>"
            except Exception:
                prop_name = "<prop>"

            self.v.visit(lhs_obj)
            p_obj, it_obj = deepPlace(lhs_obj)
            obj_place = p_obj or lhs_obj.getText()

            self.v.visit(rhs_exp)
            p_rhs, it_rhs = deepPlace(rhs_exp)
            rhs_place = p_rhs or rhs_exp.getText()

            q = self.v.emitter.emit(Op.FIELD_STORE, arg1=obj_place, res=rhs_place, label=prop_name)
            if it_obj:
                self.v.emitter.temp_pool.free(obj_place, "*")
            if it_rhs:
                self.v.emitter.temp_pool.free(rhs_place, "*")

            return None

        return None

    # ----------------------------------
    # foreach (sin emisión específica)
    # ----------------------------------
    @logFunction(channel="tac")
    def visitForeachStatement(self, ctx):
        # No hay lowering aquí; solo visitar el bloque por efectos.
        self.v.visit(ctx.block())
        self.v.emitter.temp_pool.resetPerStatement()
        return {"terminated": False, "reason": None}
