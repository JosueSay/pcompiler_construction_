from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger import log, logFunction
from utils.ast_utils import deepPlace, isAssignText
from ir.tac import Op
from ir.addr_format import place_of_symbol
from semantic.custom_types import ClassType


class TacStatements:
    def __init__(self, v):
        log("="*60, channel="tac")
        log("↳ [TacStatements] initialized", channel="tac")
        log("="*60, channel="tac")
        self.v = v

    # ---------- helpers AST ----------
    def suffixSeqAndPropsFromText(self, lhs_ctx):
        """
        A partir del texto del LHS, devuelve:
        - seq: lista con elementos en {'Index','Prop','Call'} en el orden en que aparecen
        - base_txt: texto base antes del primer sufijo (id o 'this')
        - prop_chain: lista de nombres de propiedades en orden (después de '.')
        No depende de la estructura concreta del árbol para clasificar.
        """
        try:
            lhs_txt = lhs_ctx.getText()
        except Exception:
            return [], "", []

        seq = []
        prop_chain = []
        n = len(lhs_txt)
        i = 0

        # leer base (hasta '.', '[' o '(')
        base_chars = []
        while i < n and lhs_txt[i] not in ".[(":
            base_chars.append(lhs_txt[i])
            i += 1
        base_txt = "".join(base_chars)

        def skipBracket(i):
            # salta hasta ']' correspondiente (sin anidación en nuestro lenguaje)
            i += 1  # saltar '['
            while i < n and lhs_txt[i] != ']':
                i += 1
            return i + 1 if i < n else i

        def skipParens(i):
            # salta hasta ')' correspondiente (sin anidación en nuestro lenguaje)
            i += 1  # saltar '('
            while i < n and lhs_txt[i] != ')':
                i += 1
            return i + 1 if i < n else i

        def readIdent(i):
            # lee un identificador tras un '.'
            j = i
            while j < n and lhs_txt[j] not in ".[()":
                j += 1
            return lhs_txt[i:j], j

        # recorrer sufijos
        while i < n:
            c = lhs_txt[i]
            if c == '[':
                seq.append("Index")
                i = skipBracket(i)
            elif c == '.':
                seq.append("Prop")
                i += 1  # saltar '.'
                ident, i = readIdent(i)
                if ident:
                    prop_chain.append(ident)
            elif c == '(':
                seq.append("Call")
                i = skipParens(i)
            else:
                # caracter inesperado: avanzar 1 para no quedar en bucle
                i += 1

        return seq, base_txt, prop_chain
    
    
    def resolveFieldOffset(self, owner: str, field: str):
        try:
            return self.v.lvalues.resolveFieldOffset(owner, field)
        except Exception:
            return None


    def symType(self, name: str):
        try:
            return self.v.lvalues.symType(name)
        except Exception:
            return None


    def resolveAttrType(self, owner: str, field: str):
        try:
            ch = getattr(self.v, "class_handler", None)
            if ch is not None and hasattr(ch, "getAttributeType"):
                return ch.getAttributeType(owner, field)
        except Exception:
            pass
        return None


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
        if lhs_ctx is None:
            log("\t[TacStatements][matchSimpleIndexAssign] no lhs_ctx", channel="tac")
            return None

        seq, base_txt, _props = self.suffixSeqAndPropsFromText(lhs_ctx)
        num_suffix = len(seq)
        log(f"\t[TacStatements][matchSimpleIndexAssign][TRACE] base='{base_txt}', num_suffix={num_suffix}, seq={seq}", channel="tac")

        # Reglas estrictas para "simple index":
        if not base_txt or base_txt == 'this' or '.' in base_txt:
            log("\t[TacStatements][matchSimpleIndexAssign] base inválida o no-simple", channel="tac")
            return None
        if num_suffix != 1 or seq != ["Index"]:
            log("\t[TacStatements][matchSimpleIndexAssign] Rechazado: requiere exactamente 1 suffix (Index)", channel="tac")
            return None

        idx_node = self.findDesc(lhs_ctx, CompiscriptParser.IndexExprContext)
        if idx_node is None:
            log("\t[TacStatements][matchSimpleIndexAssign] no IndexExprContext encontrado", channel="tac")
            return None

        res = (base_txt, idx_node)
        log(f"\t[TacStatements][matchSimpleIndexAssign] OK -> {res}", channel="tac")
        return res


    def buildSuffixPlan(self, lhs_ctx):
        """
        Devuelve un plan general de navegación a partir del LHS.
        plan: lista de pasos [('Index', idx_ctx), ('Prop', 'b'), ('Index', idx_ctx), ...] en orden.
        base_txt: identificador base o 'this'.
        """
        seq, base_txt, prop_chain = self.suffixSeqAndPropsFromText(lhs_ctx)

        # Recolectar todos los contextos reales en el mismo orden en que aparecen
        def collectInOrder(node, acc):
            try:
                for ch in node.getChildren():
                    if isinstance(ch, CompiscriptParser.IndexExprContext):
                        acc.append(("Index", ch))
                    elif isinstance(ch, CompiscriptParser.PropertyAccessExprContext):
                        # De PropertyAccessExprContext tomamos el texto ".name"
                        try:
                            txt = ch.getText()
                            # quitar el punto inicial
                            name = txt[1:] if txt.startswith('.') else txt
                        except Exception:
                            name = "<prop>"
                        acc.append(("Prop", name))
                    else:
                        collectInOrder(ch, acc)
            except Exception:
                return

        raw_plan = []
        collectInOrder(lhs_ctx, raw_plan)

        # Si no logramos detectar Props por los contextos, caemos al prop_chain extraído del texto
        if not any(kind == "Prop" for kind, _ in raw_plan) and prop_chain:
            # Insertar props en su orden textual entre índices cuando corresponda
            plan = []
            pi = 0
            for kind, payload in raw_plan:
                plan.append((kind, payload))
                if kind == "Index" and pi < len(prop_chain):
                    plan.append(("Prop", prop_chain[pi]))
                    pi += 1
            while pi < len(prop_chain):
                plan.append(("Prop", prop_chain[pi]))
                pi += 1
        else:
            plan = raw_plan

        return base_txt, plan


    def matchPropertyIndexAssign(self, lhs_or_expr_node):
        lhs_ctx = self.findDesc(lhs_or_expr_node, CompiscriptParser.LeftHandSideContext)
        if lhs_ctx is None:
            log("\t[TacStatements][matchPropertyIndexAssign] no lhs_ctx", channel="tac")
            return None

        seq_txt, base_txt, prop_chain_txt = self.suffixSeqAndPropsFromText(lhs_ctx)
        log(f"\t[TacStatements][matchPropertyIndexAssign][TRACE] num_suffix={len(seq_txt)}, seq={seq_txt}", channel="tac")

        base_txt, plan = self.buildSuffixPlan(lhs_ctx)

        # Debe haber al menos un Prop o un Index en total para que tenga sentido como acceso compuesto
        if not plan or all(kind not in ("Prop", "Index") for kind, _ in plan):
            log("\t[TacStatements][matchPropertyIndexAssign] Rechazado: sin pasos Prop/Index", channel="tac")
            return None

        # Aceptamos base simple o 'this'; la generalización cubre casos profundos
        log(f"\t[TacStatements][matchPropertyIndexAssign] OK: base={base_txt}, plan={[(k, (p.getText() if hasattr(p,'getText') else p)) for k,p in plan]}", channel="tac")
        return (base_txt, plan)


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

            # 1) Asignación con propiedad obj.prop[i] = rhs
            mp = self.matchPropertyIndexAssign(expr)
            if mp is not None:
                base_txt, plan = mp
                rhs_node = self.rhsOfAssignExpr(expr)
                if rhs_node is not None:
                    curr_place = 'this' if base_txt == 'this' else base_txt
                    temp_to_free = None
                    owner_name = getattr(self.symType(base_txt), "name", None)

                    # visitar RHS una sola vez (lo usaremos al final)
                    self.v.visit(rhs_node)
                    p_rhs, it_rhs = deepPlace(rhs_node)
                    rhs_place = p_rhs or rhs_node.getText()

                    # Procesar todos los pasos salvo el último, avanzando curr_place
                    for i, (kind, payload) in enumerate(plan[:-1]):
                        if kind == "Index":
                            idx_expr = payload.expression() if hasattr(payload, "expression") else payload
                            self.v.visit(idx_expr)
                            p_idx, it_idx = deepPlace(idx_expr)
                            idx_place = p_idx or idx_expr.getText()

                            if hasattr(self.v.emitter, "emitIndexLoad"):
                                t_len, _ = self.v.emitter.emitBoundsCheck(idx_place, curr_place)
                                t_next = self.v.emitter.temp_pool.newTemp("ref")
                                self.v.emitter.emitIndexLoad(curr_place, idx_place, t_next)
                                if t_len: self.v.emitter.temp_pool.free(t_len, "*")
                                if it_idx: self.v.emitter.temp_pool.free(idx_place, "*")
                            else:
                                # Fallback: al menos el check
                                self.v.emitter.emitBoundsCheck(idx_place, curr_place)
                                t_next = curr_place  # no avanzamos realmente sin emitIndexLoad

                            if temp_to_free and temp_to_free != 'this':
                                self.v.emitter.temp_pool.free(temp_to_free, "*")
                            temp_to_free = t_next
                            curr_place = t_next

                        elif kind == "Prop":
                            prop_name = payload
                            t_next = self.v.emitter.temp_pool.newTemp("*")
                            off = self.resolveFieldOffset(owner_name, prop_name) if owner_name else None
                            label_for_emit = off if isinstance(off, int) else prop_name
                            self.v.emitter.emitFieldLoad(curr_place, label_for_emit, t_next)

                            # actualizar owner_name para siguientes hops
                            if owner_name:
                                next_t = self.resolveAttrType(owner_name, prop_name)
                                owner_name = getattr(next_t, "name", None)

                            if temp_to_free and temp_to_free != 'this':
                                self.v.emitter.temp_pool.free(temp_to_free, "*")
                            temp_to_free = t_next
                            curr_place = t_next

                    # Paso final: decide STORE por Index o por Prop
                    last_kind, last_payload = plan[-1]
                    if last_kind == "Index":
                        idx_expr = last_payload.expression() if hasattr(last_payload, "expression") else last_payload
                        self.v.visit(idx_expr)
                        p_idx, it_idx = deepPlace(idx_expr)
                        idx_place = p_idx or idx_expr.getText()

                        t_len, _ = self.v.emitter.emitBoundsCheck(idx_place, curr_place)
                        self.v.emitter.emitIndexStore(curr_place, idx_place, rhs_place)
                        if t_len: self.v.emitter.temp_pool.free(t_len, "*")
                        if it_idx: self.v.emitter.temp_pool.free(idx_place, "*")

                    elif last_kind == "Prop":
                        prop_name = last_payload
                        off = self.resolveFieldOffset(owner_name, prop_name) if owner_name else None
                        label_for_emit = off if isinstance(off, int) else prop_name
                        self.v.emitter.emitFieldStore(curr_place, label_for_emit, rhs_place)

                    # liberar temporales
                    if it_rhs: self.v.emitter.temp_pool.free(rhs_place, "*")
                    if temp_to_free and temp_to_free != 'this': self.v.emitter.temp_pool.free(temp_to_free, "*")

                    self.v.emitter.temp_pool.resetPerStatement()
                    return None



            # 2) Luego: Asignación simple a[i] = rhs
            m = self.matchSimpleIndexAssign(expr)
            if m is not None:
                log(f"\t[TacStatements][visitExpressionStatement] simple index assign: {m}", channel="tac")
                base_name, idx_node = m
                rhs_node = self.rhsOfAssignExpr(expr)
                if rhs_node is not None:
                    self.v.visit(idx_node.expression() if hasattr(idx_node, "expression") else idx_node)
                    p_idx, it_idx = deepPlace(idx_node if not hasattr(idx_node, "expression") else idx_node.expression())
                    idx_place = p_idx or (idx_node.expression().getText() if hasattr(idx_node, "expression") else idx_node.getText())

                    self.v.visit(rhs_node)
                    p_rhs, it_rhs = deepPlace(rhs_node)
                    rhs_place = p_rhs or rhs_node.getText()

                    t_len, _ = self.v.emitter.emitBoundsCheck(idx_place, base_name)
                    self.v.emitter.emitIndexStore(base_name, idx_place, rhs_place)
                    if it_idx: self.v.emitter.temp_pool.free(idx_place, "*")
                    if it_rhs: self.v.emitter.temp_pool.free(rhs_place, "*")
                    if t_len: self.v.emitter.temp_pool.free(t_len, "*")

                    self.v.emitter.temp_pool.resetPerStatement()
                    return None

            # 3) Fallback a visitAssignment
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
            self.v.emitter.emitAssign(dst_place, rhs_place)

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
            self.v.emitter.emitAssign(name, rhs_place)

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
            # 1) obj.prop[...] = expr
            mp = self.matchPropertyIndexAssign(exprs[0])
            if mp is not None:
                base_txt, plan = mp
                rhs_node = exprs[1]

                curr_place = 'this' if base_txt == 'this' else base_txt
                temp_to_free = None
                owner_name = getattr(self.symType(base_txt), "name", None)

                # Pre-evaluar RHS
                self.v.visit(rhs_node)
                p_rhs, it_rhs = deepPlace(rhs_node)
                rhs_place = p_rhs or rhs_node.getText()

                # Avanzar por todos los pasos salvo el último
                for i, (kind, payload) in enumerate(plan[:-1]):
                    if kind == "Index":
                        idx_expr = payload.expression() if hasattr(payload, "expression") else payload
                        self.v.visit(idx_expr)
                        p_idx, it_idx = deepPlace(idx_expr)
                        idx_place = p_idx or idx_expr.getText()

                        if hasattr(self.v.emitter, "emitIndexLoad"):
                            t_len, _ = self.v.emitter.emitBoundsCheck(idx_place, curr_place)
                            t_next = self.v.emitter.temp_pool.newTemp("ref")
                            self.v.emitter.emitIndexLoad(curr_place, idx_place, t_next)
                            if t_len: self.v.emitter.temp_pool.free(t_len, "*")
                            if it_idx: self.v.emitter.temp_pool.free(idx_place, "*")
                        else:
                            self.v.emitter.emitBoundsCheck(idx_place, curr_place)
                            t_next = curr_place

                        if temp_to_free and temp_to_free != 'this':
                            self.v.emitter.temp_pool.free(temp_to_free, "*")
                        temp_to_free = t_next
                        curr_place = t_next

                    elif kind == "Prop":
                        prop_name = payload
                        t_next = self.v.emitter.temp_pool.newTemp("*")
                        off = self.resolveFieldOffset(owner_name, prop_name) if owner_name else None
                        label_for_emit = off if isinstance(off, int) else prop_name
                        self.v.emitter.emitFieldLoad(curr_place, label_for_emit, t_next)

                        if owner_name:
                            next_t = self.resolveAttrType(owner_name, prop_name)
                            owner_name = getattr(next_t, "name", None)

                        if temp_to_free and temp_to_free != 'this':
                            self.v.emitter.temp_pool.free(temp_to_free, "*")
                        temp_to_free = t_next
                        curr_place = t_next

                # Paso final: STORE por Index o por Prop
                last_kind, last_payload = plan[-1]
                if last_kind == "Index":
                    idx_expr = last_payload.expression() if hasattr(last_payload, "expression") else last_payload
                    self.v.visit(idx_expr)
                    p_idx, it_idx = deepPlace(idx_expr)
                    idx_place = p_idx or idx_expr.getText()

                    t_len, _ = self.v.emitter.emitBoundsCheck(idx_place, curr_place)
                    self.v.emitter.emitIndexStore(curr_place, idx_place, rhs_place)
                    if t_len: self.v.emitter.temp_pool.free(t_len, "*")
                    if it_idx: self.v.emitter.temp_pool.free(idx_place, "*")

                elif last_kind == "Prop":
                    prop_name = last_payload
                    off = self.resolveFieldOffset(owner_name, prop_name) if owner_name else None
                    label_for_emit = off if isinstance(off, int) else prop_name
                    self.v.emitter.emitFieldStore(curr_place, label_for_emit, rhs_place)

                if it_rhs: self.v.emitter.temp_pool.free(rhs_place, "*")
                if temp_to_free and temp_to_free != 'this': self.v.emitter.temp_pool.free(temp_to_free, "*")

                self.v.emitter.temp_pool.resetPerStatement()
                log(f"\t[TacStatements][visitAssignment] property index assign complete (general)", channel="tac")
                return None

          
            
            # 2. v[i] = expr
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
                self.v.emitter.emitIndexStore(base_name, idx_place, rhs_place)
                if it_idx: self.v.emitter.temp_pool.free(idx_place, "*")
                if it_rhs: self.v.emitter.temp_pool.free(rhs_place, "*")
                if t_len: self.v.emitter.temp_pool.free(t_len, "*")
                self.v.emitter.temp_pool.resetPerStatement()
                log(f"\t[TacStatements][visitAssignment] simple index assign complete: {base_name}[{idx_place}] = {rhs_place}", channel="tac")
                return None

            # 3. id = expr
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
                    self.v.emitter.emitAssign(dst_place, rhs_place)
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
            self.v.emitter.emitAssign(dst_place, rhs_place)
            if it: self.v.emitter.temp_pool.free(rhs_place, "*")
            self.v.emitter.temp_pool.resetPerStatement()
            log(f"\t[TacStatements][visitAssignment] variable assign: {name} = {rhs_place}", channel="tac")
            return None

        # (index) v[i] = expr
        if n == 2:
            # 1) property-index
            mp = self.matchPropertyIndexAssign(exprs[0])
            if mp is not None:
                log(f"\t[TacStatements][visitAssignment] property index assign (general): {mp}", channel="tac")
                base_txt, plan = mp
                rhs_node = exprs[1]

                curr_place = 'this' if base_txt == 'this' else base_txt
                temp_to_free = None
                owner_name = getattr(self.symType(base_txt), "name", None)

                # Pre-evaluar RHS
                self.v.visit(rhs_node)
                p_rhs, it_rhs = deepPlace(rhs_node)
                rhs_place = p_rhs or rhs_node.getText()

                # Avanzar por todos los pasos salvo el último
                for i, (kind, payload) in enumerate(plan[:-1]):
                    if kind == "Index":
                        idx_expr = payload.expression() if hasattr(payload, "expression") else payload
                        self.v.visit(idx_expr)
                        p_idx, it_idx = deepPlace(idx_expr)
                        idx_place = p_idx or idx_expr.getText()

                        if hasattr(self.v.emitter, "emitIndexLoad"):
                            t_len, _ = self.v.emitter.emitBoundsCheck(idx_place, curr_place)
                            t_next = self.v.emitter.temp_pool.newTemp("ref")
                            self.v.emitter.emitIndexLoad(curr_place, idx_place, t_next)
                            if t_len: self.v.emitter.temp_pool.free(t_len, "*")
                            if it_idx: self.v.emitter.temp_pool.free(idx_place, "*")
                        else:
                            self.v.emitter.emitBoundsCheck(idx_place, curr_place)
                            t_next = curr_place

                        if temp_to_free and temp_to_free != 'this':
                            self.v.emitter.temp_pool.free(temp_to_free, "*")
                        temp_to_free = t_next
                        curr_place = t_next

                    elif kind == "Prop":
                        prop_name = payload
                        t_next = self.v.emitter.temp_pool.newTemp("*")
                        off = self.resolveFieldOffset(owner_name, prop_name) if owner_name else None
                        label_for_emit = off if isinstance(off, int) else prop_name
                        self.v.emitter.emitFieldLoad(curr_place, label_for_emit, t_next)

                        if owner_name:
                            next_t = self.resolveAttrType(owner_name, prop_name)
                            owner_name = getattr(next_t, "name", None)

                        if temp_to_free and temp_to_free != 'this':
                            self.v.emitter.temp_pool.free(temp_to_free, "*")
                        temp_to_free = t_next
                        curr_place = t_next

                # STORE por Index o por Prop
                last_kind, last_payload = plan[-1]
                if last_kind == "Index":
                    idx_expr = last_payload.expression() if hasattr(last_payload, "expression") else last_payload
                    self.v.visit(idx_expr)
                    p_idx, it_idx = deepPlace(idx_expr)
                    idx_place = p_idx or idx_expr.getText()

                    t_len, _ = self.v.emitter.emitBoundsCheck(idx_place, curr_place)
                    self.v.emitter.emitIndexStore(curr_place, idx_place, rhs_place)
                    if t_len: self.v.emitter.temp_pool.free(t_len, "*")
                    if it_idx: self.v.emitter.temp_pool.free(idx_place, "*")

                elif last_kind == "Prop":
                    prop_name = last_payload
                    off = self.resolveFieldOffset(owner_name, prop_name) if owner_name else None
                    label_for_emit = off if isinstance(off, int) else prop_name
                    self.v.emitter.emitFieldStore(curr_place, label_for_emit, rhs_place)

                if it_rhs: self.v.emitter.temp_pool.free(rhs_place, "*")
                if temp_to_free and temp_to_free != 'this': self.v.emitter.temp_pool.free(temp_to_free, "*")

                self.v.emitter.temp_pool.resetPerStatement()
                log(f"\t[TacStatements][visitAssignment] property index assign complete (general)", channel="tac")
                return None

            
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
                self.v.emitter.emitIndexStore(base_name, idx_place, rhs_place)
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

            ret_type = self.v.visit(lhs_obj)
            node_type = getattr(lhs_obj, "_type", None)
            obj_type = getattr(lhs_obj, "_type", None) or ret_type
            p_obj, it_obj = deepPlace(lhs_obj)
            obj_place = p_obj or lhs_obj.getText()
            log(f"\t[TacStatements][visitAssignment] lhs_obj type source={'_type' if node_type else 'return'} -> {obj_type}", channel="tac")

            # RHS como antes
            self.v.visit(rhs_exp)
            p_rhs, it_rhs = deepPlace(rhs_exp)
            rhs_place = p_rhs or rhs_exp.getText()

            # Resolver owner_name de forma robusta (incluye cadenas tipo y.c):
            owner_name = None

            # 1) Si tenemos tipo directo del LHS (p.ej. TacLValues o semántica lo dejó)
            if isinstance(obj_type, ClassType):
                owner_name = obj_type.name

            # 2) Si no, intenta reconstruir caminando la cadena "base.prop1.prop2..."
            if owner_name is None:
                obj_text = getattr(lhs_obj, "getText", lambda: "")()
                if isinstance(obj_text, str) and obj_text:
                    parts = obj_text.split(".")
                    if len(parts) >= 1:
                        # tipo del base (p.ej., 'y')
                        curr_t = self.symType(parts[0])
                        # avanza por cada propiedad intermedia (p.ej., 'c' en 'y.c')
                        for mid_prop in parts[1:]:
                            curr_name = getattr(curr_t, "name", None)
                            curr_t = self.resolveAttrType(curr_name, mid_prop)
                            if curr_t is None:
                                break
                        owner_name = getattr(curr_t, "name", None)

            # 3) Último fallback (identificador simple)
            if owner_name is None:
                base_txt = getattr(lhs_obj, "getText", lambda: "")()
                st = self.symType(base_txt)
                owner_name = getattr(st, "name", None)

            log(f"\t[TacStatements][visitAssignment] owner_name resolved -> {owner_name}", channel="tac")


            off = self.resolveFieldOffset(owner_name, prop_name) if owner_name else None
            label_for_emit = off if isinstance(off, int) else prop_name
            
            log(
                f"\t[TacStatements][visitAssignment] field-store resolve: owner={owner_name}, "
                f"prop={prop_name}, offset={off}, using_label={label_for_emit}",
                channel="tac"
            )

            self.v.emitter.emitFieldStore(obj_place, label_for_emit, rhs_place)
            
            if it_obj: self.v.emitter.temp_pool.free(obj_place, "*")
            if it_rhs: self.v.emitter.temp_pool.free(rhs_place, "*")

            self.v.emitter.temp_pool.resetPerStatement()
            log(
                f"\t[TacStatements][visitAssignment] property assign: {obj_place}.{prop_name} = {rhs_place} "
                f"(label={label_for_emit})",
                channel="tac"
            )
            
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
