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
        ADEMÁS: **siempre** cierra la función (endFunction / finishCurrentFunction) para
        evitar que instrucciones posteriores queden dentro del mismo cuerpo.
        """
        name = ctx.Identifier().getText()
        fsym = findFunctionSymbol(self.v.scopeManager, name)
        if fsym is None:
            log(f"[TAC][warn] símbolo de función no encontrado: {name}; se omite emisión.", channel="tac")
            return None

        expected_ret = fsym.return_type if fsym.return_type is not None else VoidType()

        # --- prólogo ---
        # Limpia cualquier barrera de flujo previa y abre la función.
        self.v.emitter.clearFlowTermination()
        frame_size = getattr(fsym, "local_frame_size", 0) or 0
        label = getattr(fsym, "label", None) or f"{name}"
        self.v.emitter.beginFunction(label, frame_size)
        if hasattr(self.v.emitter, "temp_pool"):
            self.v.emitter.temp_pool.resetPerStatement()
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
            if hasattr(self.v, "fn_stack"):
                try:
                    self.v.fn_stack.pop()
                except Exception:
                    pass
            self.v.stmt_just_terminated = saved_term
            self.v.stmt_just_terminator_node = saved_node

        # Detectar si el flujo ya terminó dentro del bloque (por 'return')
        terminated = False
        try:
            if isinstance(block_result, dict) and block_result.get("terminated"):
                terminated = True
        except Exception:
            pass
        terminated = terminated or bool(getattr(self.v.emitter, "flow_terminated", False))

        # --- epílogo ---
        if not terminated:
            if isinstance(expected_ret, VoidType):
                # Como en el video: cerrar sin RETURN explícito
                self.v.emitter.endFunction()
                log(f"[TAC] endFunction (sin return) en función void {name}", channel="tac")

            else:
                # no-void -> return None (conservador y consistente con TacReturns)
                self.v.emitter.endFunctionWithReturn("None")
                log(f"[TAC][warn] función '{name}' no-void sin 'return' explícito; emitiendo return None.", channel="tac")

        # Limpiar barrera para que el código de nivel superior no quede bloqueado
        self.v.emitter.clearFlowTermination()
        if hasattr(self.v.emitter, "temp_pool"):
            self.v.emitter.temp_pool.resetPerStatement()
        log(f"[TAC] fin función: {name}", channel="tac")
        return block_result
