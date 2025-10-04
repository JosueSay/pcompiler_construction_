from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import (
    ArrayType, IntegerType, ErrorType, FunctionType, ClassType, VoidType
)
from semantic.type_system import isAssignable
from semantic.errors import SemanticError
from logs.logger import log, logFunction


class LValuesAnalyzer:
    """
    Valida semántica de `leftHandSide` y sus `suffixOp`:
      - Indexación: `arr[i]`
      - Llamadas: `f(a, b, ...)`
      - Acceso a propiedades: `obj.prop` / `obj.metodo`

    Notas:
    - Esta fase **no** emite TAC ni escribe metadatos de ejecución (`_place`, `_is_temp`).
    - Solo reporta errores de tipos/forma y devuelve el tipo resultante.
    - Usa barrera de emisión para impedir generación de TAC si existe un emitter activo.
    """

    @logFunction(channel="semantic")
    def __init__(self, v):
        log("===== [lvalues.py] Inicio (SEMÁNTICO) =====", channel="semantic")
        self.v = v

    @logFunction(channel="semantic")
    def visitLeftHandSide(self, ctx: CompiscriptParser.LeftHandSideContext):
        # Bloqueo de emisión TAC durante la validación semántica
        old_barrier = getattr(self.v, "emitter", None).flow_terminated if hasattr(self.v, "emitter") else None
        if hasattr(self.v, "emitter"):
            self.v.emitter.flow_terminated = True
        try:
            base_type = self.v.visit(ctx.primaryAtom())
            lit_t = None

            # Pista de arreglo literal para validación de rangos estáticos
            try:
                base_txt = ctx.primaryAtom().getText()
                if base_txt and (base_txt[0].isalpha() or base_txt[0] == '_'):
                    sym = self.v.scopeManager.lookup(base_txt)
                    if sym is not None and hasattr(sym, "init_value_type"):
                        ivt = getattr(sym, "init_value_type", None)
                        if isinstance(ivt, ArrayType):
                            lit_t = ivt
                if lit_t is None and isinstance(base_type, ArrayType) and hasattr(base_type, "_literal_len"):
                    lit_t = base_type
            except Exception:
                pass

            for suf in ctx.suffixOp():
                # IndexExpr
                if isinstance(suf, CompiscriptParser.IndexExprContext):
                    if not isinstance(base_type, ArrayType):
                        self.v.appendErr(SemanticError(
                            f"Indexación sobre un valor no-arreglo: {base_type}",
                            line=ctx.start.line, column=ctx.start.column))
                        base_type = ErrorType()
                        continue

                    idx_t = self.v.visit(suf.expression())
                    if not isinstance(idx_t, IntegerType):
                        self.v.appendErr(SemanticError(
                            f"Índice no entero en acceso de arreglo: se encontró {idx_t}",
                            line=ctx.start.line, column=ctx.start.column))
                        base_type = ErrorType()
                        continue

                    # Validación estática de rango para literales
                    if lit_t is not None and isinstance(lit_t, ArrayType):
                        try:
                            idx_txt = suf.expression().getText()
                            if (idx_txt.isdigit() or (idx_txt.startswith('-') and idx_txt[1:].isdigit())) \
                               and hasattr(lit_t, "_literal_len"):
                                idx_val = int(idx_txt)
                                n = int(getattr(lit_t, "_literal_len", -1))
                                if not (0 <= idx_val < n):
                                    self.v.appendErr(SemanticError(
                                        f"Índice fuera de rango: {idx_val}; válido: 0..{n-1}",
                                        line=ctx.start.line, column=ctx.start.column))
                                    base_type = ErrorType()
                                    continue
                        except Exception:
                            pass

                    base_type = base_type.elem_type
                    if isinstance(lit_t, ArrayType):
                        lit_t = lit_t.elem_type
                    continue

                # CallExpr
                if isinstance(suf, CompiscriptParser.CallExprContext):
                    if not isinstance(base_type, FunctionType):
                        self.v.appendErr(SemanticError(
                            "Llamada a algo que no es función.",
                            line=ctx.start.line, column=ctx.start.column))
                        base_type = ErrorType()
                        continue

                    args_nodes = list(suf.arguments().expression()) if suf.arguments() else []
                    arg_types = [self.v.visit(e) for e in args_nodes]

                    expected = len(base_type.param_types)
                    got = len(arg_types)
                    if got != expected:
                        self.v.appendErr(SemanticError(
                            f"Número de argumentos inválido: esperados {expected}, recibidos {got}.",
                            line=ctx.start.line, column=ctx.start.column))
                        base_type = ErrorType()
                        continue

                    ok = True
                    for i, (pt, at) in enumerate(zip(base_type.param_types, arg_types), start=1):
                        if not isAssignable(pt, at):
                            self.v.appendErr(SemanticError(
                                f"Argumento #{i} incompatible: no se puede asignar {at} a {pt}.",
                                line=ctx.start.line, column=ctx.start.column))
                            ok = False
                    if not ok:
                        base_type = ErrorType()
                        continue

                    base_type = base_type.return_type if base_type.return_type is not None else VoidType()
                    continue

                # PropertyAccessExpr
                if isinstance(suf, CompiscriptParser.PropertyAccessExprContext):
                    prop_name = suf.Identifier().getText()
                    if not isinstance(base_type, ClassType):
                        self.v.appendErr(SemanticError(
                            f"Acceso a propiedades en tipo no-objeto '{base_type}'.",
                            line=ctx.start.line, column=ctx.start.column))
                        base_type = ErrorType()
                        continue

                    class_name = base_type.name
                    # Atributo
                    attr_t = self.v.class_handler.getAttributeType(class_name, prop_name)
                    if attr_t is not None:
                        base_type = attr_t
                        lit_t = None
                        continue

                    # Método (con herencia)
                    sig = self.v.method_registry.lookupMethod(f"{class_name}.{prop_name}")
                    if sig is None:
                        curr, seen = class_name, set()
                        while curr and curr not in seen and sig is None:
                            seen.add(curr)
                            sig = self.v.method_registry.lookupMethod(f"{curr}.{prop_name}")
                            if sig:
                                break
                            curr = getattr(self.v.class_handler._classes.get(curr), "base", None)

                    if sig:
                        param_types, ret_t = sig
                        ret_t = ret_t if ret_t is not None else VoidType()
                        params_wo_this = param_types[1:] if len(param_types) > 0 else []
                        base_type = FunctionType(params_wo_this, ret_t)
                        continue

                    self.v.appendErr(SemanticError(
                        f"Miembro '{prop_name}' no declarado en clase '{class_name}'.",
                        line=ctx.start.line, column=ctx.start.column))
                    base_type = ErrorType()
                    continue

            log(f"[lvalues][SEM] resultado tipo={base_type}", channel="semantic")
            return base_type

        finally:
            if hasattr(self.v, "emitter"):
                self.v.emitter.flow_terminated = old_barrier
