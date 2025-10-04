from semantic.symbol_kinds import SymbolCategory
from semantic.validators.literal import validateLiteral
from semantic.custom_types import ClassType,VoidType, ErrorType, FunctionType
from semantic.type_system import (
    resultArithmetic, resultModulo, resultRelational, resultEquality,
    resultLogical, resultUnaryMinus, resultUnaryNot, isAssignable
)
from logs.logger import log, logFunction
from semantic.errors import SemanticError


class ExpressionsAnalyzer:
    """
    Análisis **semántico** de expresiones (solo tipos, sin emitir TAC).
    - Resuelve tipos de literales, identificadores, arrays, `this`, `new`.
    - Calcula tipos resultado de operadores unarios/binarios.
    - Verifica asignabilidad de argumentos en llamadas/constructores.
    - Anota metadatos mínimos útiles para la pasada TAC (p.ej. `_label` en funciones).
    """

    @logFunction(channel="semantic")
    def __init__(self, v, lvalues):
        log("===== [Expressions.py] Inicio (SEMÁNTICO) =====", channel="semantic")
        self.v = v
        self.lvalues = lvalues

    # ---------- Entradas de dispatch (solo tipos) ----------
    @logFunction(channel="semantic")
    def visitExpression(self, ctx):
        if ctx.getChildCount() == 0:
            return None
        return self.v.visit(ctx.getChild(0))

    @logFunction(channel="semantic")
    def visitExprNoAssign(self, ctx):
        if ctx.getChildCount() == 0:
            return None
        return self.v.visit(ctx.getChild(0))

    # ---------- Primarios ----------
    @logFunction(channel="semantic")
    def visitPrimaryExpr(self, ctx):
        # literalExpr | leftHandSide | '(' expression ')'
        if hasattr(ctx, "literalExpr") and ctx.literalExpr() is not None:
            return self.v.visit(ctx.literalExpr())
        if hasattr(ctx, "leftHandSide") and ctx.leftHandSide() is not None:
            return self.v.visit(ctx.leftHandSide())
        if ctx.getChildCount() == 3 and ctx.getChild(0).getText() == '(':
            return self.v.visit(ctx.expression())
        return self.v.visitChildren(ctx)

    @logFunction(channel="semantic")
    def visitLiteralExpr(self, ctx):
        # Si el literal es realmente un array, delega:
        if hasattr(ctx, "arrayLiteral") and ctx.arrayLiteral() is not None:
            return self.visitArrayLiteral(ctx.arrayLiteral())

        # Primitivos (integer, string, boolean, null)
        text = ctx.getText()
        t = validateLiteral(text, self.v.errors, ctx)
        setattr(ctx, "_type", t)
        return t

    @logFunction(channel="semantic")
    def visitIdentifierExpr(self, ctx):
        name = ctx.getText()
        sym = self.v.scopeManager.lookup(name)
        if sym is None:
            self.v.appendErr(SemanticError(
                f"Identificador '{name}' no está declarado.",
                line=ctx.start.line, column=ctx.start.column))
            return ErrorType()

        if sym.category == SymbolCategory.FUNCTION:
            rtype = sym.return_type if sym.return_type is not None else VoidType()
            ftype = FunctionType(sym.param_types, rtype)
            # anotar label para futuras llamadas (lectura por TAC)
            try:
                setattr(ftype, "_label", getattr(sym, "label", None) or f"f_{sym.name}")
            except Exception:
                pass
            return ftype

        # Registro de capturas (variables externas) para closures — solo semántica
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

    @logFunction(channel="semantic")
    def visitArrayLiteral(self, ctx):
        from semantic.custom_types import ArrayType, ErrorType
        from semantic.errors import SemanticError

        elems = list(ctx.expression()) if ctx.expression() else []

        if not elems:
            # Política para [] sin anotación: error (podrías usar 'any' si existiera).
            err = SemanticError(
                "Arreglo vacío no tiene tipo inferible sin anotación.",
                line=ctx.start.line, column=ctx.start.column
            )
            self.v.appendErr(err)
            t = ErrorType()
            setattr(ctx, "_type", t)
            return t

        # Visita el primero y unifica con el resto.
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
                ok = False

        t = ArrayType(elem_t) if ok else ErrorType()
        setattr(ctx, "_type", t)
        return t

    @logFunction(channel="semantic")
    def visitThisExpr(self, ctx):
        if not self.v.in_method or not self.v.class_stack:
            self.v.appendErr(SemanticError(
                "'this' solo puede usarse dentro de métodos de clase.",
                line=ctx.start.line, column=ctx.start.column))
            return ErrorType()
        cls_name = self.v.class_stack[-1]
        return ClassType(cls_name)

    # ---------- Operadores (solo tipos) ----------
    @logFunction(channel="semantic")
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
            if isinstance(res_type, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Operación aritmética inválida: {current_type} {op_txt} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                return ErrorType()
            current_type = res_type
            i += 2
        return current_type

    @logFunction(channel="semantic")
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
            if isinstance(res_type, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Operación multiplicativa inválida: {current_type} {op_txt} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                return ErrorType()
            current_type = res_type
            i += 2
        return current_type

    @logFunction(channel="semantic")
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
            if isinstance(res, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Comparación no válida: {last_type} {children[i].getText()} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                return ErrorType()
            final_type = res
            last_type = right_type
            i += 2
        return final_type if final_type is not None else last_type

    @logFunction(channel="semantic")
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
            if isinstance(res, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Igualdad no válida: {last_type} {children[i].getText()} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                return ErrorType()
            final_type = res
            last_type = right_type
            i += 2
        return final_type if final_type is not None else last_type

    @logFunction(channel="semantic")
    def visitLogicalAndExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        current_type = self.v.visit(children[0])
        i = 1
        while i < len(children):
            right_type = self.v.visit(children[i + 1])
            res = resultLogical(current_type, right_type)
            if isinstance(res, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Operación lógica inválida: {current_type} && {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                return ErrorType()
            current_type = res
            i += 2
        return current_type

    @logFunction(channel="semantic")
    def visitLogicalOrExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children:
            return None

        current_type = self.v.visit(children[0])
        i = 1
        while i < len(children):
            right_type = self.v.visit(children[i + 1])
            res = resultLogical(current_type, right_type)
            if isinstance(res, ErrorType):
                self.v.appendErr(SemanticError(
                    f"Operación lógica inválida: {current_type} || {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                return ErrorType()
            current_type = res
            i += 2
        return current_type

    @logFunction(channel="semantic")
    def visitUnaryExpr(self, ctx):
        if ctx.getChildCount() == 2:
            op_txt = ctx.getChild(0).getText()
            inner_type = self.v.visit(ctx.unaryExpr())

            if op_txt == '-':
                res = resultUnaryMinus(inner_type)
                if isinstance(res, ErrorType):
                    self.v.appendErr(SemanticError(
                        f"Operador '-' inválido sobre tipo {inner_type}",
                        line=ctx.start.line, column=ctx.start.column))
                return res

            if op_txt == '!':
                res = resultUnaryNot(inner_type)
                if isinstance(res, ErrorType):
                    self.v.appendErr(SemanticError(
                        f"Operador '!' inválido sobre tipo {inner_type}",
                        line=ctx.start.line, column=ctx.start.column))
                return res

            return ErrorType()
        else:
            return self.v.visit(ctx.primaryExpr())

    # ---------- Objetos / propiedades / new (solo tipos) ----------
    @logFunction(channel="semantic")
    def visitNewExpr(self, ctx):
        class_name = ctx.Identifier().getText()

        if not self.v.class_handler.exists(class_name):
            self.v.appendErr(SemanticError(
                f"Clase '{class_name}' no declarada.",
                line=ctx.start.line, column=ctx.start.column))
            return ErrorType()

        args_nodes = list(ctx.arguments().expression()) if ctx.arguments() else []
        arg_types = [self.v.visit(e) for e in args_nodes]

        # Buscar firma de constructor en la jerarquía
        found_sig = None
        if self.v.class_handler.exists(class_name):
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
            # sin constructor declarado: esperamos 0 args
            if len(arg_types) != 0:
                self.v.appendErr(SemanticError(
                    f"Constructor de '{class_name}' no declarado; se esperaban 0 argumentos.",
                    line=ctx.start.line, column=ctx.start.column))
        else:
            ctor_owner, (param_types, _rtype) = found_sig
            expected = len(param_types) - 1   # sin 'this'
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
        return ClassType(class_name)

    @logFunction(channel="semantic")
    def visitPropertyAccessExpr(self, ctx):
        obj_type = self.v.visit(ctx.expression())
        prop_name = ctx.Identifier().getText()

        if not isinstance(obj_type, ClassType):
            self.v.appendErr(SemanticError(
                f"No se puede acceder a propiedades de tipo '{obj_type}'.",
                line=ctx.start.line, column=ctx.start.column))
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
            # metadata útil para TAC
            try:
                setattr(ftype, "_bound_receiver", class_name)
                setattr(ftype, "_decl_owner", owner or class_name)
            except Exception:
                pass
            return ftype

        self.v.appendErr(SemanticError(
            f"Miembro '{prop_name}' no declarado en clase '{class_name}'.",
            line=ctx.start.line, column=ctx.start.column))
        return ErrorType()

    @logFunction(channel="semantic")
    def visitLeftHandSide(self, ctx):
        return self.lvalues.visitLeftHandSide(ctx)
