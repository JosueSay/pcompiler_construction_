from semantic.symbol_kinds import SymbolCategory
from logs.logger import log, logFunction
from utils.ast_utils import setPlace, getPlace, isTempNode, freeIfTemp, deepPlace
from ir.tac import Op
from ir.addr_format import place_of_symbol


class TacExpressions:
    """
    Emisión de TAC para expresiones.
    No valida tipos ni símbolos (la pasada semántica ya lo hizo);
    aquí solo materializamos lugares (places) y cuádruplos.
    """

    
    def __init__(self, v, lvalues):
        """
        Inicializa el generador de TAC para expresiones.
        :param v: Visitador/contexto que contiene emitter, temp_pool, etc.
        :param lvalues: Visitor auxiliar para lvalues
        """
        self.v = v
        self.lvalues = lvalues

        log("=" * 60, channel="tac")
        log("↳ [TacExpressions] initialized", channel="tac")
        log("=" * 60, channel="tac")

    # ---------- Entradas ----------

    
    def visitExpression(self, ctx):
        if ctx.getChildCount() == 0:
            return None
        child = ctx.getChild(0)
        log(f"\t[TAC][expr] visitExpression -> child: {child.getText()}", channel="tac")
        self.v.visit(child)
        p, it = deepPlace(child)
        if p is not None:
            setPlace(ctx, p, it)
            log(f"\t[TAC][expr] place set for node '{ctx.getText()}': {p}", channel="tac")
        return None

    
    def visitExprNoAssign(self, ctx):
        if ctx.getChildCount() == 0:
            return None
        child = ctx.getChild(0)
        log(f"\t[TAC][expr] visitExprNoAssign -> child: {child.getText()}", channel="tac")
        self.v.visit(child)
        p, it = deepPlace(child)
        if p is not None:
            setPlace(ctx, p, it)
            log(f"\t[TAC][expr] place set for node '{ctx.getText()}': {p}", channel="tac")
        return None

    # ---------- Primarios ----------

    
    def visitPrimaryExpr(self, ctx):
        if hasattr(ctx, "literalExpr") and ctx.literalExpr() is not None:
            return self.v.visit(ctx.literalExpr())
        if hasattr(ctx, "leftHandSide") and ctx.leftHandSide() is not None:
            return self.v.visit(ctx.leftHandSide())
        if ctx.getChildCount() == 3 and ctx.getChild(0).getText() == '(':
            self.v.visit(ctx.expression())
            ch = ctx.expression()
            p = getPlace(ch) or deepPlace(ch)[0]
            if p is not None:
                setPlace(ctx, p, isTempNode(ch))
                log(f"\t[TAC][expr] place set for parenthesized expr: {p}", channel="tac")
            return None
        return self.v.visitChildren(ctx)

    
    def visitLiteralExpr(self, ctx):
        value = ctx.getText()
        setPlace(ctx, value, False)
        log(f"\t[TAC][expr] literal: {value}", channel="tac")
        return None

    
    def visitIdentifierExpr(self, ctx):
        name = ctx.getText()
        sym = self.v.scopeManager.lookup(name)
        if sym is None:
            log(f"\t[TAC][warn] identifier not found: {name}", channel="tac")
            return None

        if sym.category == SymbolCategory.FUNCTION:
            captured = []
            try:
                cap_info = getattr(sym, "captures", None)
                if cap_info and getattr(cap_info, "captured", None):
                    captured = [n for (n, _t, _sid) in cap_info.captured]
            except Exception:
                captured = []

            if captured:
                args_txt = ",".join(captured) if captured else ""
                env_t = self.v.emitter.temp_pool.newTemp("ref")
                self.v.emitter.emit(Op.MKENV, arg1=args_txt, res=env_t)
                clos_t = self.v.emitter.temp_pool.newTemp("ref")
                f_label = getattr(sym, "label", None) or f"{sym.name}"
                self.v.emitter.emit(Op.MKCLOS, arg1=f_label, arg2=env_t, res=clos_t)
                self.v.emitter.temp_pool.free(env_t, "*")
                setPlace(ctx, clos_t, True)
                log(f"\t[TAC][expr] closure created for function '{name}' -> {clos_t}", channel="tac")
                return None

            # Función sin capturas
            setPlace(ctx, name, False)
            log(f"\t[TAC][expr] function identifier: {name}", channel="tac")
            return None

        # Variable / campo
        try:
            addr = place_of_symbol(sym) if sym is not None else name
        except Exception:
            addr = name
        setPlace(ctx, addr, False)
        log(f"\t[TAC][expr] variable identifier: {name} -> {addr}", channel="tac")
        return None

    
    def visitArrayLiteral(self, ctx):
        expr_ctxs = list(ctx.expression()) or []
        t_list = self.v.emitter.temp_pool.newTemp("ref")
        self.v.emitter.emit(Op.NEWLIST, arg1=len(expr_ctxs), res=t_list)
        log(f"\t[TAC][expr] new array/list temp: {t_list} with {len(expr_ctxs)} elements", channel="tac")

        for k, ek in enumerate(expr_ctxs):
            self.v.visit(ek)
            elem_place = getattr(ek, "_place", None) or ek.getText()
            self.v.emitter.emit(Op.INDEX_STORE, arg1=t_list, res=elem_place, label=k)
            log(f"\t[TAC][expr] array element {k}: {elem_place}", channel="tac")
            if getattr(ek, "_is_temp", False):
                self.v.emitter.temp_pool.free(elem_place, "*")

        setPlace(ctx, t_list, True)
        log(f"\t[TAC][expr] array literal place: {t_list}", channel="tac")
        return None

    
    def visitThisExpr(self, ctx):
        setPlace(ctx, "this", False)
        log(f"\t[TAC][expr] 'this' expression", channel="tac")
        return None

    # ---------- Operadores con emisión ----------

    
    def visitAdditiveExpr(self, ctx):
        """
        Evalúa una cadena izquierda-asociativa de sumas/restas.
        """
        children = list(ctx.getChildren())
        if not children:
            return None

        left_node = children[0]
        self.v.visit(left_node)
        current_place = getPlace(left_node) or deepPlace(left_node)[0] or left_node.getText()
        current_node = left_node

        i = 1
        made_temp = False
        while i < len(children):
            op_txt = children[i].getText()
            right_node = children[i + 1]
            self.v.visit(right_node)
            right_place = getPlace(right_node) or deepPlace(right_node)[0] or right_node.getText()

            t = self.v.emitter.temp_pool.newTemp("*")
            self.v.emitter.emit(Op.BINARY, arg1=current_place, arg2=right_place, res=t, label=op_txt)
            log(f"\t[TAC][expr] binary {op_txt}: {current_place}, {right_place} -> {t}", channel="tac")

            freeIfTemp(current_node, self.v.emitter.temp_pool, "*")
            freeIfTemp(right_node, self.v.emitter.temp_pool, "*")
            current_place = t
            current_node = ctx
            made_temp = True
            i += 2

        setPlace(ctx, current_place, True if made_temp else isTempNode(left_node))
        log(f"\t[TAC][expr] additive expr place: {current_place}", channel="tac")
        return None

    
    def visitMultiplicativeExpr(self, ctx):
        return self.visitAdditiveExpr(ctx)

    
    def visitRelationalExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        left_node = children[0]
        self.v.visit(left_node)
        last_place = getPlace(left_node) or deepPlace(left_node)[0] or left_node.getText()
        last_node = left_node

        i = 1
        final_place = last_place
        made_temp = False

        while i < len(children):
            op_txt = children[i].getText()
            right_node = children[i + 1]
            self.v.visit(right_node)
            right_place = getPlace(right_node) or deepPlace(right_node)[0] or right_node.getText()

            t = self.v.emitter.temp_pool.newTemp("bool")
            self.v.emitter.emit(Op.BINARY, arg1=last_place, arg2=right_place, res=t, label=op_txt)
            log(f"\t[TAC][expr] relational {op_txt}: {last_place}, {right_place} -> {t}", channel="tac")

            freeIfTemp(last_node, self.v.emitter.temp_pool, "*")
            freeIfTemp(right_node, self.v.emitter.temp_pool, "*")
            final_place = t
            last_place = right_place
            last_node = ctx
            made_temp = True
            i += 2

        setPlace(ctx, final_place, True if made_temp else isTempNode(left_node))
        log(f"\t[TAC][expr] relational expr place: {final_place}", channel="tac")
        return None

    
    def visitEqualityExpr(self, ctx):
        return self.visitRelationalExpr(ctx)

    
    def visitLogicalAndExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        left_node = children[0]
        self.v.visit(left_node)
        current_place = getPlace(left_node) or deepPlace(left_node)[0] or left_node.getText()
        current_node = left_node

        i = 1
        made_temp = False

        while i < len(children):
            right_node = children[i + 1]
            self.v.visit(right_node)
            right_place = getPlace(right_node) or deepPlace(right_node)[0] or right_node.getText()

            t = self.v.emitter.temp_pool.newTemp("bool")
            self.v.emitter.emit(Op.BINARY, arg1=current_place, arg2=right_place, res=t, label="&&")
            log(f"\t[TAC][expr] logical AND: {current_place}, {right_place} -> {t}", channel="tac")

            freeIfTemp(current_node, self.v.emitter.temp_pool, "*")
            freeIfTemp(right_node, self.v.emitter.temp_pool, "*")
            current_place = t
            current_node = ctx
            made_temp = True
            i += 2

        setPlace(ctx, current_place, True if made_temp else isTempNode(left_node))
        log(f"\t[TAC][expr] logical AND expr place: {current_place}", channel="tac")
        return None

    
    def visitLogicalOrExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        left_node = children[0]
        self.v.visit(left_node)
        current_place = getPlace(left_node) or deepPlace(left_node)[0] or left_node.getText()
        current_node = left_node

        i = 1
        made_temp = False
        while i < len(children):
            right_node = children[i + 1]
            self.v.visit(right_node)
            right_place = getPlace(right_node) or deepPlace(right_node)[0] or right_node.getText()

            t = self.v.emitter.temp_pool.newTemp("bool")
            self.v.emitter.emit(Op.BINARY, arg1=current_place, arg2=right_place, res=t, label="||")
            log(f"\t[TAC][expr] logical OR: {current_place}, {right_place} -> {t}", channel="tac")

            freeIfTemp(current_node, self.v.emitter.temp_pool, "*")
            freeIfTemp(right_node, self.v.emitter.temp_pool, "*")
            current_place = t
            current_node = ctx
            made_temp = True
            i += 2

        setPlace(ctx, current_place, True if made_temp else isTempNode(left_node))
        log(f"\t[TAC][expr] logical OR expr place: {current_place}", channel="tac")
        return None

    
    def visitUnaryExpr(self, ctx):
        if ctx.getChildCount() == 2:
            op_txt = ctx.getChild(0).getText()
            inner_node = ctx.unaryExpr()
            self.v.visit(inner_node)
            inner_place = getPlace(inner_node) or deepPlace(inner_node)[0] or inner_node.getText()

            t = self.v.emitter.temp_pool.newTemp("bool" if op_txt == "!" else "*")
            self.v.emitter.emit(Op.UNARY, arg1=inner_place, res=t, label=op_txt)
            freeIfTemp(inner_node, self.v.emitter.temp_pool, "*")
            setPlace(ctx, t, True)
            log(f"\t[TAC][expr] unary {op_txt}: {inner_place} -> {t}", channel="tac")
            return None

        # Caso "(expr)" → propagar place del hijo.
        self.v.visit(ctx.primaryExpr())
        p = getPlace(ctx.primaryExpr()) or deepPlace(ctx.primaryExpr())[0]
        if p is not None:
            setPlace(ctx, p, isTempNode(ctx.primaryExpr()))
            log(f"\t[TAC][expr] propagated place from primary: {p}", channel="tac")
        return None

    # ---------- Objetos / propiedades / new ----------

    
    def visitNewExpr(self, ctx):
        class_name = ctx.Identifier().getText()

        # Tamaño estimado del objeto (si el semántico lo expone).
        try:
            obj_size = int(self.v.class_handler.getObjectSize(class_name))
        except Exception:
            obj_size = 0

        t_obj = self.v.emitter.temp_pool.newTemp("ref")
        self.v.emitter.emit(Op.NEWOBJ, arg1=class_name, arg2=str(obj_size), res=t_obj)
        log(f"\t[TAC][expr] NEWOBJ {class_name} (size={obj_size}) -> {t_obj}", channel="tac")

        # Llamada al constructor si existe en la jerarquía
        ctor_owner = None
        mt = self.v.method_registry.lookupMethod(f"{class_name}.constructor")
        if mt is not None:
            ctor_owner = class_name
        else:
            for base in self.v.class_handler.iterBases(class_name):
                mt = self.v.method_registry.lookupMethod(f"{base}.constructor")
                if mt is not None:
                    ctor_owner = base
                    break

        if ctor_owner is not None:
            self.v.emitter.emit(Op.PARAM, arg1=t_obj)
            n_params = 1
            for e in (list(ctx.arguments().expression()) if ctx.arguments() else []):
                self.v.visit(e)
                p, is_tmp = deepPlace(e)
                aplace = p or e.getText()
                self.v.emitter.emit(Op.PARAM, arg1=aplace)
                if is_tmp:
                    self.v.emitter.temp_pool.free(aplace, "*")
                n_params += 1
            f_label = f"{ctor_owner}_constructor"
            self.v.emitter.emitCall(f_label, n_params)
            log(f"\t[TAC][expr] CALL constructor {f_label} with {n_params} params", channel="tac")


        setPlace(ctx, t_obj, True)
        log(f"\t[TAC][expr] newExpr place: {t_obj}", channel="tac")
        return None

    
    def visitPropertyAccessExpr(self, ctx):
        # No materializa por sí solo: LValues decide si hace FIELD_LOAD o binding de método.
        self.v.visit(ctx.expression())
        log(f"\t[TAC][expr] property access on expr: {ctx.getText()}", channel="tac")
        return None

    
    def visitLeftHandSide(self, ctx):
        log(f"\t[TAC][expr] visitLeftHandSide: {ctx.getText()}", channel="tac")
        return self.lvalues.visitLeftHandSide(ctx)
