from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import (
    ArrayType, IntegerType, ErrorType, FunctionType, ClassType, VoidType
)
from semantic.type_system import isAssignable
from semantic.errors import SemanticError
from logs.logger import log


class LValuesAnalyzer:
    """
    Valida semántica de `leftHandSide` y sus `suffixOp` (indexación, llamadas, acceso a propiedades).

    Notas:
      - No emite TAC.
      - Reporta errores de tipos/forma.
      - Devuelve el tipo resultante.
    """

    def __init__(self, v):
        log("\n" + "="*80, channel="semantic")
        log("===== [LValuesAnalyzer] Inicio SEMÁNTICO =====", channel="semantic")
        log("="*80 + "\n", channel="semantic")
        self.v = v

    def visitLeftHandSide(self, ctx: CompiscriptParser.LeftHandSideContext):
        old_barrier = getattr(self.v, "emitter", None).flow_terminated if hasattr(self.v, "emitter") else None
        if hasattr(self.v, "emitter"):
            self.v.emitter.flow_terminated = True

        try:
            # Tipo base del átomo
            base_type = self.v.visit(ctx.primaryAtom())
            log(f"[LHS] inicio: {ctx.getText()}, base_type inicial={base_type}", channel="semantic")

            try:
                setattr(ctx.primaryAtom(), "_type", base_type)
            except Exception:
                pass

            lit_t = None
            # Validación de arreglos literales
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
                log(f"[LHS] suffixOp: {type(suf).__name__}, base_type antes={base_type}", channel="semantic")

                # ---------------------------
                # IndexExpr
                if isinstance(suf, CompiscriptParser.IndexExprContext):
                    if not isinstance(base_type, ArrayType):
                        self.v.appendErr(SemanticError(
                            f"Indexación sobre un valor no-arreglo: {base_type}",
                            line=ctx.start.line, column=ctx.start.column))
                        log("\t[error] indexación sobre no-arreglo", channel="semantic")
                        base_type = ErrorType()
                        continue

                    idx_t = self.v.visit(suf.expression())
                    if not isinstance(idx_t, IntegerType):
                        self.v.appendErr(SemanticError(
                            f"Índice no entero en acceso de arreglo: se encontró {idx_t}",
                            line=ctx.start.line, column=ctx.start.column))
                        log(f"\t[error] índice no entero: {idx_t}", channel="semantic")
                        base_type = ErrorType()
                        continue

                    # Validación estática de rango
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
                                    log(f"\t[error] índice fuera de rango: {idx_val}", channel="semantic")
                                    base_type = ErrorType()
                                    continue
                        except Exception:
                            pass

                    base_type = base_type.elem_type
                    log(f"[LHS] IndexExpr: base_type actualizado={base_type}", channel="semantic")

                    if isinstance(lit_t, ArrayType):
                        lit_t = lit_t.elem_type
                    continue

                # ---------------------------
                # CallExpr
                if isinstance(suf, CompiscriptParser.CallExprContext):
                    if not isinstance(base_type, FunctionType):
                        self.v.appendErr(SemanticError(
                            "Llamada a algo que no es función.",
                            line=ctx.start.line, column=ctx.start.column))
                        log("\t[error] llamada a no-función", channel="semantic")
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
                        log(f"\t[error] args inválidos: esperados {expected}, recibidos {got}", channel="semantic")
                        base_type = ErrorType()
                        continue

                    ok = True
                    for i, (pt, at) in enumerate(zip(base_type.param_types, arg_types), start=1):
                        if not isAssignable(pt, at):
                            self.v.appendErr(SemanticError(
                                f"Argumento #{i} incompatible: no se puede asignar {at} a {pt}.",
                                line=ctx.start.line, column=ctx.start.column))
                            log(f"\t[error] arg#{i} incompatible: {at} -> {pt}", channel="semantic")
                            ok = False
                    if not ok:
                        base_type = ErrorType()
                        continue

                    base_type = base_type.return_type if base_type.return_type else VoidType()
                    log(f"[LHS] CallExpr: base_type actualizado={base_type}", channel="semantic")

                    continue

                # ---------------------------
                # PropertyAccessExpr
                if isinstance(suf, CompiscriptParser.PropertyAccessExprContext):
                    prop_name = suf.Identifier().getText()
                    if not isinstance(base_type, ClassType):
                        self.v.appendErr(SemanticError(
                            f"Acceso a propiedades en tipo no-objeto '{base_type}'.",
                            line=ctx.start.line, column=ctx.start.column))
                        log(f"\t[error] acceso a propiedad en no-objeto: {base_type}", channel="semantic")
                        base_type = ErrorType()
                        continue

                    class_name = base_type.name
                    attr_t = self.v.class_handler.getAttributeType(class_name, prop_name)
                    if attr_t:
                        base_type = attr_t
                        lit_t = None
                        log(f"[LHS] PropertyAccessExpr: {prop_name}, base_type actualizado={base_type}", channel="semantic")
                        continue
                    


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
                        ret_t = ret_t if ret_t else VoidType()
                        params_wo_this = param_types[1:] if len(param_types) > 0 else []
                        base_type = FunctionType(params_wo_this, ret_t)
                        continue

                    self.v.appendErr(SemanticError(
                        f"Miembro '{prop_name}' no declarado en clase '{class_name}'.",
                        line=ctx.start.line, column=ctx.start.column))
                    log(f"\t[error] miembro no declarado: {prop_name}", channel="semantic")
                    base_type = ErrorType()
                    continue

            log(f"[lvalues][SEM] resultado tipo={base_type}", channel="semantic")

            try:
                setattr(ctx, "_type", base_type)
            except Exception:
                pass

            return base_type

        finally:
            if hasattr(self.v, "emitter"):
                self.v.emitter.flow_terminated = old_barrier
