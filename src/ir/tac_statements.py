from antlr4.tree.Tree import TerminalNode
from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger import log, logFunction
from utils.ast_utils import deepPlace, isAssignText
from ir.tac import Op
from ir.addr_format import place_of_symbol


class TacStatements:
    def __init__(self, v):
        log("="*60, channel="tac")
        log("↳ [TacStatements] initialized", channel="tac")
        log("="*60, channel="tac")
        self.v = v

    # ---------- helpers AST ----------
    
    def findDesc(self, node, klass):
        log(f"\t[TacStatements][findDesc] enter node={node}, looking for {klass}", channel="tac")
        try:
            for ch in node.getChildren():
                if isinstance(ch, klass):
                    log(f"\t[TacStatements][findDesc] found {klass} in {ch}", channel="tac")
                    return ch
                sub = self.findDesc(ch, klass)
                if sub is not None:
                    return sub
        except Exception:
            return None
        return None

    def expressionsFromCTX(self, ctx):
        exprs = []
        try:
            exprs = ctx.getRuleContexts(CompiscriptParser.ExpressionContext)
            if exprs:
                exprs = list(exprs)
        except Exception:
            pass
        if not exprs:
            try:
                raw = ctx.expression()
                if raw is None:
                    exprs = []
                elif isinstance(raw, (list, tuple)):
                    exprs = list(raw)
                else:
                    exprs = [raw]
            except Exception:
                exprs = []
        log(f"\t[TacStatements][expressionsFromCTX] found {len(exprs)} expressions in {ctx.getText()}", channel="tac")
        return exprs

    def rhsOfAssignExpr(self, expr_ctx):
        rhs = None
        try:
            assign = self.findDesc(expr_ctx, CompiscriptParser.AssignExprContext)
            if assign is not None:
                try:
                    rhs = assign.exprNoAssign()
                    if isinstance(rhs, (list, tuple)):
                        rhs = rhs[-1] if rhs else None
                except Exception:
                    rhs = None
        except Exception:
            rhs = None

        log(f"\t[TacStatements][rhsOfAssignExpr] rhs for {expr_ctx.getText()} -> {rhs}", channel="tac")
        return rhs

    def matchSimpleIndexAssign(self, lhs_or_expr_node):
        res = None
        lhs_ctx = self.findDesc(lhs_or_expr_node, CompiscriptParser.LeftHandSideContext)
        if lhs_ctx:
            try:
                lhs_txt = lhs_ctx.getText()
                brk = lhs_txt.find('[')
                if brk > 0:
                    base_txt = lhs_txt[:brk]
                    if base_txt not in ('this',) and '.' not in base_txt:
                        idx_node = self.findDesc(lhs_ctx, CompiscriptParser.IndexExprContext)
                        if idx_node:
                            res = (base_txt, idx_node)
            except Exception:
                res = None
        log(f"\t[TacStatements][matchSimpleIndexAssign] {lhs_or_expr_node.getText()} -> {res}", channel="tac")
        return res

    def matchPropertyIndexAssign(self, lhs_or_expr_node):
        res = None
        lhs_ctx = self.findDesc(lhs_or_expr_node, CompiscriptParser.LeftHandSideContext)
        if lhs_ctx:
            try:
                lhs_txt = lhs_ctx.getText()
                brk = lhs_txt.find('[')
                if brk > 0:
                    base_txt = lhs_txt[:brk]
                    if '.' in base_txt:
                        parts = base_txt.split('.')
                        if len(parts) >= 2:
                            obj_txt = parts[0]
                            prop_chain = parts[1:]
                            idx_node = self.findDesc(lhs_ctx, CompiscriptParser.IndexExprContext)
                            if idx_node:
                                res = (obj_txt, prop_chain, idx_node)
            except Exception:
                res = None
        log(f"\t[TacStatements][matchPropertyIndexAssign] {lhs_or_expr_node.getText()} -> {res}", channel="tac")
        return res


    def visitExpressionStatement(self, ctx):
        log(f"\t[TacStatements][visitExpressionStatement] enter: {ctx.getText()}", channel="tac")

        if getattr(self.v.emitter, "flow_terminated", False):
            log("\t[TacStatements][visitExpressionStatement] flow already terminated, skipping", channel="tac")
            return None

        get_asgn = getattr(ctx, "assignment", None)
        if callable(get_asgn):
            asg = get_asgn()
            if asg is not None:
                log(f"\t[TacStatements][visitExpressionStatement] found assignment: {asg.getText()}", channel="tac")
                self.visitAssignment(asg)
                self.v.emitter.temp_pool.resetPerStatement()
                return None

        expr = ctx.expression()
        txt = getattr(expr, "getText", lambda: "")()
        is_assign = isAssignText(txt) or isAssignText(getattr(ctx, "getText", lambda: "")())

        if is_assign:
            log(f"\t[TacStatements][visitExpressionStatement] detected assignment expression: {txt}", channel="tac")

            # Asignación simple a[i] = rhs
            m = self.matchSimpleIndexAssign(expr)
            if m is not None:
                log(f"\t[TacStatements][visitExpressionStatement] simple index assign: {m}", channel="tac")
                base_name, idx_node = m
                rhs_node = self.rhsOfAssignExpr(expr)
                if rhs_node is not None:
                    log(f"\t[TacStatements][visitExpressionStatement] RHS detected: {rhs_node.getText()}", channel="tac")
                    self.v.visit(idx_node.expression() if hasattr(idx_node, "expression") else idx_node)
                    p_idx, it_idx = deepPlace(idx_node if not hasattr(idx_node, "expression") else idx_node.expression())
                    idx_place = p_idx or (idx_node.expression().getText() if hasattr(idx_node, "expression") else idx_node.getText())

                    self.v.visit(rhs_node)
                    p_rhs, it_rhs = deepPlace(rhs_node)
                    rhs_place = p_rhs or rhs_node.getText()

                    t_len, _ = self.v.emitter.emitBoundsCheck(idx_place, base_name)
                    self.v.emitter.emit(Op.INDEX_STORE, arg1=base_name, res=rhs_place, label=idx_place)
                    if it_idx: self.v.emitter.temp_pool.free(idx_place, "*")
                    if it_rhs: self.v.emitter.temp_pool.free(rhs_place, "*")
                    if t_len: self.v.emitter.temp_pool.free(t_len, "*")

                    self.v.emitter.temp_pool.resetPerStatement()
                    return None

            # Asignación con propiedad obj.prop[i] = rhs
            mp = self.matchPropertyIndexAssign(expr)
            if mp is not None:
                log(f"\t[TacStatements][visitExpressionStatement] property index assign: {mp}", channel="tac")
                obj_txt, prop_chain, idx_node = mp
                rhs_node = self.rhsOfAssignExpr(expr)
                if rhs_node is not None:
                    curr_place = 'this' if obj_txt == 'this' else obj_txt
                    temp_to_free = None
                    for prop_name in prop_chain:
                        t_next = self.v.emitter.temp_pool.newTemp("*")
                        q = self.v.emitter.emit(Op.FIELD_LOAD, arg1=curr_place, res=t_next, label=prop_name)
                        if temp_to_free and temp_to_free != 'this':
                            self.v.emitter.temp_pool.free(temp_to_free, "*")
                        temp_to_free = t_next
                        curr_place = t_next

                    idx_expr = idx_node.expression() if hasattr(idx_node, "expression") else idx_node
                    self.v.visit(idx_expr)
                    p_idx, it_idx = deepPlace(idx_expr)
                    idx_place = p_idx or idx_expr.getText()

                    self.v.visit(rhs_node)
                    p_rhs, it_rhs = deepPlace(rhs_node)
                    rhs_place = p_rhs or rhs_node.getText()

                    t_len, _ = self.v.emitter.emitBoundsCheck(idx_place, curr_place)
                    self.v.emitter.emit(Op.INDEX_STORE, arg1=curr_place, res=rhs_place, label=idx_place)

                    if t_len: self.v.emitter.temp_pool.free(t_len, "*")
                    if it_idx: self.v.emitter.temp_pool.free(idx_place, "*")
                    if it_rhs: self.v.emitter.temp_pool.free(rhs_place, "*")
                    if temp_to_free and temp_to_free != 'this': self.v.emitter.temp_pool.free(temp_to_free, "*")

                    self.v.emitter.temp_pool.resetPerStatement()
                    return None

            # Fallback a visitAssignment
            log("\t[TacStatements][visitExpressionStatement] fallback to visitAssignment", channel="tac")
            self.visitAssignment(expr)
            self.v.emitter.temp_pool.resetPerStatement()
            return None

        log("\t[TacStatements][visitExpressionStatement] evaluate expression for effects", channel="tac")
        self.v.visit(expr)
        self.v.emitter.temp_pool.resetPerStatement()
        return None

    # ----------------------------------
    # Bloques (barrera de flujo)
    # ----------------------------------

    def visitBlock(self, ctx):
        log(f"\t[TacStatements][visitBlock] enter block with {len(ctx.statement())} statements", channel="tac")
        terminated = False
        reason = None

        for st in ctx.statement():
            if terminated or getattr(self.v.emitter, "flow_terminated", False):
                log(f"\t[TacStatements][visitBlock] flow terminated, skipping remaining statements", channel="tac")
                break

            self.v.stmt_just_terminated = None
            self.v.stmt_just_terminator_node = None

            self.v.visit(st)

            if self.v.stmt_just_terminated:
                terminated = True
                reason = self.v.stmt_just_terminated
                log(f"\t[TacStatements][visitBlock] flow terminated by {reason}", channel="tac")
                if hasattr(self.v.emitter, "markFlowTerminated"):
                    self.v.emitter.markFlowTerminated()
                break

        log(f"\t[TacStatements][visitBlock] exit block, terminated={terminated}, reason={reason}", channel="tac")
        return {
            "terminated": terminated or bool(getattr(self.v.emitter, "flow_terminated", False)),
            "reason": reason or getattr(self.v, "stmt_just_terminated", None),
        }


    # ----------------------------------
    # Declaraciones (solo inicializador)
    # ----------------------------------

    def visitVariableDeclaration(self, ctx):
        name = ctx.Identifier().getText()
        log(f"\t[TacStatements][visitVariableDeclaration] enter: {name}", channel="tac")
        if getattr(self.v.emitter, "flow_terminated", False):
            log("\t[TacStatements][visitVariableDeclaration] flow terminated, skipping", channel="tac")
            return None

        init = ctx.initializer()
        if init is not None:
            self.v.visit(init.expression())
            p, it = deepPlace(init.expression())
            rhs_place = p or init.expression().getText()
            log(f"\t[TacStatements][visitVariableDeclaration] initializer for {name}: {rhs_place}", channel="tac")

            try:
                sym = self.v.scopeManager.lookup(name)
                log(f"[DEBUG] lookup({name}) -> {sym}", channel="tac")
                dst_place = place_of_symbol(sym) if sym is not None else name
                log(f"[DEBUG] dst_place -> {dst_place}", channel="tac")
            except Exception:
                dst_place = name

            log(f"\t[TAC][VAR] {name} -> {dst_place} = {rhs_place}", channel="tac")
            self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=dst_place)

            # liberar RHS si fue temporal
            if it:
                self.v.emitter.temp_pool.free(rhs_place, "*")

        self.v.emitter.temp_pool.resetPerStatement()
        log(f"\t[TacStatements][visitVariableDeclaration] exit: {name}", channel="tac")
        return None


    
    def visitConstantDeclaration(self, ctx):
        name = ctx.Identifier().getText() if ctx.Identifier() else "<unnamed-const>"
        log(f"\t[TacStatements][visitConstantDeclaration] enter: {name}", channel="tac")
        if getattr(self.v.emitter, "flow_terminated", False):
            log("\t[TacStatements][visitConstantDeclaration] flow terminated, skipping", channel="tac")
            return None

        expr_ctx = ctx.expression()
        if expr_ctx is not None:
            self.v.visit(expr_ctx)
            p, it = deepPlace(expr_ctx)
            rhs_place = p or expr_ctx.getText()
            log(f"\t[TacStatements][visitConstantDeclaration] initializer: {rhs_place}", channel="tac")
            self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=name)

            # liberar RHS si fue temporal
            if it:
                self.v.emitter.temp_pool.free(rhs_place, "*")

        self.v.emitter.temp_pool.resetPerStatement()
        log(f"\t[TacStatements][visitConstantDeclaration] exit: {name}", channel="tac")
        return None

    # ----------------------------------
    # Asignaciones
    # ----------------------------------

    
    def visitAssignment(self, ctx):
        if getattr(self.v.emitter, "flow_terminated", False):
            log("\t[TacStatements][visitAssignment] flow terminated, skipping", channel="tac")
            return None

        log(f"\t[TacStatements][visitAssignment] enter: {getattr(ctx, 'getText', lambda: '')()}", channel="tac")
        is_expr_ctx = isinstance(ctx, CompiscriptParser.ExpressionContext)
        exprs = self.expressionsFromCTX(ctx)
        n = len(exprs)

        if is_expr_ctx and n == 2:
            # v[i] = expr
            m = self.matchSimpleIndexAssign(exprs[0])
            if m is not None:
                log(f"\t[TacStatements][visitAssignment] simple index assign detected: {m}", channel="tac")
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
                if it_idx: self.v.emitter.temp_pool.free(idx_place, "*")
                if it_rhs: self.v.emitter.temp_pool.free(rhs_place, "*")
                if t_len: self.v.emitter.temp_pool.free(t_len, "*")
                self.v.emitter.temp_pool.resetPerStatement()
                log(f"\t[TacStatements][visitAssignment] simple index assign complete: {base_name}[{idx_place}] = {rhs_place}", channel="tac")
                return None

            # id = expr
            lhs_ctx = self.findDesc(exprs[0], CompiscriptParser.LeftHandSideContext)
            if lhs_ctx is not None:
                name = None
                has_suffix = getattr(lhs_ctx, "suffixOp", lambda: [])() is not None
                if not has_suffix:
                    try:
                        name = lhs_ctx.primaryAtom().getText()
                    except Exception:
                        pass
                if name:
                    self.v.visit(exprs[1])
                    p, it = deepPlace(exprs[1])
                    rhs_place = p or exprs[1].getText()

                    try:
                        sym = self.v.scopeManager.lookup(name)
                        log(f"[DEBUG] lookup({name}) -> {sym}", channel="tac")
                        dst_place = place_of_symbol(sym) if sym is not None else name
                        log(f"[DEBUG] dst_place -> {dst_place}", channel="tac")
                    except Exception:
                        dst_place = name

                    log(f"\t[TAC][ASSIGN] {name} -> {dst_place} = {rhs_place}", channel="tac")
                    self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=dst_place)
                    if it: self.v.emitter.temp_pool.free(rhs_place, "*")
                    self.v.emitter.temp_pool.resetPerStatement()
                    log(f"\t[TacStatements][visitAssignment] simple assign: {name} = {rhs_place}", channel="tac")
                    return None

        # Asignación a índice
        if n == 1 and ctx.Identifier() is not None:
            name = ctx.Identifier().getText()
            self.v.visit(exprs[0])
            p, it = deepPlace(exprs[0])
            rhs_place = p or exprs[0].getText()

            try:
                sym = self.v.scopeManager.lookup(name)
                log(f"[DEBUG] lookup({name}) -> {sym}", channel="tac")
                dst_place = place_of_symbol(sym) if sym is not None else name
                log(f"[DEBUG] dst_place -> {dst_place}", channel="tac")
            except Exception:
                dst_place = name

            log(f"\t[TAC][ASSIGN] {name} -> {dst_place} = {rhs_place}", channel="tac")
            self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=dst_place)
            if it: self.v.emitter.temp_pool.free(rhs_place, "*")
            self.v.emitter.temp_pool.resetPerStatement()
            log(f"\t[TacStatements][visitAssignment] variable assign: {name} = {rhs_place}", channel="tac")
            return None

        # (index) v[i] = expr
        if n == 2:
            m = self.matchSimpleIndexAssign(exprs[0])
            if m is not None:
                log(f"\t[TacStatements][visitAssignment] index assign: {m}", channel="tac")
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
                if it_idx: self.v.emitter.temp_pool.free(idx_place, "*")
                if it_rhs: self.v.emitter.temp_pool.free(rhs_place, "*")
                if t_len: self.v.emitter.temp_pool.free(t_len, "*")
                self.v.emitter.temp_pool.resetPerStatement()
                log(f"\t[TacStatements][visitAssignment] index assign complete: {base_name}[{idx_place}] = {rhs_place}", channel="tac")
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

            self.v.emitter.emit(Op.FIELD_STORE, arg1=obj_place, res=rhs_place, label=prop_name)
            if it_obj: self.v.emitter.temp_pool.free(obj_place, "*")
            if it_rhs: self.v.emitter.temp_pool.free(rhs_place, "*")

            self.v.emitter.temp_pool.resetPerStatement()
            log(f"\t[TacStatements][visitAssignment] property assign: {obj_place}.{prop_name} = {rhs_place}", channel="tac")
            return None

        log("\t[TacStatements][visitAssignment] exit", channel="tac")
        # Asegurar reset incluso si ninguna rama hizo return temprano
        self.v.emitter.temp_pool.resetPerStatement()
        return None

    # ----------------------------------
    # foreach (sin emisión específica)
    # ----------------------------------

    
    def visitForeachStatement(self, ctx):
        log("\t[TacStatements][visitForeachStatement] enter", channel="tac")
        self.v.visit(ctx.block())
        self.v.emitter.temp_pool.resetPerStatement()
        log("\t[TacStatements][visitForeachStatement] exit", channel="tac")
        return {"terminated": False, "reason": None}
