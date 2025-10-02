from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger import log, logFunction
from semantic.custom_types import VoidType
from utils.ast_utils import findFunctionSymbol


class TacFunctions:
    """
    Emisión de TAC para **declaraciones de funciones** (no métodos).
    Supone que el análisis semántico ya registró:
      - label de la función
      - tamaño de frame local
      - tipo de retorno

    Requisitos del visitor `v`:
      - v.emitter  : Emitter (beginFunction/endFunctionWithReturn/clearFlowTermination/flow_terminated)
      - v.visit    : despache de subárboles TAC
      - v.scopeManager : para resolver símbolos con findFunctionSymbol
      - v.fn_stack : pila con el tipo de retorno esperado (opcional pero usado por retornos TAC)
    """

    @logFunction(channel="tac")
    def __init__(self, v):
        log("[tac_functions] init", channel="tac")
        self.v = v

    @logFunction(channel="tac")
    def visitFunctionDeclaration(self, ctx: CompiscriptParser.FunctionDeclarationContext):
        """
        Emite prólogo, cuerpo y epílogo (return implícito si void) para una función global.
        """
        name = ctx.Identifier().getText()
        fsym = findFunctionSymbol(self.v.scopeManager, name)
        if fsym is None:
            log(f"[TAC][warn] símbolo de función no encontrado: {name}; se omite emisión.", channel="tac")
            return None

        expected_ret = fsym.return_type if fsym.return_type is not None else VoidType()

        # --- prólogo ---
        self.v.emitter.clearFlowTermination()
        frame_size = getattr(fsym, "local_frame_size", 0) or 0
        label = getattr(fsym, "label", None) or f"f_{name}"
        self.v.emitter.beginFunction(label, frame_size)
        log(f"[TAC] beginFunction: label={label}, frame_size={frame_size}", channel="tac")

        # Guardar/limpiar banderas externas para no contaminar scopes superiores
        saved_term = getattr(self.v, "stmt_just_terminated", None)
        saved_node = getattr(self.v, "stmt_just_terminator_node", None)
        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None

        # Contexto de retorno (consumido por visitReturn en TAC)
        if hasattr(self.v, "fn_stack"):
            self.v.fn_stack.append(expected_ret)

        # --- cuerpo ---
        try:
            block_result = self.v.visit(ctx.block())
        finally:
            # Restaurar entorno del visitor
            self.v.stmt_just_terminated = saved_term
            self.v.stmt_just_terminator_node = saved_node
            if hasattr(self.v, "fn_stack"):
                self.v.fn_stack.pop()

        # --- return implícito si es void y el flujo no terminó adentro ---
        if isinstance(expected_ret, VoidType) and not self.v.emitter.flow_terminated:
            self.v.emitter.endFunctionWithReturn(None)
            log(f"[TAC] return implícito en función void {name}", channel="tac")

        # limpiar barrera y salir
        self.v.emitter.clearFlowTermination()
        log(f"[TAC] fin función: {name}", channel="tac")
        return block_result
