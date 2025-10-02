from semantic.symbol_kinds import SymbolCategory
from logs.logger import log, logFunction
from utils.ast_utils import setPlace, getPlace, isTempNode, freeIfTemp, deepPlace
from ir.tac import Op


class TacExpressions:
    """
    Emisión de TAC para expresiones.
    No valida tipos ni símbolos (la pasada semántica ya lo hizo);
    aquí solo materializamos lugares (places) y cuádruplos.
    """

    @logFunction(channel="tac")
    def __init__(self, v, lvalues):
        log("===== [tac_expressions] start =====", channel="tac")
        self.v = v
        self.lvalues = lvalues

    # ---------- Entradas ----------

    @logFunction(channel="tac")
    def visitExpression(self, ctx):
        if ctx.getChildCount() == 0:
            return None
        child = ctx.getChild(0)
        self.v.visit(child)
        p, it = deepPlace(child)
        if p is not None:
            setPlace(ctx, p, it)
        return None

    @logFunction(channel="tac")
    def visitExprNoAssign(self, ctx):
        if ctx.getChildCount() == 0:
            return None
        child = ctx.getChild(0)
        self.v.visit(child)
        p, it = deepPlace(child)
        if p is not None:
            setPlace(ctx, p, it)
        return None

    # ---------- Primarios ----------

    @logFunction(channel="tac")
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
            return None
        return self.v.visitChildren(ctx)

    @logFunction(channel="tac")
    def visitLiteralExpr(self, ctx):
        # Los literales usan su texto como place.
        value = ctx.getText()
        setPlace(ctx, value, False)
        return None

    @logFunction(channel="tac")
    def visitIdentifierExpr(self, ctx):
        name = ctx.getText()
        sym = self.v.scopeManager.lookup(name)
        if sym is None:
            # La pasada semántica debió reportarlo.
            return None

        if sym.category == SymbolCategory.FUNCTION:
            # Función con capturas → construir closure
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
                f_label = getattr(sym, "label", None) or f"f_{sym.name}"
                self.v.emitter.emit(Op.MKCLOS, arg1=f_label, arg2=env_t, res=clos_t)

                setPlace(ctx, clos_t, True)
                return None

            # Función sin capturas: usar el nombre textual como place.
            setPlace(ctx, name, False)
            return None

        # Variable / campo: el nombre textual es el place.
        setPlace(ctx, name, False)
        return None

    @logFunction(channel="tac")
    def visitArrayLiteral(self, ctx):
        expr_ctxs = list(ctx.expression()) or []

        # Crear lista
        t_list = self.v.emitter.temp_pool.newTemp("ref")
        self.v.emitter.emit(Op.NEWLIST, arg1=len(expr_ctxs), res=t_list)

        # Cargar elementos
        for k, ek in enumerate(expr_ctxs):
            self.v.visit(ek)
            elem_place = getattr(ek, "_place", None) or ek.getText()
            self.v.emitter.emit(Op.INDEX_STORE, arg1=t_list, res=elem_place, label=k)
            if getattr(ek, "_is_temp", False):
                self.v.emitter.temp_pool.free(elem_place, "*")

        setPlace(ctx, t_list, True)
        return None

    @logFunction(channel="tac")
    def visitThisExpr(self, ctx):
        setPlace(ctx, "this", False)
        return None

    # ---------- Operadores con emisión ----------

    @logFunction(channel="tac")
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
        while i < len(children):
            op_txt = children[i].getText()
            right_node = children[i + 1]
            self.v.visit(right_node)
            right_place = getPlace(right_node) or deepPlace(right_node)[0] or right_node.getText()

            t = self.v.emitter.temp_pool.newTemp("*")
            self.v.emitter.emit(Op.BINARY, arg1=current_place, arg2=right_place, res=t, label=op_txt)

            freeIfTemp(current_node, self.v.emitter.temp_pool, "*")
            freeIfTemp(right_node, self.v.emitter.temp_pool, "*")
            current_place = t
            current_node = ctx
            i += 2

        setPlace(ctx, current_place, str(current_place).startswith("t"))
        return None

    @logFunction(channel="tac")
    def visitMultiplicativeExpr(self, ctx):
        """
        Misma estrategia que aditiva (izquierda-asociativa).
        """
        return self.visitAdditiveExpr(ctx)

    @logFunction(channel="tac")
    def visitRelationalExpr(self, ctx):
        """
        Cadenas relacionales (a < b < c) se evalúan por pares,
        materializando booleanos intermedios.
        """
        children = list(ctx.getChildren())
        if not children:
            return None

        left_node = children[0]
        self.v.visit(left_node)
        last_place = getPlace(left_node) or deepPlace(left_node)[0] or left_node.getText()
        last_node = left_node

        i = 1
        final_place = last_place
        while i < len(children):
            op_txt = children[i].getText()
            right_node = children[i + 1]
            self.v.visit(right_node)
            right_place = getPlace(right_node) or deepPlace(right_node)[0] or right_node.getText()

            t = self.v.emitter.temp_pool.newTemp("bool")
            self.v.emitter.emit(Op.BINARY, arg1=last_place, arg2=right_place, res=t, label=op_txt)

            freeIfTemp(last_node, self.v.emitter.temp_pool, "*")
            freeIfTemp(right_node, self.v.emitter.temp_pool, "*")
            final_place = t
            last_place = right_place
            last_node = ctx
            i += 2

        setPlace(ctx, final_place, True)
        return None

    @logFunction(channel="tac")
    def visitEqualityExpr(self, ctx):
        # Igual que relacional (resultado booleano).
        return self.visitRelationalExpr(ctx)

    @logFunction(channel="tac")
    def visitLogicalAndExpr(self, ctx):
        """
        Versión no-cortocircuito para usar en contexto de expresión:
        genera un temporal booleano con '&&' como operador binario.
        (El cortocircuito se maneja cuando está en posición condicional.)
        """
        children = list(ctx.getChildren())
        if not children:
            return None

        left_node = children[0]
        self.v.visit(left_node)
        current_place = getPlace(left_node) or deepPlace(left_node)[0] or left_node.getText()
        current_node = left_node

        i = 1
        while i < len(children):
            right_node = children[i + 1]
            self.v.visit(right_node)
            right_place = getPlace(right_node) or deepPlace(right_node)[0] or right_node.getText()

            t = self.v.emitter.temp_pool.newTemp("bool")
            self.v.emitter.emit(Op.BINARY, arg1=current_place, arg2=right_place, res=t, label="&&")

            freeIfTemp(current_node, self.v.emitter.temp_pool, "*")
            freeIfTemp(right_node, self.v.emitter.temp_pool, "*")
            current_place = t
            current_node = ctx
            i += 2

        setPlace(ctx, current_place, True)
        return None

    @logFunction(channel="tac")
    def visitLogicalOrExpr(self, ctx):
        """
        Versión no-cortocircuito para contexto de expresión:
        genera un temporal booleano con '||' como operador binario.
        """
        children = list(ctx.getChildren())
        if not children:
            return None

        left_node = children[0]
        self.v.visit(left_node)
        current_place = getPlace(left_node) or deepPlace(left_node)[0] or left_node.getText()
        current_node = left_node

        i = 1
        while i < len(children):
            right_node = children[i + 1]
            self.v.visit(right_node)
            right_place = getPlace(right_node) or deepPlace(right_node)[0] or right_node.getText()

            t = self.v.emitter.temp_pool.newTemp("bool")
            self.v.emitter.emit(Op.BINARY, arg1=current_place, arg2=right_place, res=t, label="||")

            freeIfTemp(current_node, self.v.emitter.temp_pool, "*")
            freeIfTemp(right_node, self.v.emitter.temp_pool, "*")
            current_place = t
            current_node = ctx
            i += 2

        setPlace(ctx, current_place, True)
        return None

    @logFunction(channel="tac")
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
            return None

        # Caso "(expr)" → propagar place del hijo.
        self.v.visit(ctx.primaryExpr())
        p = getPlace(ctx.primaryExpr()) or deepPlace(ctx.primaryExpr())[0]
        if p is not None:
            setPlace(ctx, p, isTempNode(ctx.primaryExpr()))
        return None

    # ---------- Objetos / propiedades / new ----------

    @logFunction(channel="tac")
    def visitNewExpr(self, ctx):
        class_name = ctx.Identifier().getText()

        # Tamaño estimado del objeto (si el semántico lo expone).
        try:
            obj_size = int(self.v.class_handler.getObjectSize(class_name))
        except Exception:
            obj_size = 0

        t_obj = self.v.emitter.temp_pool.newTemp("ref")
        self.v.emitter.emit(Op.NEWOBJ, arg1=class_name, arg2=str(obj_size), res=t_obj)

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
            f_label = f"f_{ctor_owner}_constructor"
            self.v.emitter.emit(Op.CALL, arg1=f_label, arg2=str(n_params))

        setPlace(ctx, t_obj, True)
        return None

    @logFunction(channel="tac")
    def visitPropertyAccessExpr(self, ctx):
        # No materializa por sí solo: LValues decide si hace FIELD_LOAD o binding de método.
        self.v.visit(ctx.expression())
        return None

    @logFunction(channel="tac")
    def visitLeftHandSide(self, ctx):
        return self.lvalues.visitLeftHandSide(ctx)
