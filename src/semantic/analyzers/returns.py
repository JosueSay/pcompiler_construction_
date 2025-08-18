from semantic.custom_types import VoidType
from semantic.errors import SemanticError

class ReturnsAnalyzer:
    def __init__(self, v):
        self.v = v

    def visitReturnStatement(self, ctx):
        if not self.v.fn_stack:
            self.v._append_err(SemanticError(
                "'return' fuera de una función.",
                line=ctx.start.line, column=ctx.start.column))
            return None

        expected = self.v.fn_stack[-1]
        has_expr = ctx.expression() is not None

        if isinstance(expected, VoidType):
            if has_expr:
                self.v._append_err(SemanticError(
                    "La función 'void' no debe retornar un valor.",
                    line=ctx.start.line, column=ctx.start.column))
            return None

        if not has_expr:
            self.v._append_err(SemanticError(
                "Se esperaba un valor en 'return'.",
                line=ctx.start.line, column=ctx.start.column))
            return None

        value_t = self.v.visit(ctx.expression())
        from semantic.type_system import isAssignable
        if not isAssignable(expected, value_t):
            self.v._append_err(SemanticError(
                f"Tipo de retorno incompatible: no se puede asignar {value_t} a {expected}.",
                line=ctx.start.line, column=ctx.start.column))
        return None
