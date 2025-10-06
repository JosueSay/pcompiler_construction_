from semantic.custom_types import VoidType, ErrorType
from semantic.errors import SemanticError
from semantic.type_system import isAssignable
from logs.logger import log


class ReturnsAnalyzer:
    """
    Valida el uso de `return` en contexto semántico con logs estilo TAC.

    Reglas:
      - `return` debe estar dentro de una función.
      - En funciones `void`, no se permite `return <expr>`.
      - En funciones no-void, `return` debe tener expresión y tipo asignable.
    """

    def __init__(self, v):
        log("\n" + "="*80, channel="semantic")
        log("===== [ReturnsAnalyzer] Inicio SEMÁNTICO =====", channel="semantic")
        log("="*80 + "\n", channel="semantic")
        self.v = v

    def typeOfSilent(self, expr_ctx):
        """
        Devuelve el tipo de `expr_ctx` sin generar TAC
        (usa barrera temporal si hay emitter).
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

    def visitReturnStatement(self, ctx):
        """
        Chequea semánticamente un `return`:
        ubicación válida y compatibilidad de tipo.
        """
        log("\n" + "-"*80, channel="semantic")
        log(f"[return] línea={ctx.start.line}", channel="semantic")

        # 1) 'return' fuera de función
        if not getattr(self.v, "fn_stack", None):
            self.v.appendErr(SemanticError(
                "'return' fuera de una función.",
                line=ctx.start.line, column=ctx.start.column))
            log("\t[error] 'return' fuera de función", channel="semantic")
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        expected = self.v.fn_stack[-1]
        has_expr = ctx.expression() is not None
        log(f"\t[return] esperado={expected}, con_expr={has_expr}", channel="semantic")

        # 2) Función void
        if isinstance(expected, VoidType):
            if has_expr:
                self.v.appendErr(SemanticError(
                    "La función 'void' no debe retornar un valor.",
                    line=ctx.start.line, column=ctx.start.column))
                log("\t[error] void retornó valor", channel="semantic")
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        # 3) Función no-void sin expresión
        if not has_expr:
            self.v.appendErr(SemanticError(
                "Se esperaba un valor en 'return'.",
                line=ctx.start.line, column=ctx.start.column))
            log("\t[error] retorno sin valor en función no-void", channel="semantic")
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        # 4) Evaluar tipo de la expresión sin TAC
        value_t = self.typeOfSilent(ctx.expression())
        log(f"\t[return] tipo valor={value_t}", channel="semantic")
        if not isAssignable(expected, value_t):
            self.v.appendErr(SemanticError(
                f"Tipo de retorno incompatible: no se puede asignar {value_t} a {expected}.",
                line=ctx.start.line, column=ctx.start.column))
            log("\t[error] tipo retorno incompatible", channel="semantic")

        self.v.stmt_just_terminated = "return"
        self.v.stmt_just_terminator_node = ctx
        log("-"*80 + "\n", channel="semantic")
        return {"terminated": True, "reason": "return"}
