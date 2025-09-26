from semantic.custom_types import VoidType
from semantic.errors import SemanticError
from semantic.type_system import isAssignable

class ReturnsAnalyzer:
    def __init__(self, v):
        self.v = v

    def visitReturnStatement(self, ctx):
        if not self.v.fn_stack:
            self.v.appendErr(SemanticError(
                "'return' fuera de una función.",
                line=ctx.start.line, column=ctx.start.column))
            # Aun así, marca terminación del flujo local
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        expected = self.v.fn_stack[-1]
        has_expr = ctx.expression() is not None

        if isinstance(expected, VoidType):
            if has_expr:
                self.v.appendErr(SemanticError(
                    "La función 'void' no debe retornar un valor.",
                    line=ctx.start.line, column=ctx.start.column))
            # En cualquier caso, return termina el flujo
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        if not has_expr:
            self.v.appendErr(SemanticError(
                "Se esperaba un valor en 'return'.",
                line=ctx.start.line, column=ctx.start.column))
            # Aún así, el return vacío termina el flujo
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        value_t = self.v.visit(ctx.expression())
        if not isAssignable(expected, value_t):
            self.v.appendErr(SemanticError(
                f"Tipo de retorno incompatible: no se puede asignar {value_t} a {expected}.",
                line=ctx.start.line, column=ctx.start.column))
        # Return siempre termina flujo
        self.v.stmt_just_terminated = "return"
        self.v.stmt_just_terminator_node = ctx
        return {"terminated": True, "reason": "return"}
