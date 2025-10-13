from semantic.custom_types import VoidType
from logs.logger import log
from utils.ast_utils import deepPlace, freeIfTemp
from ir.tac import Op

class TacReturns:
    """
    Generación de instrucciones TAC para sentencias 'return'.

    Responsabilidades:
    - Emitir la instrucción RETURN apropiada según el contexto.
    - Respetar la semántica ya validada previamente:
        * Si la función es void → return sin valor.
        * Si la función no es void y no hay expresión → return None.
        * Si la función no es void con expresión → return <expr>.
    - Marcar el flujo de control como terminado (para análisis posteriores).
    """

    def __init__(self, v):
        """
        Inicializa el generador de TAC para returns.
        :param v: Visitador/contexto que contiene fn_stack, emitter, etc.
        """
        self.v = v
        log("=" * 60, channel="tac")
        log("↳ [TacReturns] initialized", channel="tac")
        log("=" * 60, channel="tac")

    def visitReturnStatement(self, ctx):
        """
        Procesa una sentencia 'return' y emite la instrucción TAC correspondiente.
        :param ctx: Nodo del AST con la sentencia 'return'.
        """
        line = getattr(getattr(ctx, "start", None), "line", "?")
        log(f"\n[RETURN] Found at line {line}", channel="tac")

        # Si no hay función activa en la pila, marcamos solo la terminación
        if not getattr(self.v, "fn_stack", None):
            log("\t(no enclosing function: marking as terminated)", channel="tac")
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        expected = self.v.fn_stack[-1]      # tipo de retorno esperado
        has_expr = ctx.expression() is not None

        # Función auxiliar para finalizar correctamente el flujo
        def _end(value=None):
            """
            Emite RETURN en TAC y marca flujo como terminado.
            NO cierra la función aquí: el epílogo único lo hace TacFunctions.
            """
            pretty_val = value if value is not None else "(no value)"
            log(f"\t[TAC] RETURN {pretty_val}", channel="tac")

            if value is None:
                self.v.emitter.emit(Op.RETURN)
            else:
                self.v.emitter.emit(Op.RETURN, arg1=value)

            if hasattr(self.v.emitter, "markFlowTerminated"):
                self.v.emitter.markFlowTerminated()

            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        # Caso 1: función void → siempre return sin valor
        if isinstance(expected, VoidType):
            return _end(None)

        # Caso 2: función no-void sin expresión → conservador: RETURN None
        if not has_expr:
            return _end("None")

        # Caso 3: función no-void con expresión → evaluamos y retornamos expr
        self.v.visit(ctx.expression())
        place, _ = deepPlace(ctx.expression())
        ret_place = place or ctx.expression().getText()

        log(f"\t[expr] Evaluated return expression → {ret_place}", channel="tac")

        self.v.emitter.emit(Op.RETURN, arg1=ret_place)

        # Liberar temporales asociados a la expresión, si corresponde
        try:
            freeIfTemp(ctx.expression(), self.v.emitter.temp_pool, "*")
            log(f"\t[temp] Freed temporary(s) for {ret_place}", channel="tac")
        except Exception:
            log(f"\t[temp] No temporaries to free for {ret_place}", channel="tac")

        if hasattr(self.v.emitter, "markFlowTerminated"):
            self.v.emitter.markFlowTerminated()

        self.v.stmt_just_terminated = "return"
        self.v.stmt_just_terminator_node = ctx
        return {"terminated": True, "reason": "return"}