from semantic.custom_types import VoidType, ErrorType
from semantic.errors import SemanticError
from semantic.type_system import isAssignable
from logs.logger import log, logFunction


class ReturnsAnalyzer:
    """
    Valida el uso de `return` en contexto semántico (sin emitir TAC).

    Reglas:
      - `return` debe estar dentro de una función.
      - En funciones `void`, no se permite `return <expr>`.
      - En funciones no-void, `return` debe tener expresión y
        el tipo del valor debe ser asignable al tipo de retorno esperado.

    Notas:
      - Para evaluar el tipo de la expresión de retorno sin generar TAC,
        se usa una *barrera* temporal en el emitter (si existe).
    """

    @logFunction(channel="semantic")
    def __init__(self, v):
        log("===== [returns.py] Inicio (SEMÁNTICO) =====", channel="semantic")
        self.v = v

    @logFunction(channel="semantic")
    def typeOfSilent(self, expr_ctx):
        """
        Devuelve el tipo de `expr_ctx` sin generar TAC
        (activa una barrera temporal en el emitter si está presente).
        """
        if expr_ctx is None:
            return ErrorType()
        old_barrier = getattr(self.v, "emitter", None).flow_terminated if hasattr(self.v, "emitter") else None
        if hasattr(self.v, "emitter"):
            self.v.emitter.flow_terminated = True
        try:
            t = self.v.visit(expr_ctx)
        finally:
            if hasattr(self.v, "emitter"):
                self.v.emitter.flow_terminated = old_barrier
                try:
                    self.v.emitter.temp_pool.resetPerStatement()
                except Exception:
                    pass
        return t

    @logFunction(channel="semantic")
    def visitReturnStatement(self, ctx):
        """
        Chequea semánticamente un `return`:
        ubicación válida y compatibilidad de tipo con el retorno esperado.
        """
        log(f"[SEM][return] línea={ctx.start.line}", channel="semantic")

        # 1) 'return' fuera de función
        if not getattr(self.v, "fn_stack", None):
            self.v.appendErr(SemanticError(
                "'return' fuera de una función.",
                line=ctx.start.line, column=ctx.start.column))
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        expected = self.v.fn_stack[-1]
        has_expr = ctx.expression() is not None
        log(f"[SEM][return] esperado={expected}, con_expr={has_expr}", channel="semantic")

        # 2) Función void
        if isinstance(expected, VoidType):
            if has_expr:
                self.v.appendErr(SemanticError(
                    "La función 'void' no debe retornar un valor.",
                    line=ctx.start.line, column=ctx.start.column))
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        # 3) Función no-void sin expresión
        if not has_expr:
            self.v.appendErr(SemanticError(
                "Se esperaba un valor en 'return'.",
                line=ctx.start.line, column=ctx.start.column))
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        # 4) Evaluar tipo de la expresión sin TAC
        value_t = self.typeOfSilent(ctx.expression())
        if not isAssignable(expected, value_t):
            self.v.appendErr(SemanticError(
                f"Tipo de retorno incompatible: no se puede asignar {value_t} a {expected}.",
                line=ctx.start.line, column=ctx.start.column))

        self.v.stmt_just_terminated = "return"
        self.v.stmt_just_terminator_node = ctx
        return {"terminated": True, "reason": "return"}
