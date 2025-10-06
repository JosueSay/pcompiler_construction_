from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger import log, logFunction
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
        1. Prólogo (label + beginFunction).
        2. Cuerpo (visita del bloque).
        3. Epílogo (return implícito si es void).
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
        frame_size = getattr(fsym, "local_frame_size", 0)
        func_label = fsym.label or f"{current_class}_{method_name}"

        log("\n" + "-"*60, channel="tac")
        log(f"\t[TAC][METHOD] Begin function:", channel="tac")
        log(f"\tqname      = {qname}", channel="tac")
        log(f"\tlabel      = {func_label}", channel="tac")
        log(f"\tframe_size = {frame_size}", channel="tac")
        log("-"*60 + "\n", channel="tac")

        self.v.emitter.beginFunction(func_label, frame_size)

        # --- Guardar estado externo ---
        saved_term = getattr(self.v, "stmt_just_terminated", None)
        saved_node = getattr(self.v, "stmt_just_terminator_node", None)
        saved_owner = getattr(self.v, "current_method_owner", None)

        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None
        self.v.current_method_owner = current_class  # tipado de `this`

        # --- Contexto de retorno ---
        if hasattr(self.v, "fn_stack"):
            self.v.fn_stack.append(expected_r)
        if hasattr(self.v, "in_method"):
            self.v.in_method = True

        # --- Cuerpo ---
        try:
            block_result = self.v.visit(ctx_fn.block())
        finally:
            # Restaurar contexto externo
            if hasattr(self.v, "fn_stack"):
                self.v.fn_stack.pop()
            if hasattr(self.v, "in_method"):
                self.v.in_method = False

            self.v.stmt_just_terminated = saved_term
            self.v.stmt_just_terminator_node = saved_node
            self.v.current_method_owner = saved_owner

        # --- Epílogo (return implícito) ---
        if isinstance(expected_r, VoidType) and not self.v.emitter.flow_terminated:
            self.v.emitter.endFunctionWithReturn(None)
            log(f"\t[TAC][METHOD] Implicit return in void method {qname}", channel="tac")

        self.v.emitter.clearFlowTermination()
        log(f"\t[TAC][METHOD] End function: {qname}\n", channel="tac")
        return block_result
