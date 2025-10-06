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

        if not getattr(self.v, "fn_stack", None):
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        expected = self.v.fn_stack[-1]
        has_expr = ctx.expression() is not None

        def _end():
            self.v.emitter.endFunctionWithReturn(None)
            if hasattr(self.v.emitter, "markFlowTerminated"):
                self.v.emitter.markFlowTerminated()
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        # void => return sin valor aunque el fuente traiga expr
        from semantic.custom_types import VoidType
        if isinstance(expected, VoidType):
            return _end()

        # no-void sin expr => return None (política conservadora)
        if not has_expr:
            return _end()

        # no-void con expr
        self.v.visit(ctx.expression())
        place, _ = deepPlace(ctx.expression())
        ret_place = place or ctx.expression().getText()
        self.v.emitter.endFunctionWithReturn(ret_place)
        try:
            freeIfTemp(ctx.expression(), self.v.emitter.temp_pool, "*")
        except Exception:
            pass

        if hasattr(self.v.emitter, "markFlowTerminated"):
            self.v.emitter.markFlowTerminated()

        self.v.stmt_just_terminated = "return"
        self.v.stmt_just_terminator_node = ctx
        return {"terminated": True, "reason": "return"}
