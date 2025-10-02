from semantic.custom_types import VoidType
from logs.logger import log, logFunction
from utils.ast_utils import deepPlace, freeIfTemp


class TacReturns:
    """
    Emisión de 'return' para TAC.
    - No valida tipos ni contexto (la semántica ya lo hizo).
    - Si la función es void, siempre retorna sin valor.
    - Si no hay expresión en función no-void, retorna None (conservador).
    """

    @logFunction(channel="tac")
    def __init__(self, v):
        log("[tac_returns] init", channel="tac")
        self.v = v

    @logFunction(channel="tac")
    def visitReturnStatement(self, ctx):
        line = getattr(getattr(ctx, "start", None), "line", "?")
        log(f"[TAC][return] line={line}", channel="tac")

        # Si no hay contexto de función, no emitimos quads (ya reportado en semántica).
        if not getattr(self.v, "fn_stack", None):
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        expected = self.v.fn_stack[-1]
        has_expr = ctx.expression() is not None

        # Función void: retornar sin valor (aunque el fuente tenga expresión).
        if isinstance(expected, VoidType):
            self.v.emitter.endFunctionWithReturn(None)
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        # Función no-void sin expresión: retornar None (política conservadora).
        if not has_expr:
            self.v.emitter.endFunctionWithReturn(None)
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        # Función no-void con expresión: evaluar y retornar su place.
        self.v.visit(ctx.expression())
        place, _ = deepPlace(ctx.expression())
        ret_place = place or ctx.expression().getText()
        self.v.emitter.endFunctionWithReturn(ret_place)

        # Best-effort: liberar temporal del valor retornado si aplica.
        try:
            freeIfTemp(ctx.expression(), self.v.emitter.temp_pool, "*")
        except Exception:
            pass

        self.v.stmt_just_terminated = "return"
        self.v.stmt_just_terminator_node = ctx
        return {"terminated": True, "reason": "return"}
