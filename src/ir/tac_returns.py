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

        def _end(value=None):
            # value: None  -> RETURN            (sin valor)
            # value: "None"-> RETURN None       (literal None)
            self.v.emitter.endFunctionWithReturn(value)
            if hasattr(self.v.emitter, "markFlowTerminated"):
                self.v.emitter.markFlowTerminated()
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        if isinstance(expected, VoidType):
            # funciones void: siempre sin valor
            return _end(None)
        
        if not has_expr:
            # no-void sin expresión: RETURN None (conservador)
            return _end("None")


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
