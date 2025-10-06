from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger import log, logFunction
from semantic.custom_types import VoidType
from utils.ast_utils import findFunctionSymbol


class TacFunctions:
    """
    Generación de TAC para **funciones globales** (no métodos de clase).

    Supuestos:
      - La fase semántica ya resolvió: label, local_frame_size, return_type y fn_scope_id.
    """

    def __init__(self, v):
        log("\n" + "="*80, channel="tac")
        log("[TAC_FUNCTIONS] Init TacFunctions", channel="tac")
        log("="*80 + "\n", channel="tac")
        self.v = v

    def visitFunctionDeclaration(self, ctx: CompiscriptParser.FunctionDeclarationContext):
        """
        Emite prólogo, cuerpo (una única visita) y epílogo.
        - Si void y no hubo return: endFunction implícito.
        - Si no-void y no hubo return: endFunctionWithReturn(None).
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

        # --- Contexto: fn_stack + scope del cuerpo ---
        sm = self.v.scopeManager
        func_scope_id = getattr(fsym, "fn_scope_id", None)
        pushed = False

        # Guardar/limpiar banderas externas
        saved_term = getattr(self.v, "stmt_just_terminated", None)
        saved_node = getattr(self.v, "stmt_just_terminator_node", None)
        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None

        # Empujar tipo de retorno esperado
        if hasattr(self.v, "fn_stack"):
            self.v.fn_stack.append(expected_ret)
            log(f"[TacFunctions] fn_stack.push({expected_ret}); depth={len(self.v.fn_stack)}", channel="tac")

        log(f"[TacFunctions] Using fn_scope_id={func_scope_id}", channel="tac")
        try:
            if func_scope_id is not None:
                if hasattr(sm, "pushScopeById"):
                    sm.pushScopeById(func_scope_id)
                    pushed = True
                    log(f"[TacFunctions] Entered scope (pushScopeById) {func_scope_id}", channel="tac")
                elif hasattr(sm, "enterScopeById"):
                    sm.enterScopeById(func_scope_id)
                    pushed = True
                    log(f"[TacFunctions] Entered scope (enterScopeById) {func_scope_id}", channel="tac")
                else:
                    log(f"[TacFunctions][WARN] ScopeManager no expone enter/pushScopeById; no se reactivó el scope.", channel="tac")
            else:
                log(f"[TacFunctions][WARN] Función '{name}' sin fn_scope_id; se usa scope actual", channel="tac")

            # --- Cuerpo (una sola visita) ---
            log(f"[TacFunctions] Visiting function body of {name}", channel="tac")
            block_result = self.v.visit(ctx.block())
            log(f"[TacFunctions] Finished function body of {name}, block_result={block_result}", channel="tac")

        finally:
            # Salir del scope reactivado
            if pushed:
                if hasattr(sm, "popScope"):
                    sm.popScope()
                    log(f"[TacFunctions] Exited scope (popScope) {func_scope_id}", channel="tac")
                elif hasattr(sm, "leaveScope"):
                    sm.leaveScope()
                    log(f"[TacFunctions] Exited scope (leaveScope) {func_scope_id}", channel="tac")

            # fn_stack pop y restaurar banderas
            if hasattr(self.v, "fn_stack"):
                try:
                    popped = self.v.fn_stack.pop()
                    log(f"[TacFunctions] fn_stack.pop() -> {popped}; depth={len(self.v.fn_stack)}", channel="tac")
                except Exception:
                    log(f"[TacFunctions][WARN] fn_stack.pop() falló (pila vacía)", channel="tac")

            self.v.stmt_just_terminated = saved_term
            self.v.stmt_just_terminator_node = saved_node

        # --- Detección de flujo terminado ---
        terminated = False
        try:
            if isinstance(block_result, dict) and block_result.get("terminated"):
                terminated = True
        except Exception:
            pass
        if getattr(self.v.emitter, "flow_terminated", False):
            terminated = True
        log(f"[TacFunctions] terminated={terminated}, flow_terminated={getattr(self.v.emitter, 'flow_terminated', False)}", channel="tac")

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
