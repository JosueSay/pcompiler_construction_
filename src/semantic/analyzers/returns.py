from semantic.custom_types import VoidType
from semantic.errors import SemanticError
from semantic.type_system import isAssignable


class ReturnsAnalyzer:
    def __init__(self, v):
        self.v = v

    def visitReturnStatement(self, ctx):
        """
        Semántica:
          - Verifica que 'return' esté dentro de una función.
          - Chequea valor vs tipo de retorno esperado.
        TAC:
          - Emite 'return' o 'return <place>'.
          - Activa barrera de emisión (v.emitter.markFlowTerminated()) vía endFunctionWithReturn.
        """
        # --- 1) Return fuera de función ---
        if not self.v.fn_stack:
            self.v.appendErr(SemanticError(
                "'return' fuera de una función.",
                line=ctx.start.line, column=ctx.start.column))
            # Aun así, el 'return' termina el flujo local del bloque actual
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        expected = self.v.fn_stack[-1]
        has_expr = ctx.expression() is not None

        # --- 2) Función 'void' ---
        if isinstance(expected, VoidType):
            if has_expr:
                self.v.appendErr(SemanticError(
                    "La función 'void' no debe retornar un valor.",
                    line=ctx.start.line, column=ctx.start.column))
            # Emitimos 'return' sin valor siempre (TAC)
            self.v.emitter.endFunctionWithReturn(None)
            # Marcar terminación de flujo para análisis de 'dead code'
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        # --- 3) Función no-void: se espera valor ---
        if not has_expr:
            self.v.appendErr(SemanticError(
                "Se esperaba un valor en 'return'.",
                line=ctx.start.line, column=ctx.start.column))
            # Emitimos de todos modos 'return' para cerrar el flujo en TAC
            self.v.emitter.endFunctionWithReturn(None)
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        # Evaluar expresión de retorno
        value_t = self.v.visit(ctx.expression())

        # Chequeo de asignabilidad del tipo
        if not isAssignable(expected, value_t):
            self.v.appendErr(SemanticError(
                f"Tipo de retorno incompatible: no se puede asignar {value_t} a {expected}.",
                line=ctx.start.line, column=ctx.start.column))

        # Obtener el 'place' del valor para el TAC
        place, _ = self.v.exprs.deepPlace(ctx.expression())
        ret_place = place or ctx.expression().getText()

        # Emitimos 'return <place>'
        self.v.emitter.endFunctionWithReturn(ret_place)

        # Liberar temporal si aplica (best-effort)
        try:
            self.v.exprs.freeIfTemp(ctx.expression(), value_t)
        except Exception:
            pass

        # Marcar terminación de flujo
        self.v.stmt_just_terminated = "return"
        self.v.stmt_just_terminator_node = ctx
        return {"terminated": True, "reason": "return"}
