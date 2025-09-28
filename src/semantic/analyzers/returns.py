from semantic.custom_types import VoidType
from semantic.errors import SemanticError
from semantic.type_system import isAssignable
from logs.logger_semantic import log_semantic, log_function

class ReturnsAnalyzer:
    @log_function
    def __init__(self, v):
        log_semantic("===== [Returns.py] Inicio =====")
        log_semantic(f"__init__ -> Recibido v={v}")
        self.v = v

    @log_function
    def visitReturnStatement(self, ctx):
        """
        Semántica:
          - Verifica que 'return' esté dentro de una función.
          - Chequea valor vs tipo de retorno esperado.
        TAC:
          - Emite 'return' o 'return <place>'.
          - Activa barrera de emisión vía endFunctionWithReturn.
        """
        log_semantic(f"[visitReturnStatement] Revisando 'return' en línea {ctx.start.line}")

        # --- 1) Return fuera de función ---
        if not self.v.fn_stack:
            log_semantic("Return fuera de función detectado")
            self.v.appendErr(SemanticError(
                "'return' fuera de una función.",
                line=ctx.start.line, column=ctx.start.column))
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        expected = self.v.fn_stack[-1]
        has_expr = ctx.expression() is not None
        log_semantic(f"Tipo de retorno esperado: {expected}, expresión presente: {has_expr}")

        # --- 2) Función 'void' ---
        if isinstance(expected, VoidType):
            if has_expr:
                log_semantic("Error: función void retornando valor")
                self.v.appendErr(SemanticError(
                    "La función 'void' no debe retornar un valor.",
                    line=ctx.start.line, column=ctx.start.column))
            log_semantic("Emitir TAC: return sin valor")
            self.v.emitter.endFunctionWithReturn(None)
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        # --- 3) Función no-void: se espera valor ---
        if not has_expr:
            log_semantic("Error: función no-void sin valor de retorno")
            self.v.appendErr(SemanticError(
                "Se esperaba un valor en 'return'.",
                line=ctx.start.line, column=ctx.start.column))
            log_semantic("Emitir TAC: return sin valor (forzado)")
            self.v.emitter.endFunctionWithReturn(None)
            self.v.stmt_just_terminated = "return"
            self.v.stmt_just_terminator_node = ctx
            return {"terminated": True, "reason": "return"}

        # Evaluar expresión de retorno
        value_t = self.v.visit(ctx.expression())
        log_semantic(f"Tipo de valor de retorno evaluado: {value_t}")

        # Chequeo de asignabilidad del tipo
        if not isAssignable(expected, value_t):
            log_semantic(f"Error: tipo incompatible {value_t} no asignable a {expected}")
            self.v.appendErr(SemanticError(
                f"Tipo de retorno incompatible: no se puede asignar {value_t} a {expected}.",
                line=ctx.start.line, column=ctx.start.column))

        # Obtener el 'place' del valor para el TAC
        place, _ = self.v.exprs.deepPlace(ctx.expression())
        ret_place = place or ctx.expression().getText()
        log_semantic(f"Emitir TAC: return {ret_place}")
        self.v.emitter.endFunctionWithReturn(ret_place)

        # Liberar temporal si aplica (best-effort)
        try:
            self.v.exprs.freeIfTemp(ctx.expression(), value_t)
        except Exception:
            log_semantic("No se liberó temporal (excepción atrapada)")

        # Marcar terminación de flujo
        self.v.stmt_just_terminated = "return"
        self.v.stmt_just_terminator_node = ctx
        log_semantic("Return procesado, flujo marcado como terminado")
        return {"terminated": True, "reason": "return"}
