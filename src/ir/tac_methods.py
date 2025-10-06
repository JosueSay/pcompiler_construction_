from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger import log, logFunction
from semantic.custom_types import VoidType
from utils.ast_utils import findFunctionSymbol


class TacMethods:
    """
    Emite TAC para clases y métodos.

    Supuestos:
    - La fase semántica ya registró en la tabla de símbolos: label, tamaño de frame
      y tipo de retorno de cada método.
    - Aquí no se hacen validaciones; sólo se baja a cuádruplos.
    - Expone `self.v.current_method_owner` durante el cuerpo del método para que
      otros visitantes (p. ej. LValues) puedan tipar `this` como la clase correcta.
    """

    @logFunction(channel="tac")
    def __init__(self, v):
        log("[tac_methods] init", channel="tac")
        self.v = v

    # -------------------------------------------------------------------------
    # Visitors
    # -------------------------------------------------------------------------
    @logFunction(channel="tac")
    def visitClassDeclaration(self, ctx: CompiscriptParser.ClassDeclarationContext):
        """
        Recorre los miembros de la clase y emite TAC sólo para los métodos.
        Campos/constantes no generan 3AC aquí.
        """
        name = ctx.Identifier(0).getText()
        log(f"[TAC][class] enter: {name}", channel="tac")

        for mem in ctx.classMember():
            fn = mem.functionDeclaration()
            if fn:
                self.visitMethodDeclaration(fn, current_class=name)

        log(f"[TAC][class] exit: {name}", channel="tac")
        return None

    @logFunction(channel="tac")
    def visitMethodDeclaration(self, ctx_fn: CompiscriptParser.FunctionDeclarationContext, *, current_class: str):
        """
        Emite prólogo (label + enter), cuerpo y, si aplica, return implícito para métodos void.
        Mientras emite el cuerpo fija `current_method_owner` para que `this` tenga tipo.
        """
        method_name = ctx_fn.Identifier().getText()
        qname = f"{current_class}.{method_name}"

        # Símbolo del método (label, frame_size, tipo retorno)
        fsym = findFunctionSymbol(self.v.scopeManager, qname)
        if fsym is None:
            log(f"[TAC][warn] método no encontrado en símbolos: {qname}; se omite emisión.", channel="tac")
            return None

        expected_r = fsym.return_type if fsym.return_type is not None else VoidType()

        # --- Prólogo ---
        self.v.emitter.clearFlowTermination()
        frame_size = fsym.local_frame_size if getattr(fsym, "local_frame_size", None) is not None else 0
        func_label = fsym.label or f"{current_class}_{method_name}"
        self.v.emitter.beginFunction(func_label, frame_size)
        log(f"[TAC] beginFunction: label={func_label}, frame_size={frame_size}", channel="tac")

        # Guardar estado externo y fijar owner para `this`
        saved_term = getattr(self.v, "stmt_just_terminated", None)
        saved_node = getattr(self.v, "stmt_just_terminator_node", None)
        saved_owner = getattr(self.v, "current_method_owner", None)

        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None
        self.v.current_method_owner = current_class  # clave para tipar `this` en TAC

        # Contexto de retorno (si el backend de returns lo utiliza)
        if hasattr(self.v, "fn_stack"):
            self.v.fn_stack.append(expected_r)
        if hasattr(self.v, "in_method"):
            self.v.in_method = True

        # --- Cuerpo ---
        try:
            block_result = self.v.visit(ctx_fn.block())
        finally:
            # Restaurar contexto
            if hasattr(self.v, "fn_stack"):
                self.v.fn_stack.pop()
            if hasattr(self.v, "in_method"):
                self.v.in_method = False

            self.v.stmt_just_terminated = saved_term
            self.v.stmt_just_terminator_node = saved_node
            self.v.current_method_owner = saved_owner

        # --- Return implícito si void y no terminó el flujo ---
        if isinstance(expected_r, VoidType) and not self.v.emitter.flow_terminated:
            self.v.emitter.endFunctionWithReturn(None)
            log(f"[TAC] implicit return in method/ctor {qname}", channel="tac")

        self.v.emitter.clearFlowTermination()
        return block_result
