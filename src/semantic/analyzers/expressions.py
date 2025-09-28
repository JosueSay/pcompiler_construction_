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
from logs.logger_semantic import log_semantic
from semantic.errors import SemanticError
from ir.tac import Op


class ExpressionsAnalyzer:
    def __init__(self, v, lvalues):
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
            setattr(node, "_place", place)
            setattr(node, "_is_temp", is_temp)
        except Exception:
            pass

    def getPlace(self, node) -> str | None:
        return getattr(node, "_place", None)

    def isTempNode(self, node) -> bool:
        return bool(getattr(node, "_is_temp", False))

    def newTempFor(self, t) -> str:
        kind = self.typeToTempKind(t)
        return self.v.emitter.temp_pool.newTemp(kind)

    def freeIfTemp(self, node, t_hint=None) -> None:
        if not self.isTempNode(node):
            return
        place = self.getPlace(node)
        if place is None:
            return
        kind = self.typeToTempKind(t_hint) if t_hint is not None else "*"
        self.v.emitter.temp_pool.free(place, kind)

    def deepPlace(self, node) -> tuple[str | None, bool]:
        """Busca recursivamente un _place ya calculado en hijos (sin volver a visitar)."""
        if node is None:
            return None, False
        p = getattr(node, "_place", None)
        if p is not None:
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
        return t

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
        return t

    # ---------- Primarios ----------
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
            return t
        return self.v.visitChildren(ctx)

    # Literales e identificadores
    def visitLiteralExpr(self, ctx):
        if hasattr(ctx, "arrayLiteral") and ctx.arrayLiteral() is not None:
            return self.visitArrayLiteral(ctx.arrayLiteral())
        value = ctx.getText()
        log_semantic(f"Literal detected: {value}")
        t = validateLiteral(value, self.v.errors, ctx)
        self.setPlace(ctx, value, False)
        return t

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
                # Materializamos la closure: ENV = mkenv(x,y,...) ; C = mkclos f_label, ENV
                # 1) construir lista textual de lugares para las capturas (por ahora, por nombre)
                args_txt = ",".join(captured) if captured else ""
                env_t = self.v.emitter.temp_pool.newTemp("ref")
                self.v.emitter.emit(Op.MKENV, arg1=args_txt, res=env_t)

                clos_t = self.v.emitter.temp_pool.newTemp("ref")
                f_label = getattr(ftype, "_label", f"f_{sym.name}")
                self.v.emitter.emit(Op.MKCLOS, arg1=f_label, arg2=env_t, res=clos_t)

                # El identificador produce una *closure value*
                self.setPlace(ctx, clos_t, True)
                try:
                    setattr(ftype, "_closure_place", clos_t)  # marcador para callc
                except Exception:
                    pass
                return ftype

            # Si no hay capturas, el identificador queda como nombre (llamada directa con CALL)
            self.setPlace(ctx, name, False)
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

        self.setPlace(ctx, name, False)
        return sym.type

    def visitArrayLiteral(self, ctx):
        expr_ctxs = list(ctx.expression())
        if not expr_ctxs:
            self.v.appendErr(SemanticError(
                "Arreglo vacío sin tipo explícito no soportado aún.",
                line=ctx.start.line, column=ctx.start.column))
            return ErrorType()
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

        self.setPlace(ctx, ctx.getText(), False)
        return arr_t

    def visitThisExpr(self, ctx):
        if not self.v.in_method or not self.v.class_stack:
            self.v.appendErr(SemanticError(
                "'this' solo puede usarse dentro de métodos de clase.",
                line=ctx.start.line, column=ctx.start.column))
            return ErrorType()
        self.setPlace(ctx, "this", False)
        return ClassType(self.v.class_stack[-1])

    # ---------- Operadores con emisión TAC ----------
    def visitAdditiveExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        left_type = self.v.visit(children[0])
        left_node = children[0]
        # left_place = self.getPlace(left_node) or left_node.getText()
        left_place  = self.getPlace(left_node)  or self.deepPlace(left_node)[0]  or left_node.getText()

        i = 1
        current_type = left_type
        current_place = left_place
        current_node = left_node

        while i < len(children):
            op_txt = children[i].getText()
            right_node = children[i + 1]
            right_type = self.v.visit(right_node)
            # right_place = self.getPlace(right_node) or right_node.getText()
            right_place = self.getPlace(right_node) or self.deepPlace(right_node)[0] or right_node.getText()

            res_type = resultArithmetic(current_type, right_type, op_txt) if op_txt != '%' else resultModulo(current_type, right_type)
            if isinstance(res_type, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Operación aritmética inválida: {current_type} {op_txt} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                current_type = ErrorType()
            else:
                t = self.v.emitter.temp_pool.newTemp(self.typeToTempKind(res_type))
                self.v.emitter.emit(Op.BINARY, arg1=current_place, arg2=right_place, res=t, label=op_txt)
                self.freeIfTemp(current_node, current_type)
                self.freeIfTemp(right_node, right_type)
                current_place = t
                current_node = ctx
                current_type = res_type
            i += 2

        self.setPlace(ctx, current_place, str(current_place).startswith("t"))
        return current_type

    def visitMultiplicativeExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        left_type = self.v.visit(children[0])
        left_node = children[0]
        # left_place = self.getPlace(left_node) or left_node.getText()
        left_place  = self.getPlace(left_node)  or self.deepPlace(left_node)[0]  or left_node.getText()

        i = 1
        current_type = left_type
        current_place = left_place
        current_node = left_node

        while i < len(children):
            op_txt = children[i].getText()
            right_node = children[i + 1]
            right_type = self.v.visit(right_node)
            # right_place = self.getPlace(right_node) or right_node.getText()
            right_place = self.getPlace(right_node) or self.deepPlace(right_node)[0] or right_node.getText()

            res_type = resultModulo(current_type, right_type) if op_txt == '%' else resultArithmetic(current_type, right_type, op_txt)

            if isinstance(res_type, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Operación multiplicativa inválida: {current_type} {op_txt} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                current_type = ErrorType()
            else:
                t = self.v.emitter.temp_pool.newTemp(self.typeToTempKind(res_type))
                self.v.emitter.emit(Op.BINARY, arg1=current_place, arg2=right_place, res=t, label=op_txt)
                self.freeIfTemp(current_node, current_type)
                self.freeIfTemp(right_node, right_type)
                current_place = t
                current_node = ctx
                current_type = res_type
            i += 2

        self.setPlace(ctx, current_place, str(current_place).startswith("t"))
        return current_type

    def visitRelationalExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        left_node = children[0]
        left_type = self.v.visit(left_node)
        # left_place = self.getPlace(left_node) or left_node.getText()
        left_place  = self.getPlace(left_node)  or self.deepPlace(left_node)[0]  or left_node.getText()

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
            # right_place = self.getPlace(right_node) or right_node.getText()
            right_place = self.getPlace(right_node) or self.deepPlace(right_node)[0] or right_node.getText()

            res = resultRelational(last_type, right_type)
            if isinstance(res, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Comparación no válida: {last_type} {op_txt} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                final_type = ErrorType()
                final_place = last_place
            else:
                t = self.v.emitter.temp_pool.newTemp(self.typeToTempKind(res))
                self.v.emitter.emit(Op.BINARY, arg1=last_place, arg2=right_place, res=t, label=op_txt)
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

    def visitEqualityExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        left_node = children[0]
        left_type = self.v.visit(left_node)
        # left_place = self.getPlace(left_node) or left_node.getText()
        left_place  = self.getPlace(left_node)  or self.deepPlace(left_node)[0]  or left_node.getText()

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
            # right_place = self.getPlace(right_node) or right_node.getText()
            right_place = self.getPlace(right_node) or self.deepPlace(right_node)[0] or right_node.getText()

            res = resultEquality(last_type, right_type)
            if isinstance(res, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Igualdad no válida: {last_type} {op_txt} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                final_type = ErrorType()
                final_place = last_place
            else:
                t = self.v.emitter.temp_pool.newTemp(self.typeToTempKind(res))
                self.v.emitter.emit(Op.BINARY, arg1=last_place, arg2=right_place, res=t, label=op_txt)
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

    def visitLogicalAndExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        left_node = children[0]
        left_type = self.v.visit(left_node)
        # left_place = self.getPlace(left_node) or left_node.getText()
        left_place  = self.getPlace(left_node)  or self.deepPlace(left_node)[0]  or left_node.getText()

        i = 1
        current_type = left_type
        current_place = left_place
        current_node = left_node

        while i < len(children):
            right_node = children[i + 1]
            right_type = self.v.visit(right_node)
            # right_place = self.getPlace(right_node) or right_node.getText()
            right_place = self.getPlace(right_node) or self.deepPlace(right_node)[0] or right_node.getText()

            res = resultLogical(current_type, right_type)
            if isinstance(res, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Operación lógica inválida: {current_type} && {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                current_type = ErrorType()
            else:
                t = self.v.emitter.temp_pool.newTemp(self.typeToTempKind(res))
                self.v.emitter.emit(Op.BINARY, arg1=current_place, arg2=right_place, res=t, label="&&")
                self.freeIfTemp(current_node, current_type)
                self.freeIfTemp(right_node, right_type)
                current_place = t
                current_node = ctx
                current_type = res
            i += 2

        self.setPlace(ctx, current_place, str(current_place).startswith("t"))
        return current_type

    def visitLogicalOrExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        left_node = children[0]
        left_type = self.v.visit(left_node)
        # left_place = self.getPlace(left_node) or left_node.getText()
        left_place  = self.getPlace(left_node)  or self.deepPlace(left_node)[0]  or left_node.getText()

        i = 1
        current_type = left_type
        current_place = left_place
        current_node = left_node

        while i < len(children):
            right_node = children[i + 1]
            right_type = self.v.visit(right_node)
            # right_place = self.getPlace(right_node) or right_node.getText()
            right_place = self.getPlace(right_node) or self.deepPlace(right_node)[0] or right_node.getText()

            res = resultLogical(current_type, right_type)
            if isinstance(res, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Operación lógica inválida: {current_type} || {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                current_type = ErrorType()
            else:
                t = self.v.emitter.temp_pool.newTemp(self.typeToTempKind(res))
                self.v.emitter.emit(Op.BINARY, arg1=current_place, arg2=right_place, res=t, label="||")
                self.freeIfTemp(current_node, current_type)
                self.freeIfTemp(right_node, right_type)
                current_place = t
                current_node = ctx
                current_type = res
            i += 2

        self.setPlace(ctx, current_place, str(current_place).startswith("t"))
        return current_type

    def visitUnaryExpr(self, ctx):
        if ctx.getChildCount() == 2:
            op_txt = ctx.getChild(0).getText()
            inner_node = ctx.unaryExpr()
            inner_type = self.v.visit(inner_node)
            # inner_place = self.getPlace(inner_node) or inner_node.getText()
            inner_place = self.getPlace(inner_node) or self.deepPlace(inner_node)[0] or inner_node.getText()


            if op_txt == '-':
                res = resultUnaryMinus(inner_type)
                if isinstance(res, ErrorType):
                    self.v.appendErr(SemanticError(
                        f"Operador '-' inválido sobre tipo {inner_type}",
                        line=ctx.start.line, column=ctx.start.column))
                    return res
                t = self.v.emitter.temp_pool.newTemp(self.typeToTempKind(res))
                self.v.emitter.emit(Op.UNARY, arg1=inner_place, res=t, label='-')
                self.freeIfTemp(inner_node, inner_type)
                self.setPlace(ctx, t, True)
                return res

            if op_txt == '!':
                res = resultUnaryNot(inner_type)
                if isinstance(res, ErrorType):
                    self.v.appendErr(SemanticError(
                        f"Operador '!' inválido sobre tipo {inner_type}",
                        line=ctx.start.line, column=ctx.start.column))
                    return res
                t = self.v.emitter.temp_pool.newTemp(self.typeToTempKind(res))
                self.v.emitter.emit(Op.UNARY, arg1=inner_place, res=t, label='!')
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
    def visitNewExpr(self, ctx):
        class_name = ctx.Identifier().getText()

        # Verificación de clase
        if not self.v.class_handler.exists(class_name):
            self.v.appendErr(SemanticError(
                f"Clase '{class_name}' no declarada.",
                line=ctx.start.line, column=ctx.start.column))
            return ErrorType()

        # Recolectar tipos de argumentos
        arg_types = []
        if ctx.arguments():
            for e in ctx.arguments().expression():
                arg_types.append(self.v.visit(e))

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

        if found_sig is None:
            if len(arg_types) != 0:
                self.v.appendErr(SemanticError(
                    f"Constructor de '{class_name}' no declarado; se esperaban 0 argumentos.",
                    line=ctx.start.line, column=ctx.start.column))
        else:
            ctor_owner, (param_types, rtype) = found_sig
            expected = len(param_types) - 1  # quitar 'this'
            if len(arg_types) != expected:
                self.v.appendErr(SemanticError(
                    f"Número de argumentos inválido para '{ctor_owner}.constructor': "
                    f"esperados {expected}, recibidos {len(arg_types)}.",
                    line=ctx.start.line, column=ctx.start.column))
            else:
                for i, (pt, at) in enumerate(zip(param_types[1:], arg_types), start=1):
                    if not isAssignable(pt, at):
                        self.v.appendErr(SemanticError(
                            f"Argumento #{i} incompatible en constructor de '{ctor_owner}': "
                            f"no se puede asignar {at} a {pt}.",
                            line=ctx.start.line, column=ctx.start.column))

        # Emisión real de new/ctor llegará en la etapa de RA; aquí solo tipo/place
        self.setPlace(ctx, f"new {class_name}()", False)
        return ClassType(class_name)

    def visitPropertyAccessExpr(self, ctx):
        """
        expression '.' Identifier
        - Si es atributo: devuelve su tipo (con herencia).
        - Si es método: devuelve FunctionType(params_sin_this, ret), buscando en la jerarquía.
        La emisión de lectura/escritura/llamada se maneja fuera (LValues / Funcs).
        """
        obj_type = self.v.visit(ctx.expression())

        if not isinstance(obj_type, ClassType):
            self.v.appendErr(SemanticError(
                f"No se puede acceder a propiedades de tipo '{obj_type}'.",
                line=ctx.start.line, column=ctx.start.column))
            return ErrorType()

        class_name = obj_type.name
        prop_name = ctx.Identifier().getText()

        # 1) Atributo (con herencia)
        attr_t = self.v.class_handler.get_attribute_type(class_name, prop_name)
        if attr_t is not None:
            return attr_t

        # 2) Método en esta clase o en bases (method_registry y, como respaldo, symbol table)
        #    Construimos FunctionType quitando 'this' del inicio si existe.
        def _lookup_method_in_hierarchy(cls: str, mname: str):
            # registry directo
            sig = self.v.method_registry.lookup(f"{cls}.{mname}")
            if sig is not None:
                return cls, sig
            # subir a bases
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
            # respaldo: símbolo global "Clase.metodo"
            qname = f"{cls}.{mname}"
            sym = self.v.scopeManager.lookup(qname)
            if sym is not None and sym.category == SymbolCategory.FUNCTION:
                ret_t = sym.return_type if sym.return_type is not None else VoidType()
                # param_types ya incluiría 'this' como primero
                return cls, (sym.param_types, ret_t)
            return None, None

        owner, sig = _lookup_method_in_hierarchy(class_name, prop_name)
        if sig is not None:
            param_types, ret_t = sig
            ret_t = ret_t if ret_t is not None else VoidType()
            # quitar 'this' si viene
            params_wo_this = param_types[1:] if len(param_types) > 0 else []
            ftype = FunctionType(params_wo_this, ret_t)
            try:
                setattr(ftype, "_bound_receiver", class_name)
                setattr(ftype, "_decl_owner", owner or class_name)
            except Exception:
                pass
            return ftype

        # 3) Ninguno: error
        self.v.appendErr(SemanticError(
            f"Miembro '{prop_name}' no declarado en clase '{class_name}'.",
            line=ctx.start.line, column=ctx.start.column))
        return ErrorType()

    def visitLeftHandSide(self, ctx):
        return self.lvalues.visitLeftHandSide(ctx)
