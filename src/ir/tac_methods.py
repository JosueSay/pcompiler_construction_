from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger import log
from semantic.custom_types import VoidType
from utils.ast_utils import findFunctionSymbol


class TacMethods:
    """
    Generación de TAC para clases y métodos.

    Supuestos previos:
      - La fase semántica ya resolvió símbolos: etiqueta, tamaño de frame
        y tipo de retorno de cada método.
      - Aquí no se hacen validaciones semánticas adicionales, sólo emisión de TAC.
    
    Responsabilidades:
      - Emitir prólogo (label, frame size) y epílogo (return implícito en void).
      - Exponer `self.v.current_method_owner` durante el cuerpo para tipar `this`.
      - Manejar el stack de retorno (`fn_stack`) y el estado de flujo.
    """

    
    def __init__(self, v):
        log("\n" + "="*80, channel="tac")
        log("[TAC_METHODS] Init TacMethods", channel="tac")
        log("="*80 + "\n", channel="tac")
        self.v = v

    # -------------------------------------------------------------------------
    # Visitors
    # -------------------------------------------------------------------------

    
    def visitClassDeclaration(self, ctx: CompiscriptParser.ClassDeclarationContext):
        """
        Recorre los miembros de la clase y emite TAC solo para los métodos.
        Campos/atributos no generan código intermedio aquí.
        """
        class_name = ctx.Identifier(0).getText()
        log(f"\n[TAC][CLASS] >>> Enter class: {class_name}", channel="tac")

        for mem in ctx.classMember():
            fn = mem.functionDeclaration()
            if fn:
                self.visitMethodDeclaration(fn, current_class=class_name)

        log(f"\t[TAC][CLASS] <<< Exit class: {class_name}\n", channel="tac")
        return None

    
    def visitMethodDeclaration(
        self, ctx_fn: CompiscriptParser.FunctionDeclarationContext, *, current_class: str
    ):
        """
        Emite TAC para un método:
        1) Prólogo (label + beginFunction)
        2) Cuerpo (una sola visita con contexto correcto)
        3) Epílogo (implícito si void)
        """
        method_name = ctx_fn.Identifier().getText()
        qname = f"{current_class}.{method_name}"

        # --- Resolución del símbolo del método ---
        fsym = findFunctionSymbol(self.v.scopeManager, qname)
        if fsym is None:
            log(f"\t[TAC][WARN] Método no encontrado en símbolos: {qname}; se omite emisión.\n", channel="tac")
            return None

        expected_r = fsym.return_type if fsym.return_type is not None else VoidType()

        # --- Prólogo ---
        self.v.emitter.clearFlowTermination()
        frame_size = getattr(fsym, "local_frame_size", 0) or 0
        func_label = getattr(fsym, "label", None) or f"{current_class}_{method_name}"

        log("\n" + "-"*60, channel="tac")
        log(f"\t[TAC][METHOD] Begin function:", channel="tac")
        log(f"\tqname      = {qname}", channel="tac")
        log(f"\tlabel      = {func_label}", channel="tac")
        log(f"\tframe_size = {frame_size}", channel="tac")
        log("-"*60 + "\n", channel="tac")

        self.v.emitter.beginFunction(func_label, frame_size)
        if hasattr(self.v.emitter, "temp_pool"):
            self.v.emitter.temp_pool.resetPerStatement()

        # --- Contexto del método y scope ---
        sm = self.v.scopeManager
        func_scope_id = (
            getattr(fsym, "func_scope_id", None)
            if getattr(fsym, "func_scope_id", None) is not None
            else getattr(fsym, "fn_scope_id", None)
        )
        restore_id = sm.currentScopeId()  # llamar al método, no usar atributo
        pushed = False

        # Guardar estado externo
        saved_term = getattr(self.v, "stmt_just_terminated", None)
        saved_node = getattr(self.v, "stmt_just_terminator_node", None)
        saved_owner = getattr(self.v, "current_method_owner", None)

        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None

        # Pila de retorno + owner ANTES de visitar el cuerpo
        if hasattr(self.v, "fn_stack"):
            self.v.fn_stack.append(expected_r)
            log(f"[TacMethods] fn_stack.push({expected_r}); depth={len(self.v.fn_stack)}", channel="tac")

        if hasattr(self.v, "in_method"):
            self.v.in_method = True

        self.v.current_method_owner = current_class
        log(f"[TacMethods] current_method_owner = {current_class}", channel="tac")
        log(f"[TacMethods] Using func_scope_id={func_scope_id} (restore_id={restore_id})", channel="tac")

        # --- Cuerpo: UNA sola visita dentro del scope correcto ---
        try:
            if func_scope_id is not None:
                if hasattr(sm, "pushScopeById"):
                    sm.pushScopeById(func_scope_id); pushed = True
                    log(f"[TacMethods] Entered scope (pushScopeById) {func_scope_id}", channel="tac")
                elif hasattr(sm, "enterScopeById"):
                    sm.enterScopeById(func_scope_id); pushed = True
                    log(f"[TacMethods] Entered scope (enterScopeById) {func_scope_id}", channel="tac")
                elif hasattr(sm, "enterScope"):
                    sm.enterScope(func_scope_id); pushed = True
                    log(f"[TacMethods] Entered scope (enterScope) {func_scope_id}", channel="tac")
            else:
                log(f"[TacMethods][WARN] Método '{qname}' sin func_scope_id; usando scope actual", channel="tac")

            log(f"[TacMethods] Visiting method body of {qname}", channel="tac")
            block_result = self.v.visit(ctx_fn.block())
            log(f"[TacMethods] Finished method body of {qname}, block_result={block_result}", channel="tac")

        finally:
            # Salir del scope del método
            if pushed and hasattr(sm, "popScope"):
                sm.popScope()
                log(f"[TacMethods] Exited scope (popScope) {func_scope_id}", channel="tac")
            elif pushed and hasattr(sm, "leaveScope"):
                sm.leaveScope()
                log(f"[TacMethods] Exited scope (leaveScope) {func_scope_id}", channel="tac")
            elif not pushed and restore_id is not None and hasattr(sm, "setCurrentScopeId"):
                sm.setCurrentScopeId(restore_id)
                log(f"[TacMethods] Restored previous scope {restore_id}", channel="tac")

            # Pop de contexto del método
            if hasattr(self.v, "fn_stack"):
                try:
                    popped = self.v.fn_stack.pop()
                    log(f"[TacMethods] fn_stack.pop() -> {popped}; depth={len(self.v.fn_stack)}", channel="tac")
                except Exception:
                    log(f"[TacMethods][WARN] fn_stack.pop() falló (pila vacía)", channel="tac")

            if hasattr(self.v, "in_method"):
                self.v.in_method = False

            self.v.current_method_owner = saved_owner
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
        log(f"[TacMethods] terminated={terminated}, flow_terminated={getattr(self.v.emitter, 'flow_terminated', False)}", channel="tac")

        # --- Epílogo ---
        if not terminated:
            if isinstance(expected_r, VoidType):
                self.v.emitter.endFunction()
                log(f"\t[TAC][METHOD] Implicit endFunction (sin return) en método void {qname}", channel="tac")
            else:
                self.v.emitter.endFunctionWithReturn("None")
                log(f"\t[TAC][WARN] Método '{qname}' no-void sin 'return'; emitiendo return None.", channel="tac")
                
        else:
            self.v.emitter.endFunction()

        self.v.emitter.clearFlowTermination()
        if hasattr(self.v.emitter, "temp_pool"):
            self.v.emitter.temp_pool.resetPerStatement()

        log(f"\t[TAC][METHOD] End function: {qname}\n", channel="tac")
        return block_result
