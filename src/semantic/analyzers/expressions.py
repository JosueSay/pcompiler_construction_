from semantic.symbol_kinds import SymbolCategory
from semantic.validators.literal import validateLiteral
from semantic.custom_types import (
    ArrayType, ClassType, IntegerType, StringType, BoolType, FloatType,
    VoidType, NullType, ErrorType, FunctionType
)
from semantic.type_system import (
    resultArithmetic, resultModulo, resultRelational, resultEquality,
    resultLogical, resultUnaryMinus, resultUnaryNot, isAssignable
)
from logs.logger_semantic import log_semantic, log_function
from semantic.errors import SemanticError
from ir.tac import Op


class ExpressionsAnalyzer:
    @log_function
    def __init__(self, v, lvalues):
        log_semantic("===== [Expressions.py] Inicio =====")
        self.v = v
        self.lvalues = lvalues

    # ---------- Helpers TAC ----------
    def typeToTempKind(self, t) -> str:
        if isinstance(t, BoolType): return "bool"
        if isinstance(t, IntegerType): return "int"
        if isinstance(t, FloatType): return "float"
        if isinstance(t, (StringType, ClassType, ArrayType, FunctionType, NullType)):
            return "ref"
        return "*"

    def setPlace(self, node, place: str, is_temp: bool) -> None:
        try:
            old_place = getattr(node, "_place", None)
            old_temp = getattr(node, "_is_temp", None)
            setattr(node, "_place", place)
            setattr(node, "_is_temp", is_temp)
            log_semantic(f"setPlace: Node={node}, old=({old_place},{old_temp}) new=({place},{is_temp})")
        except Exception:
            log_semantic(f"setPlace: Node={node} could not be updated")

    def getPlace(self, node) -> str | None:
        return getattr(node, "_place", None)

    def isTempNode(self, node) -> bool:
        return bool(getattr(node, "_is_temp", False))

    def newTempFor(self, t) -> str:
        kind = self.typeToTempKind(t)
        temp = self.v.emitter.temp_pool.newTemp(kind)
        log_semantic(f"newTempFor: Type={t} -> Temp={temp}")
        return temp

    def freeIfTemp(self, node, t_hint=None) -> None:
        if not self.isTempNode(node):
            return
        place = self.getPlace(node)
        if place is None:
            return
        kind = self.typeToTempKind(t_hint) if t_hint is not None else "*"
        log_semantic(f"freeIfTemp: Freeing temp={place} of kind={kind}")
        self.v.emitter.temp_pool.free(place, kind)

    def deepPlace(self, node) -> tuple[str | None, bool]:
        """Busca recursivamente un _place ya calculado en hijos (sin volver a visitar)."""
        if node is None:
            return None, False
        p = getattr(node, "_place", None)
        if p is not None:
            log_semantic(f"deepPlace: Found place={p} (is_temp={getattr(node, '_is_temp', False)}) in node={node}")
            return p, bool(getattr(node, "_is_temp", False))
        try:
            n = node.getChildCount()
        except Exception:
            n = 0
        for i in range(n or 0):
            ch = node.getChild(i)
            p2, it2 = self.deepPlace(ch)
            if p2 is not None:
                return p2, it2
        return None, False


    # ---------- Entradas de dispatch envoltorio ----------
    @log_function
    def visitExpression(self, ctx):
        if ctx.getChildCount() == 0:
            return None
        child = ctx.getChild(0)
        t = self.v.visit(child)
        p = getattr(child, "_place", None)
        if p is None:
            p, it = self.deepPlace(child)
        else:
            it = bool(getattr(child, "_is_temp", False))
        if p is not None:
            self.setPlace(ctx, p, it)
            log_semantic(f"visitExpression: Set place for ctx={ctx} -> place={p}, is_temp={it}")
        return t

    @log_function
    def visitExprNoAssign(self, ctx):
        if ctx.getChildCount() == 0:
            return None
        child = ctx.getChild(0)
        t = self.v.visit(child)
        p = getattr(child, "_place", None)
        if p is None:
            p, it = self.deepPlace(child)
        else:
            it = bool(getattr(child, "_is_temp", False))
        if p is not None:
            self.setPlace(ctx, p, it)
            log_semantic(f"visitExprNoAssign: Set place for ctx={ctx} -> place={p}, is_temp={it}")
        return t

    # ---------- Primarios ----------
    @log_function
    def visitPrimaryExpr(self, ctx):
        # literalExpr | leftHandSide | '(' expression ')'
        if hasattr(ctx, "literalExpr") and ctx.literalExpr() is not None:
            return self.v.visit(ctx.literalExpr())
        if hasattr(ctx, "leftHandSide") and ctx.leftHandSide() is not None:
            return self.v.visit(ctx.leftHandSide())
        # Paréntesis: propagar place del hijo
        if ctx.getChildCount() == 3 and ctx.getChild(0).getText() == '(':
            t = self.v.visit(ctx.expression())
            ch = ctx.expression()
            p = self.getPlace(ch)
            if p is not None:
                self.setPlace(ctx, p, self.isTempNode(ch))
                log_semantic(f"visitPrimaryExpr: Parentheses, propagated place={p}, is_temp={self.isTempNode(ch)}")
            return t
        return self.v.visitChildren(ctx)

    @log_function
    def visitLiteralExpr(self, ctx):
        if hasattr(ctx, "arrayLiteral") and ctx.arrayLiteral() is not None:
            return self.visitArrayLiteral(ctx.arrayLiteral())
        value = ctx.getText()
        log_semantic(f"visitLiteralExpr: Literal detected: {value}")
        t = validateLiteral(value, self.v.errors, ctx)
        self.setPlace(ctx, value, False)
        log_semantic(f"visitLiteralExpr: Set place for ctx={ctx} -> place={value}, is_temp=False")
        return t

    @log_function
    def visitIdentifierExpr(self, ctx):
        name = ctx.getText()
        log_semantic(f"Identifier used: {name}")
        sym = self.v.scopeManager.lookup(name)
        if sym is None:
            self.v.appendErr(SemanticError(
                f"Identificador '{name}' no está declarado.",
                line=ctx.start.line, column=ctx.start.column))
            return ErrorType()

        if sym.category == SymbolCategory.FUNCTION:
            # Tipo de función (para el sistema de tipos)
            rtype = sym.return_type if sym.return_type is not None else VoidType()
            ftype = FunctionType(sym.param_types, rtype)

            # Guardamos el label para llamadas directas si aplica
            try:
                setattr(ftype, "_label", getattr(sym, "label", None) or f"f_{sym.name}")
            except Exception:
                pass

            # ¿Esta función necesita closure? (tiene capturas reales)
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
                f_label = getattr(ftype, "_label", f"f_{sym.name}")
                self.v.emitter.emit(Op.MKCLOS, arg1=f_label, arg2=env_t, res=clos_t)

                self.setPlace(ctx, clos_t, True)
                log_semantic(f"visitIdentifierExpr: Closure created for {name} -> place={clos_t}")
                try:
                    setattr(ftype, "_closure_place", clos_t)
                except Exception:
                    pass
                return ftype

            self.setPlace(ctx, name, False)
            log_semantic(f"visitIdentifierExpr: Function identifier {name} -> place={name}")
            return ftype

        # Captura de variables externas si estamos dentro de una función
        if self.v.fn_ctx_stack:
            curr_fn_ctx = self.v.fn_ctx_stack[-1]
            curr_fn_scope_id = curr_fn_ctx["scope_id"]
            if sym.scope_id < curr_fn_scope_id:
                try:
                    tstr = str(sym.type)
                except Exception:
                    tstr = "<type>"
                curr_fn_ctx["captures"].add((sym.name, tstr, sym.scope_id))
                log_semantic(f"visitIdentifierExpr: Captured variable {name} from outer scope")

        self.setPlace(ctx, name, False)
        log_semantic(f"visitIdentifierExpr: Variable identifier {name} -> place={name}")
        return sym.type

    @log_function
    def visitArrayLiteral(self, ctx):
        expr_ctxs = list(ctx.expression())
        if not expr_ctxs:
            self.v.appendErr(SemanticError(
                "Arreglo vacío sin tipo explícito no soportado aún.",
                line=ctx.start.line, column=ctx.start.column))
            return ErrorType()

        # 1) Validar tipos de elementos
        elem_types = [self.v.visit(e) for e in expr_ctxs]
        if any(t is None for t in elem_types):
            return ErrorType()
        first = elem_types[0]
        if isinstance(first, ErrorType):
            return ErrorType()

        def same(a, b):
            if isinstance(a, ArrayType) and isinstance(b, ArrayType):
                return same(a.elem_type, b.elem_type)
            if isinstance(a, ClassType) and isinstance(b, ClassType):
                return a.name == b.name
            prims = (IntegerType, StringType, BoolType, FloatType, VoidType, NullType, ErrorType)
            return isinstance(a, prims) and isinstance(b, prims) and a.__class__ is b.__class__

        if not all(same(t, first) for t in elem_types):
            self.v.appendErr(SemanticError(
                f"Elementos de arreglo con tipos inconsistentes: {[str(t) for t in elem_types]}",
                line=ctx.start.line, column=ctx.start.column))
            return ErrorType()

        arr_t = ArrayType(first)
        try:
            arr_t._literal_len = len(expr_ctxs)
        except Exception:
            pass

        # 2) EMISIÓN TAC para literal de lista
        t_list = self.v.emitter.temp_pool.newTemp("ref")
        n_elems = len(expr_ctxs)
        self.v.emitter.emitNewList(t_list, n_elems)

        for k, ek in enumerate(expr_ctxs):
            # visitar el elemento con el visitor real
            self.v.visit(ek)

            # recuperar el place del elemento
            elem_place = getattr(ek, "_place", None)
            if elem_place is None:
                try:
                    elem_place = ek.getText()
                except Exception:
                    elem_place = "<undef>"

            self.v.emitter.emit(Op.INDEX_STORE, arg1=t_list, res=elem_place, label=k)

            # libera temporal del elemento si lo fue
            self.freeIfTemp(ek, elem_types[k])

        self.setPlace(ctx, t_list, True)
        log_semantic(f"visitArrayLiteral: Array literal -> place={t_list}, type={arr_t}")
        return arr_t


    @log_function
    def visitThisExpr(self, ctx):
        if not self.v.in_method or not self.v.class_stack:
            self.v.appendErr(SemanticError(
                "'this' solo puede usarse dentro de métodos de clase.",
                line=ctx.start.line, column=ctx.start.column))
            log_semantic("visitThisExpr: 'this' used outside method, error emitted")
            return ErrorType()
        self.setPlace(ctx, "this", False)
        cls_name = self.v.class_stack[-1]
        log_semantic(f"visitThisExpr: 'this' in class {cls_name} -> place='this'")
        return ClassType(cls_name)

    # ---------- Operadores con emisión TAC ----------
    @log_function
    def visitAdditiveExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        left_type = self.v.visit(children[0])
        left_node = children[0]
        left_place = self.getPlace(left_node) or self.deepPlace(left_node)[0] or left_node.getText()

        i = 1
        current_type = left_type
        current_place = left_place
        current_node = left_node

        while i < len(children):
            op_txt = children[i].getText()
            right_node = children[i + 1]
            right_type = self.v.visit(right_node)
            right_place = self.getPlace(right_node) or self.deepPlace(right_node)[0] or right_node.getText()

            res_type = resultArithmetic(current_type, right_type, op_txt) if op_txt != '%' else resultModulo(current_type, right_type)
            if isinstance(res_type, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Operación aritmética inválida: {current_type} {op_txt} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                log_semantic(f"visitAdditiveExpr: Invalid arithmetic {current_type} {op_txt} {right_type}")
                current_type = ErrorType()
            else:
                t = self.v.emitter.temp_pool.newTemp(self.typeToTempKind(res_type))
                self.v.emitter.emit(Op.BINARY, arg1=current_place, arg2=right_place, res=t, label=op_txt)
                log_semantic(f"visitAdditiveExpr: {current_place} {op_txt} {right_place} -> {t}, type={res_type}")
                self.freeIfTemp(current_node, current_type)
                self.freeIfTemp(right_node, right_type)
                current_place = t
                current_node = ctx
                current_type = res_type
            i += 2

        self.setPlace(ctx, current_place, str(current_place).startswith("t"))
        return current_type

    @log_function
    def visitMultiplicativeExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        left_type = self.v.visit(children[0])
        left_node = children[0]
        left_place = self.getPlace(left_node) or self.deepPlace(left_node)[0] or left_node.getText()

        i = 1
        current_type = left_type
        current_place = left_place
        current_node = left_node

        while i < len(children):
            op_txt = children[i].getText()
            right_node = children[i + 1]
            right_type = self.v.visit(right_node)
            right_place = self.getPlace(right_node) or self.deepPlace(right_node)[0] or right_node.getText()

            res_type = resultModulo(current_type, right_type) if op_txt == '%' else resultArithmetic(current_type, right_type, op_txt)

            if isinstance(res_type, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Operación multiplicativa inválida: {current_type} {op_txt} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                log_semantic(f"visitMultiplicativeExpr: Invalid operation {current_type} {op_txt} {right_type}")
                current_type = ErrorType()
            else:
                t = self.v.emitter.temp_pool.newTemp(self.typeToTempKind(res_type))
                self.v.emitter.emit(Op.BINARY, arg1=current_place, arg2=right_place, res=t, label=op_txt)
                log_semantic(f"visitMultiplicativeExpr: {current_place} {op_txt} {right_place} -> {t}, type={res_type}")
                self.freeIfTemp(current_node, current_type)
                self.freeIfTemp(right_node, right_type)
                current_place = t
                current_node = ctx
                current_type = res_type
            i += 2

        self.setPlace(ctx, current_place, str(current_place).startswith("t"))
        return current_type

    @log_function
    def visitRelationalExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        left_node = children[0]
        left_type = self.v.visit(left_node)
        left_place = self.getPlace(left_node) or self.deepPlace(left_node)[0] or left_node.getText()

        i = 1
        last_type = left_type
        last_place = left_place
        last_node = left_node
        final_type = None
        final_place = last_place

        while i < len(children):
            op_txt = children[i].getText()
            right_node = children[i + 1]
            right_type = self.v.visit(right_node)
            right_place = self.getPlace(right_node) or self.deepPlace(right_node)[0] or right_node.getText()

            res = resultRelational(last_type, right_type)
            if isinstance(res, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Comparación no válida: {last_type} {op_txt} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                log_semantic(f"visitRelationalExpr: Invalid comparison {last_type} {op_txt} {right_type}")
                final_type = ErrorType()
                final_place = last_place
            else:
                t = self.v.emitter.temp_pool.newTemp(self.typeToTempKind(res))
                self.v.emitter.emit(Op.BINARY, arg1=last_place, arg2=right_place, res=t, label=op_txt)
                log_semantic(f"visitRelationalExpr: {last_place} {op_txt} {right_place} -> {t}, type={res}")
                self.freeIfTemp(last_node, last_type)
                self.freeIfTemp(right_node, right_type)
                final_type = res
                final_place = t
                last_node = ctx
            last_type = right_type
            last_place = right_place
            i += 2

        self.setPlace(ctx, final_place, str(final_place).startswith("t"))
        return final_type if final_type is not None else last_type

    @log_function
    def visitEqualityExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        left_node = children[0]
        left_type = self.v.visit(left_node)
        left_place = self.getPlace(left_node) or self.deepPlace(left_node)[0] or left_node.getText()

        i = 1
        last_type = left_type
        last_place = left_place
        last_node = left_node
        final_type = None
        final_place = last_place

        while i < len(children):
            op_txt = children[i].getText()
            right_node = children[i + 1]
            right_type = self.v.visit(right_node)
            right_place = self.getPlace(right_node) or self.deepPlace(right_node)[0] or right_node.getText()

            res = resultEquality(last_type, right_type)
            if isinstance(res, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Igualdad no válida: {last_type} {op_txt} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                log_semantic(f"visitEqualityExpr: Invalid equality {last_type} {op_txt} {right_type}")
                final_type = ErrorType()
                final_place = last_place
            else:
                t = self.v.emitter.temp_pool.newTemp(self.typeToTempKind(res))
                self.v.emitter.emit(Op.BINARY, arg1=last_place, arg2=right_place, res=t, label=op_txt)
                log_semantic(f"visitEqualityExpr: {last_place} {op_txt} {right_place} -> {t}, type={res}")
                self.freeIfTemp(last_node, last_type)
                self.freeIfTemp(right_node, right_type)
                final_type = res
                final_place = t
                last_node = ctx
            last_type = right_type
            last_place = right_place
            i += 2

        self.setPlace(ctx, final_place, str(final_place).startswith("t"))
        return final_type if final_type is not None else last_type

    @log_function
    def visitLogicalAndExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        left_node = children[0]
        left_type = self.v.visit(left_node)
        left_place = self.getPlace(left_node) or self.deepPlace(left_node)[0] or left_node.getText()

        i = 1
        current_type = left_type
        current_place = left_place
        current_node = left_node

        while i < len(children):
            right_node = children[i + 1]
            right_type = self.v.visit(right_node)
            right_place = self.getPlace(right_node) or self.deepPlace(right_node)[0] or right_node.getText()

            res = resultLogical(current_type, right_type)
            if isinstance(res, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Operación lógica inválida: {current_type} && {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                log_semantic(f"visitLogicalAndExpr: Invalid logical AND {current_type} && {right_type}")
                current_type = ErrorType()
            else:
                t = self.v.emitter.temp_pool.newTemp(self.typeToTempKind(res))
                self.v.emitter.emit(Op.BINARY, arg1=current_place, arg2=right_place, res=t, label="&&")
                log_semantic(f"visitLogicalAndExpr: {current_place} && {right_place} -> {t}, type={res}")
                self.freeIfTemp(current_node, current_type)
                self.freeIfTemp(right_node, right_type)
                current_place = t
                current_node = ctx
                current_type = res
            i += 2

        self.setPlace(ctx, current_place, str(current_place).startswith("t"))
        return current_type

    @log_function
    def visitLogicalOrExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        left_node = children[0]
        left_type = self.v.visit(left_node)
        left_place = self.getPlace(left_node) or self.deepPlace(left_node)[0] or left_node.getText()

        i = 1
        current_type = left_type
        current_place = left_place
        current_node = left_node

        while i < len(children):
            right_node = children[i + 1]
            right_type = self.v.visit(right_node)
            right_place = self.getPlace(right_node) or self.deepPlace(right_node)[0] or right_node.getText()

            res = resultLogical(current_type, right_type)
            if isinstance(res, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Operación lógica inválida: {current_type} || {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                log_semantic(f"visitLogicalOrExpr: Invalid logical OR {current_type} || {right_type}")
                current_type = ErrorType()
            else:
                t = self.v.emitter.temp_pool.newTemp(self.typeToTempKind(res))
                self.v.emitter.emit(Op.BINARY, arg1=current_place, arg2=right_place, res=t, label="||")
                log_semantic(f"visitLogicalOrExpr: {current_place} || {right_place} -> {t}, type={res}")
                self.freeIfTemp(current_node, current_type)
                self.freeIfTemp(right_node, right_type)
                current_place = t
                current_node = ctx
                current_type = res
            i += 2

        self.setPlace(ctx, current_place, str(current_place).startswith("t"))
        return current_type

    @log_function
    def visitUnaryExpr(self, ctx):
        if ctx.getChildCount() == 2:
            op_txt = ctx.getChild(0).getText()
            inner_node = ctx.unaryExpr()
            inner_type = self.v.visit(inner_node)
            inner_place = self.getPlace(inner_node) or self.deepPlace(inner_node)[0] or inner_node.getText()

            if op_txt == '-':
                res = resultUnaryMinus(inner_type)
                if isinstance(res, ErrorType):
                    self.v.appendErr(SemanticError(
                        f"Operador '-' inválido sobre tipo {inner_type}",
                        line=ctx.start.line, column=ctx.start.column))
                    log_semantic(f"visitUnaryExpr: Invalid unary minus on {inner_type}")
                    return res
                t = self.v.emitter.temp_pool.newTemp(self.typeToTempKind(res))
                self.v.emitter.emit(Op.UNARY, arg1=inner_place, res=t, label='-')
                log_semantic(f"visitUnaryExpr: -{inner_place} -> {t}, type={res}")
                self.freeIfTemp(inner_node, inner_type)
                self.setPlace(ctx, t, True)
                return res

            if op_txt == '!':
                res = resultUnaryNot(inner_type)
                if isinstance(res, ErrorType):
                    self.v.appendErr(SemanticError(
                        f"Operador '!' inválido sobre tipo {inner_type}",
                        line=ctx.start.line, column=ctx.start.column))
                    log_semantic(f"visitUnaryExpr: Invalid unary NOT on {inner_type}")
                    return res
                t = self.v.emitter.temp_pool.newTemp(self.typeToTempKind(res))
                self.v.emitter.emit(Op.UNARY, arg1=inner_place, res=t, label='!')
                log_semantic(f"visitUnaryExpr: !{inner_place} -> {t}, type={res}")
                self.freeIfTemp(inner_node, inner_type)
                self.setPlace(ctx, t, True)
                return res

            return ErrorType()
        else:
            t = self.v.visit(ctx.primaryExpr())
            p = self.getPlace(ctx.primaryExpr())
            if p is not None:
                self.setPlace(ctx, p, self.isTempNode(ctx.primaryExpr()))
            return t


    # ---------- Objetos / propiedades / new ----------
    @log_function
    def visitNewExpr(self, ctx):
        class_name = ctx.Identifier().getText()
        log_semantic(f"visitNewExpr: Creating instance of class '{class_name}'")

        # Verificación de clase
        if not self.v.class_handler.exists(class_name):
            self.v.appendErr(SemanticError(
                f"Clase '{class_name}' no declarada.",
                line=ctx.start.line, column=ctx.start.column))
            log_semantic(f"visitNewExpr: Error - class '{class_name}' not declared")
            return ErrorType()

        # Recolectar nodos + tipos de argumentos
        args_nodes = list(ctx.arguments().expression()) if ctx.arguments() else []
        arg_types = [self.v.visit(e) for e in args_nodes]

        # Buscar firma de constructor en la jerarquía
        found_sig = None
        seen = set()
        curr = class_name
        while curr and curr not in seen:
            seen.add(curr)
            ctor_sig = self.v.method_registry.lookup(f"{curr}.constructor")
            if ctor_sig is not None:
                found_sig = (curr, ctor_sig)
                break
            base = self.v.class_handler._classes.get(curr).base if hasattr(self.v.class_handler, "_classes") else None
            curr = base

        # Validaciones de aridad/tipos
        if found_sig is None:
            if len(arg_types) != 0:
                self.v.appendErr(SemanticError(
                    f"Constructor de '{class_name}' no declarado; se esperaban 0 argumentos.",
                    line=ctx.start.line, column=ctx.start.column))
                log_semantic(f"visitNewExpr: Error - no constructor for '{class_name}', got {len(arg_types)} args")
        else:
            ctor_owner, (param_types, rtype) = found_sig
            expected = len(param_types) - 1
            if len(arg_types) != expected:
                self.v.appendErr(SemanticError(
                    f"Número de argumentos inválido para '{ctor_owner}.constructor': "
                    f"esperados {expected}, recibidos {len(arg_types)}.",
                    line=ctx.start.line, column=ctx.start.column))
                log_semantic(f"visitNewExpr: Error - invalid number of args for {ctor_owner}.constructor")
            else:
                for i, (pt, at) in enumerate(zip(param_types[1:], arg_types), start=1):
                    if not isAssignable(pt, at):
                        self.v.appendErr(SemanticError(
                            f"Argumento #{i} incompatible en constructor de '{ctor_owner}': "
                            f"no se puede asignar {at} a {pt}.",
                            line=ctx.start.line, column=ctx.start.column))
                        log_semantic(f"visitNewExpr: Error - arg #{i} type mismatch in {ctor_owner}.constructor")

        # === Emisión TAC real ===
        obj_size = 0
        try:
            obj_size = int(self.v.class_handler.get_object_size(class_name))
        except Exception:
            obj_size = 0

        t_obj = self.v.emitter.temp_pool.newTemp("ref")
        self.v.emitter.emit(Op.NEWOBJ, arg1=class_name, arg2=str(obj_size), res=t_obj)
        log_semantic(f"visitNewExpr: NEWOBJ {class_name}, size={obj_size} -> {t_obj}")

        if found_sig is not None:
            ctor_owner, (_param_types, _rtype) = found_sig
            self.v.emitter.emit(Op.PARAM, arg1=t_obj)
            n_params = 1
            for e in args_nodes:
                p, is_tmp = self.deepPlace(e)
                aplace = p or e.getText()
                self.v.emitter.emit(Op.PARAM, arg1=aplace)
                log_semantic(f"visitNewExpr: PARAM {aplace}")
                if is_tmp:
                    self.v.emitter.temp_pool.free(aplace, "*")
                n_params += 1
            f_label = f"f_{ctor_owner}_constructor"
            self.v.emitter.emit(Op.CALL, arg1=f_label, arg2=str(n_params))
            log_semantic(f"visitNewExpr: CALL {f_label}, n_params={n_params}")

        self.setPlace(ctx, t_obj, True)
        return ClassType(class_name)

    @log_function
    def visitPropertyAccessExpr(self, ctx):
        obj_type = self.v.visit(ctx.expression())
        prop_name = ctx.Identifier().getText()
        log_semantic(f"visitPropertyAccessExpr: Accessing '{prop_name}' on {obj_type}")

        if not isinstance(obj_type, ClassType):
            self.v.appendErr(SemanticError(
                f"No se puede acceder a propiedades de tipo '{obj_type}'.",
                line=ctx.start.line, column=ctx.start.column))
            log_semantic(f"visitPropertyAccessExpr: Error - type {obj_type} has no properties")
            return ErrorType()

        class_name = obj_type.name

        # 1) Atributo
        attr_t = self.v.class_handler.get_attribute_type(class_name, prop_name)
        if attr_t is not None:
            log_semantic(f"visitPropertyAccessExpr: Found attribute '{prop_name}' of type {attr_t}")
            return attr_t

        # 2) Método
        def lookupMethodInHierarchy(cls: str, mname: str):
            sig = self.v.method_registry.lookup(f"{cls}.{mname}")
            if sig is not None:
                return cls, sig
            try:
                curr = cls
                seen = set()
                while curr and curr not in seen:
                    seen.add(curr)
                    base = self.v.class_handler._classes.get(curr).base
                    if not base:
                        break
                    sig = self.v.method_registry.lookup(f"{base}.{mname}")
                    if sig is not None:
                        return base, sig
                    curr = base
            except Exception:
                pass
            qname = f"{cls}.{mname}"
            sym = self.v.scopeManager.lookup(qname)
            if sym is not None and sym.category == SymbolCategory.FUNCTION:
                ret_t = sym.return_type if sym.return_type is not None else VoidType()
                return cls, (sym.param_types, ret_t)
            return None, None

        owner, sig = lookupMethodInHierarchy(class_name, prop_name)
        if sig is not None:
            param_types, ret_t = sig
            ret_t = ret_t if ret_t is not None else VoidType()
            params_wo_this = param_types[1:] if len(param_types) > 0 else []
            ftype = FunctionType(params_wo_this, ret_t)
            try:
                setattr(ftype, "_bound_receiver", class_name)
                setattr(ftype, "_decl_owner", owner or class_name)
            except Exception:
                pass
            log_semantic(f"visitPropertyAccessExpr: Found method '{prop_name}' of type {ftype}")
            return ftype

        self.v.appendErr(SemanticError(
            f"Miembro '{prop_name}' no declarado en clase '{class_name}'.",
            line=ctx.start.line, column=ctx.start.column))
        log_semantic(f"visitPropertyAccessExpr: Error - member '{prop_name}' not found in class '{class_name}'")
        return ErrorType()

    @log_function
    def visitLeftHandSide(self, ctx):
        log_semantic("visitLeftHandSide: delegating to lvalues")
        return self.lvalues.visitLeftHandSide(ctx)
