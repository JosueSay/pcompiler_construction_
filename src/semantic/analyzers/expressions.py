from semantic.symbol_kinds import SymbolCategory
from semantic.validators.literal import validateLiteral
from semantic.custom_types import ClassType, VoidType, ErrorType, FunctionType, ArrayType
from semantic.type_system import (
    resultArithmetic, resultModulo, resultRelational, resultEquality,
    resultLogical, resultUnaryMinus, resultUnaryNot, isAssignable
)
from logs.logger import log
from semantic.errors import SemanticError


class ExpressionsAnalyzer:
    """
    Análisis semántico de expresiones (solo tipos, sin emitir TAC).
    """

    def __init__(self, v, lvalues):
        log("\n" + "="*80, channel="semantic")
        log("===== [ExpressionsAnalyzer] Inicio SEMÁNTICO =====", channel="semantic")
        log("="*80 + "\n", channel="semantic")
        self.v = v
        self.lvalues = lvalues

    # ---------- Entradas ----------
    def visitExpression(self, ctx):
        if ctx.getChildCount() == 0:
            return None
        return self.v.visit(ctx.getChild(0))

    def visitExprNoAssign(self, ctx):
        if ctx.getChildCount() == 0:
            return None
        return self.v.visit(ctx.getChild(0))

    # ---------- Primarios ----------
    def visitPrimaryExpr(self, ctx):
        if hasattr(ctx, "literalExpr") and ctx.literalExpr() is not None:
            return self.v.visit(ctx.literalExpr())
        if hasattr(ctx, "leftHandSide") and ctx.leftHandSide() is not None:
            return self.v.visit(ctx.leftHandSide())
        if ctx.getChildCount() == 3 and ctx.getChild(0).getText() == '(':
            return self.v.visit(ctx.expression())
        return self.v.visitChildren(ctx)

    def visitLiteralExpr(self, ctx):
        if hasattr(ctx, "arrayLiteral") and ctx.arrayLiteral() is not None:
            return self.visitArrayLiteral(ctx.arrayLiteral())

        text = ctx.getText()
        t = validateLiteral(text, self.v.errors, ctx)
        setattr(ctx, "_type", t)
        log(f"[literal] {text} -> {t}", channel="semantic")
        return t

    def visitIdentifierExpr(self, ctx):
        name = ctx.getText()
        sym = self.v.scopeManager.lookup(name)
        if sym is None:
            self.v.appendErr(SemanticError(
                f"Identificador '{name}' no está declarado.",
                line=ctx.start.line, column=ctx.start.column))
            log(f"\t[error] id '{name}' no declarado", channel="semantic")
            return ErrorType()

        if sym.category == SymbolCategory.FUNCTION:
            rtype = sym.return_type if sym.return_type else VoidType()
            ftype = FunctionType(sym.param_types, rtype)
            try:
                setattr(ftype, "_label", getattr(sym, "label", None) or f"{sym.name}")
            except Exception:
                pass
            log(f"[func] id '{name}' -> {ftype}", channel="semantic")
            return ftype

        # Registro de capturas para closures
        if self.v.fn_ctx_stack:
            curr_fn_ctx = self.v.fn_ctx_stack[-1]
            curr_fn_scope_id = curr_fn_ctx["scope_id"]
            if sym.scope_id < curr_fn_scope_id:
                try:
                    tstr = str(sym.type)
                except Exception:
                    tstr = "<type>"
                curr_fn_ctx["captures"].add((sym.name, tstr, sym.scope_id))
        return sym.type

    def visitArrayLiteral(self, ctx):
        elems = list(ctx.expression()) if ctx.expression() else []

        if not elems:
            self.v.appendErr(SemanticError(
                "Arreglo vacío no tiene tipo inferible sin anotación.",
                line=ctx.start.line, column=ctx.start.column))
            t = ErrorType()
            setattr(ctx, "_type", t)
            log("\t[error] array vacío -> ErrorType", channel="semantic")
            return t

        first_t = self.v.visit(elems[0])
        elem_t = first_t
        ok = True

        for e in elems[1:]:
            et = self.v.visit(e)
            if et != elem_t:
                self.v.appendErr(SemanticError(
                    f"Literal de arreglo heterogéneo: se esperaba {elem_t}, se encontró {et}.",
                    line=e.start.line, column=e.start.column
                ))
                log(f"\t[error] elemento {e.getText()} tipo {et} != {elem_t}", channel="semantic")
                ok = False

        t = ArrayType(elem_t) if ok else ErrorType()
        setattr(ctx, "_type", t)
        log(f"[array] tipo -> {t}", channel="semantic")
        return t

    def visitThisExpr(self, ctx):
        if not self.v.in_method or not self.v.class_stack:
            self.v.appendErr(SemanticError(
                "'this' solo puede usarse dentro de métodos de clase.",
                line=ctx.start.line, column=ctx.start.column))
            log("\t[error] 'this' fuera de método", channel="semantic")
            return ErrorType()
        cls_name = self.v.class_stack[-1]
        t = ClassType(cls_name)
        log(f"[this] -> {t}", channel="semantic")
        return t

    # ---------- Operadores (solo tipos) ----------
    def visitAdditiveExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        current_type = self.v.visit(children[0])
        i = 1
        while i < len(children):
            op_txt = children[i].getText()
            right_type = self.v.visit(children[i + 1])
            res_type = resultModulo(current_type, right_type) if op_txt == '%' else resultArithmetic(current_type, right_type, op_txt)

            log(f"[additive] {current_type} {op_txt} {right_type} -> {res_type}", channel="semantic")

            if isinstance(res_type, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Operación aritmética inválida: {current_type} {op_txt} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                log(f"\t[error] operación aritmética inválida", channel="semantic")
                return ErrorType()
            current_type = res_type
            i += 2
        return current_type


    def visitMultiplicativeExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        current_type = self.v.visit(children[0])
        i = 1
        while i < len(children):
            op_txt = children[i].getText()
            right_type = self.v.visit(children[i + 1])
            res_type = resultModulo(current_type, right_type) if op_txt == '%' else resultArithmetic(current_type, right_type, op_txt)

            log(f"[multiplicative] {current_type} {op_txt} {right_type} -> {res_type}", channel="semantic")

            if isinstance(res_type, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Operación multiplicativa inválida: {current_type} {op_txt} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                log(f"\t[error] operación multiplicativa inválida", channel="semantic")
                return ErrorType()
            current_type = res_type
            i += 2
        return current_type


    def visitRelationalExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        last_type = self.v.visit(children[0])
        i = 1
        final_type = None
        while i < len(children):
            right_type = self.v.visit(children[i + 1])
            res = resultRelational(last_type, right_type)
            log(f"[relational] {last_type} {children[i].getText()} {right_type} -> {res}", channel="semantic")

            if isinstance(res, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Comparación no válida: {last_type} {children[i].getText()} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                log(f"\t[error] comparación no válida", channel="semantic")
                return ErrorType()
            final_type = res
            last_type = right_type
            i += 2
        return final_type if final_type is not None else last_type


    def visitEqualityExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        last_type = self.v.visit(children[0])
        i = 1
        final_type = None
        while i < len(children):
            right_type = self.v.visit(children[i + 1])
            res = resultEquality(last_type, right_type)
            log(f"[equality] {last_type} {children[i].getText()} {right_type} -> {res}", channel="semantic")

            if isinstance(res, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Igualdad no válida: {last_type} {children[i].getText()} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                log(f"\t[error] igualdad no válida", channel="semantic")
                return ErrorType()
            final_type = res
            last_type = right_type
            i += 2
        return final_type if final_type is not None else last_type


    def visitLogicalAndExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        current_type = self.v.visit(children[0])
        i = 1
        while i < len(children):
            right_type = self.v.visit(children[i + 1])
            res = resultLogical(current_type, right_type)
            log(f"[logical AND] {current_type} && {right_type} -> {res}", channel="semantic")

            if isinstance(res, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Operación lógica inválida: {current_type} && {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                log(f"\t[error] operación lógica AND inválida", channel="semantic")
                return ErrorType()
            current_type = res
            i += 2
        return current_type


    def visitLogicalOrExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        current_type = self.v.visit(children[0])
        i = 1
        while i < len(children):
            right_type = self.v.visit(children[i + 1])
            res = resultLogical(current_type, right_type)
            log(f"[logical OR] {current_type} || {right_type} -> {res}", channel="semantic")

            if isinstance(res, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Operación lógica inválida: {current_type} || {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                log(f"\t[error] operación lógica OR inválida", channel="semantic")
                return ErrorType()
            current_type = res
            i += 2
        return current_type


    def visitUnaryExpr(self, ctx):
        if ctx.getChildCount() == 2:
            op_txt = ctx.getChild(0).getText()
            inner_type = self.v.visit(ctx.unaryExpr())

            if op_txt == '-':
                res = resultUnaryMinus(inner_type)
                log(f"[unary -] {inner_type} -> {res}", channel="semantic")
                if isinstance(res, ErrorType):
                    self.v.appendErr(SemanticError(
                        f"Operador '-' inválido sobre tipo {inner_type}",
                        line=ctx.start.line, column=ctx.start.column))
                    log("\t[error] unary - inválido", channel="semantic")
                return res

            if op_txt == '!':
                res = resultUnaryNot(inner_type)
                log(f"[unary !] {inner_type} -> {res}", channel="semantic")
                if isinstance(res, ErrorType):
                    self.v.appendErr(SemanticError(
                        f"Operador '!' inválido sobre tipo {inner_type}",
                        line=ctx.start.line, column=ctx.start.column))
                    log("\t[error] unary ! inválido", channel="semantic")
                return res

            return ErrorType()
        else:
            return self.v.visit(ctx.primaryExpr())


    # ---------- Objetos / propiedades / new (solo tipos) ----------
    def visitNewExpr(self, ctx):
        class_name = ctx.Identifier().getText()
        log(f"[new] Creando instancia de clase '{class_name}'", channel="semantic")

        if not self.v.class_handler.exists(class_name):
            self.v.appendErr(SemanticError(
                f"Clase '{class_name}' no declarada.",
                line=ctx.start.line, column=ctx.start.column))
            log(f"\t[error] clase '{class_name}' no declarada", channel="semantic")
            return ErrorType()

        args_nodes = list(ctx.arguments().expression()) if ctx.arguments() else []
        arg_types = [self.v.visit(e) for e in args_nodes]

        # Buscar firma de constructor en la jerarquía
        found_sig = None
        mt = self.v.method_registry.lookupMethod(f"{class_name}.constructor")
        if mt is not None:
            found_sig = (class_name, mt)
        else:
            for base in self.v.class_handler.iterBases(class_name):
                mt = self.v.method_registry.lookupMethod(f"{base}.constructor")
                if mt is not None:
                    found_sig = (base, mt)
                    break

        if found_sig is None:
            if len(arg_types) != 0:
                self.v.appendErr(SemanticError(
                    f"Constructor de '{class_name}' no declarado; se esperaban 0 argumentos.",
                    line=ctx.start.line, column=ctx.start.column))
                log(f"\t[error] número de argumentos inválido para '{class_name}'", channel="semantic")
        else:
            ctor_owner, (param_types, _rtype) = found_sig
            expected = len(param_types) - 1   # sin 'this'
            if len(arg_types) != expected:
                self.v.appendErr(SemanticError(
                    f"Número de argumentos inválido para '{ctor_owner}.constructor': "
                    f"esperados {expected}, recibidos {len(arg_types)}.",
                    line=ctx.start.line, column=ctx.start.column))
                log(f"\t[error] número de argumentos inválido para '{ctor_owner}.constructor'", channel="semantic")
            else:
                for i, (pt, at) in enumerate(zip(param_types[1:], arg_types), start=1):
                    if not isAssignable(pt, at):
                        self.v.appendErr(SemanticError(
                            f"Argumento #{i} incompatible en constructor de '{ctor_owner}': "
                            f"no se puede asignar {at} a {pt}.",
                            line=ctx.start.line, column=ctx.start.column))
                        log(f"\t[error] argumento #{i} incompatible en constructor", channel="semantic")
        return ClassType(class_name)


    def visitPropertyAccessExpr(self, ctx):
        obj_type = self.v.visit(ctx.expression())
        prop_name = ctx.Identifier().getText()
        log(f"[property] Accediendo a '{prop_name}' en {obj_type}", channel="semantic")

        if not isinstance(obj_type, ClassType):
            self.v.appendErr(SemanticError(
                f"No se puede acceder a propiedades de tipo '{obj_type}'.",
                line=ctx.start.line, column=ctx.start.column))
            log(f"\t[error] intento de acceso a propiedad en tipo no-clase", channel="semantic")
            return ErrorType()

        class_name = obj_type.name

        # Atributo
        attr_t = self.v.class_handler.getAttributeType(class_name, prop_name)
        if attr_t is not None:
            return attr_t

        # Método en la jerarquía
        def lookupMethodInHierarchy(cls_name: str, mname: str):
            mt = self.v.method_registry.lookupMethod(f"{cls_name}.{mname}")
            if mt is not None:
                return cls_name, mt
            for b in self.v.class_handler.iterBases(cls_name):
                mt = self.v.method_registry.lookupMethod(f"{b}.{mname}")
                if mt is not None:
                    return b, mt
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
            log(f"[method] Acceso a método '{prop_name}' de '{class_name}' -> {ftype}", channel="semantic")
            return ftype

        self.v.appendErr(SemanticError(
            f"Miembro '{prop_name}' no declarado en clase '{class_name}'.",
            line=ctx.start.line, column=ctx.start.column))
        log(f"\t[error] miembro '{prop_name}' no encontrado en '{class_name}'", channel="semantic")
        return ErrorType()


    def visitLeftHandSide(self, ctx):
        log(f"[lvalue] Analizando LHS", channel="semantic")
        return self.lvalues.visitLeftHandSide(ctx)
