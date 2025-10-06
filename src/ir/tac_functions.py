from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger import log, logFunction
from semantic.custom_types import VoidType
from utils.ast_utils import findFunctionSymbol


class TacFunctions:
    """
    Generación de TAC para **funciones globales** (no métodos de clase).

    Supuestos previos:
      - La fase semántica ya resolvió símbolos: etiqueta, tamaño de frame y tipo de retorno.
    
    Responsabilidades:
      - Emitir prólogo (beginFunction).
      - Emitir cuerpo TAC (visit block).
      - Emitir epílogo (return implícito si void, return None si no-void).
      - Garantizar cierre de la función aunque el bloque no tenga return explícito.
    """

    @logFunction(channel="tac")
    def __init__(self, v):
        log("\n" + "="*80, channel="tac")
        log("[TAC_FUNCTIONS] Init TacFunctions", channel="tac")
        log("="*80 + "\n", channel="tac")
        self.v = v

    @logFunction(channel="tac")
    def visitFunctionDeclaration(self, ctx: CompiscriptParser.FunctionDeclarationContext):
        """
        Emite prólogo, cuerpo y epílogo (return implícito si void o return None si no-void).
        Siempre cierra la función para que código posterior no se quede dentro del scope.
        """
        name = ctx.Identifier().getText()
        fsym = findFunctionSymbol(self.v.scopeManager, name)
        if fsym is None:
            log(f"\t[TAC][WARN] Símbolo de función no encontrado: {name}; se omite emisión.\n", channel="tac")
            return None

        expected_ret = fsym.return_type if fsym.return_type is not None else VoidType()

        # --- Prólogo ---
        self.v.emitter.clearFlowTermination()
        frame_size = getattr(fsym, "local_frame_size", 0) or 0
        label = getattr(fsym, "label", None) or f"{name}"

        log("\n" + "-"*60, channel="tac")
        log(f"\t[TAC][FUNC] Begin function:", channel="tac")
        log(f"\tname       = {name}", channel="tac")
        log(f"\tlabel      = {label}", channel="tac")
        log(f"\tframe_size = {frame_size}", channel="tac")
        log(f"\treturn     = {expected_ret}", channel="tac")
        log("-"*60 + "\n", channel="tac")

        self.v.emitter.beginFunction(label, frame_size)
        if hasattr(self.v.emitter, "temp_pool"):
            self.v.emitter.temp_pool.resetPerStatement()

        # Guardar/limpiar banderas externas
        saved_term = getattr(self.v, "stmt_just_terminated", None)
        saved_node = getattr(self.v, "stmt_just_terminator_node", None)
        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None

        # Contexto de retorno
        if hasattr(self.v, "fn_stack"):
            self.v.fn_stack.append(expected_ret)

        # --- Cuerpo ---
        try:
            block_result = self.v.visit(ctx.block())
        finally:
            if hasattr(self.v, "fn_stack"):
                try:
                    self.v.fn_stack.pop()
                except Exception:
                    pass
            self.v.stmt_just_terminated = saved_term
            self.v.stmt_just_terminator_node = saved_node

        # --- Detección de flujo terminado ---
        terminated = False
        try:
            if isinstance(block_result, dict) and block_result.get("terminated"):
                terminated = True
        except Exception:
            pass
        terminated = terminated or bool(getattr(self.v.emitter, "flow_terminated", False))

        # --- Epílogo ---
        if not terminated:
            if isinstance(expected_ret, VoidType):
                self.v.emitter.endFunction()
                log(f"\t[TAC][FUNC] Implicit endFunction (sin return) en función void '{name}'", channel="tac")
            else:
                self.v.emitter.endFunctionWithReturn("None")
                log(f"\t[TAC][WARN] Función '{name}' no-void sin 'return'; emitiendo return None.", channel="tac")

        # --- Limpieza ---
        self.v.emitter.clearFlowTermination()
        if hasattr(self.v.emitter, "temp_pool"):
            self.v.emitter.temp_pool.resetPerStatement()

        log(f"\t[TAC][FUNC] End function: {name}\n", channel="tac")
        return block_result
