from semantic.symbol_kinds import SymbolCategory
from semantic.validators.literal import validateLiteral
from semantic.custom_types import ArrayType, ClassType, IntegerType, StringType, BoolType, FloatType, VoidType, NullType, ErrorType, FunctionType
from semantic.type_system import (
    resultArithmetic, resultModulo, resultRelational,
    resultEquality, resultLogical, resultUnaryMinus, resultUnaryNot
)
from logs.logger_semantic import log_semantic
from semantic.errors import SemanticError

class ExpressionsAnalyzer:
    def __init__(self, v, lvalues):
        self.v = v
        self.lvalues = lvalues

    # Literales y primarios
    def visitLiteralExpr(self, ctx):
        if hasattr(ctx, "arrayLiteral") and ctx.arrayLiteral() is not None:
            return self.visitArrayLiteral(ctx.arrayLiteral())
        value = ctx.getText()
        log_semantic(f"Literal detected: {value}")
        return validateLiteral(value, self.v.errors, ctx)

    def visitIdentifierExpr(self, ctx):
            name = ctx.getText()
            log_semantic(f"Identifier used: {name}")
            sym = self.v.scopeManager.lookup(name)
            if sym is None:
                self.v._append_err(SemanticError(
                    f"Identificador '{name}' no está declarado.",
                    line=ctx.start.line, column=ctx.start.column))
                return ErrorType()
            
            if sym.category == SymbolCategory.FUNCTION:
                rtype = sym.return_type if sym.return_type is not None else VoidType()
                return FunctionType(sym.param_types, rtype)

            # 🔹 Detección de captura: si estamos dentro de una función, y el símbolo
            # pertenece a un scope externo (scope_id más bajo) => capturado.
            if self.v.fn_ctx_stack:
                curr_fn_ctx = self.v.fn_ctx_stack[-1]
                curr_fn_scope_id = curr_fn_ctx["scope_id"]
                # Se capturan variables, parámetros y constantes (no funciones)
                if sym.scope_id < curr_fn_scope_id:
                    # Guardar (name, type_str, scope_id_original)
                    try:
                        tstr = str(sym.type)
                    except Exception:
                        tstr = "<type>"
                    curr_fn_ctx["captures"].add((sym.name, tstr, sym.scope_id))

            return sym.type

    def visitArrayLiteral(self, ctx):
        expr_ctxs = list(ctx.expression())
        if not expr_ctxs:
            self.v._append_err(SemanticError(
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
            # arrays
            if isinstance(a, ArrayType) and isinstance(b, ArrayType):
                return same(a.elem_type, b.elem_type)
            if isinstance(a, ClassType) and isinstance(b, ClassType):
                return a.name == b.name
            prims = (IntegerType, StringType, BoolType, FloatType, VoidType, NullType, ErrorType)
            return isinstance(a, prims) and isinstance(b, prims) and a.__class__ is b.__class__
        if not all(same(t, first) for t in elem_types):
            self.v._append_err(SemanticError(
                f"Elementos de arreglo con tipos inconsistentes: {[str(t) for t in elem_types]}",
                line=ctx.start.line, column=ctx.start.column))
            return ErrorType()
        return ArrayType(first)

    def visitThisExpr(self, ctx):
        if not self.v.in_method or not self.v.class_stack:
            self.v._append_err(SemanticError(
                "'this' solo puede usarse dentro de métodos de clase.",
                line=ctx.start.line, column=ctx.start.column))
            return ErrorType()
        return ClassType(self.v.class_stack[-1])

    # Operadores
    def visitAdditiveExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children: return None
        t = self.v.visit(children[0])
        i = 1
        while i < len(children):
            op = children[i].getText()
            rhs = self.v.visit(children[i+1])
            res = resultArithmetic(t, rhs, op)
            if isinstance(res, ErrorType):
                self.v._append_err(SemanticError(
                    f"Operación aritmética inválida: {t} {op} {rhs}",
                    line=ctx.start.line, column=ctx.start.column))
                t = ErrorType()
            else:
                t = res
            i += 2
        return t

    def visitMultiplicativeExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children: return None
        t = self.v.visit(children[0])
        i = 1
        while i < len(children):
            op = children[i].getText()
            rhs = self.v.visit(children[i+1])
            res = resultModulo(t, rhs) if op == '%' else resultArithmetic(t, rhs, op)
            if isinstance(res, ErrorType):
                self.v._append_err(SemanticError(
                    f"Operación multiplicativa inválida: {t} {op} {rhs}",
                    line=ctx.start.line, column=ctx.start.column))
                t = ErrorType()
            else:
                t = res
            i += 2
        return t

    def visitRelationalExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children: return None
        left_type = self.v.visit(children[0])
        i = 1
        final_type = None
        while i < len(children):
            op = children[i].getText()
            right_type = self.v.visit(children[i+1])
            res = resultRelational(left_type, right_type)
            if isinstance(res, ErrorType):
                self.v._append_err(SemanticError(
                    f"Comparación no válida: {left_type} {op} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                final_type = ErrorType()
            else:
                final_type = res
            left_type = right_type
            i += 2
        return final_type if final_type is not None else left_type

    def visitEqualityExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children: return None
        left_type = self.v.visit(children[0])
        i = 1
        final_type = None
        while i < len(children):
            op = children[i].getText()
            right_type = self.v.visit(children[i+1])
            res = resultEquality(left_type, right_type)
            if isinstance(res, ErrorType):
                self.v._append_err(SemanticError(
                    f"Igualdad no válida: {left_type} {op} {right_type}",
                    line=ctx.start.line, column=ctx.start.column))
                final_type = ErrorType()
            else:
                final_type = res
            left_type = right_type
            i += 2
        return final_type if final_type is not None else left_type

    def visitLogicalAndExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children: return None
        t = self.v.visit(children[0])
        i = 1
        while i < len(children):
            rhs = self.v.visit(children[i+1])
            res = resultLogical(t, rhs)
            if isinstance(res, ErrorType):
                self.v._append_err(SemanticError(
                    f"Operación lógica inválida: {t} && {rhs}",
                    line=ctx.start.line, column=ctx.start.column))
                t = ErrorType()
            else:
                t = res
            i += 2
        return t

    def visitLogicalOrExpr(self, ctx):
        children = list(ctx.getChildren())
        if not children: return None
        t = self.v.visit(children[0])
        i = 1
        while i < len(children):
            rhs = self.v.visit(children[i+1])
            res = resultLogical(t, rhs)
            if isinstance(res, ErrorType):
                self.v._append_err(SemanticError(
                    f"Operación lógica inválida: {t} || {rhs}",
                    line=ctx.start.line, column=ctx.start.column))
                t = ErrorType()
            else:
                t = res
            i += 2
        return t

    def visitUnaryExpr(self, ctx):
        if ctx.getChildCount() == 2:
            op = ctx.getChild(0).getText()
            inner = self.v.visit(ctx.unaryExpr())
            if op == '-':
                res = resultUnaryMinus(inner)
                if isinstance(res, ErrorType):
                    self.v._append_err(SemanticError(
                        f"Operador '-' inválido sobre tipo {inner}",
                        line=ctx.start.line, column=ctx.start.column))
                return res
            elif op == '!':
                res = resultUnaryNot(inner)
                if isinstance(res, ErrorType):
                    self.v._append_err(SemanticError(
                        f"Operador '!' inválido sobre tipo {inner}",
                        line=ctx.start.line, column=ctx.start.column))
                return res
            return ErrorType()
        else:
            return self.v.visit(ctx.primaryExpr())

    def visitNewExpr(self, ctx):
        class_name = ctx.Identifier().getText()

        # FIX: usar exists(), no has_class()
        if not self.v.class_handler.exists(class_name):
            self.v._append_err(SemanticError(
                f"Clase '{class_name}' no declarada.",
                line=ctx.start.line, column=ctx.start.column))
            return ErrorType()

        # Chequear firma de constructor: ClassName.constructor
        ctor_sig = self.v.method_registry.lookup(f"{class_name}.constructor")
        arg_types = []
        if ctx.arguments():
            for e in ctx.arguments().expression():
                arg_types.append(self.v.visit(e))

        if ctor_sig is None:
            # no hay constructor declarado → debe llamarse sin args
            if len(arg_types) != 0:
                self.v._append_err(SemanticError(
                    f"Constructor de '{class_name}' no declarado; se esperaban 0 argumentos.",
                    line=ctx.start.line, column=ctx.start.column))
        else:
            param_types, rtype = ctor_sig
            # param_types incluye 'this' como primer parámetro
            expected = len(param_types) - 1
            if len(arg_types) != expected:
                self.v._append_err(SemanticError(
                    f"Número de argumentos inválido para '{class_name}.constructor': "
                    f"esperados {expected}, recibidos {len(arg_types)}.",
                    line=ctx.start.line, column=ctx.start.column))
            else:
                from semantic.type_system import isAssignable
                for i, (pt, at) in enumerate(zip(param_types[1:], arg_types), start=1):
                    if not isAssignable(pt, at):
                        self.v._append_err(SemanticError(
                            f"Argumento #{i} incompatible en constructor de '{class_name}': "
                            f"no se puede asignar {at} a {pt}.",
                            line=ctx.start.line, column=ctx.start.column))
                # rtype del constructor se ignora

        return ClassType(class_name)

    def visitPropertyAccessExpr(self, ctx):
        """
        expression '.' Identifier
        Verifica acceso a propiedad en clases (con herencia).
        """
        obj_type = self.v.visit(ctx.expression())

        from semantic.custom_types import ClassType
        if not isinstance(obj_type, ClassType):
            self.v._append_err(SemanticError(
                f"No se puede acceder a propiedades de tipo '{obj_type}'.",
                line=ctx.start.line, column=ctx.start.column))
            return ErrorType()

        class_name = obj_type.name
        prop_name = ctx.Identifier().getText()
        
        # --- Atributo (con herencia)
        prop_t = self.v.class_handler.get_attribute_type(class_name, prop_name)
        if prop_t is None:
            self.v._append_err(SemanticError(
                f"Clase '{class_name}' no tiene propiedad '{prop_name}'.",
                line=ctx.start.line, column=ctx.start.column))
            return ErrorType()

        return prop_t

    def visitLeftHandSide(self, ctx):
        return self.lvalues.visitLeftHandSide(ctx)
