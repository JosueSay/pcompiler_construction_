from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import ArrayType, IntegerType, ErrorType, FunctionType, ClassType, VoidType
from semantic.symbol_kinds import SymbolCategory
from semantic.type_system import isAssignable
from logs.logger_semantic import log_semantic
from semantic.errors import SemanticError
from ir.tac import Op

class LValuesAnalyzer:
    """
    Procesa leftHandSide y aplica suffixOps: index, call, property.
    Emite TAC de lectura cuando actúa como rvalue (encadenamiento),
    y deja preparado el 'place' final del receptor.
    """
    def __init__(self, v):
        self.v = v
        

        
    def setPlace(self, node, place: str, is_temp: bool) -> None:
        try:
            setattr(node, "_place", place)
            setattr(node, "_is_temp", is_temp)
        except Exception:
            pass

    def getPlace(self, node) -> str | None:
        return getattr(node, "_place", None)

    def isTempNode(self, node) -> bool:
        return bool(getattr(node, "_is_temp", False))

    def freeIfTemp(self, node) -> None:
        if not self.isTempNode(node):
            return
        name = self.getPlace(node)
        if not name:
            return
        self.v.emitter.temp_pool.free(name, "*")



    def visitLeftHandSide(self, ctx: CompiscriptParser.LeftHandSideContext):
        # Evaluar el receptor base (primaryAtom)
        base_type = self.v.visit(ctx.primaryAtom())
        base_node = ctx.primaryAtom()
        base_place = self.getPlace(base_node) or base_node.getText()

        # rangos para literales
        lit_t = None
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

        # Recorrer sufijos
        for suf in ctx.suffixOp():
            if isinstance(base_type, ErrorType):
                continue

            # --- IndexExpr: lectura rvalue encadenada ---
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

                # Validación estática de rango (si había literal)
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

                # Emisión de lectura: t = base[index]
                idx_place = getattr(suf.expression(), "_place", suf.expression().getText())
                t = self.v.emitter.temp_pool.newTemp("ref")  # el valor podría ser ref/primitivo; usamos genérico
                self.v.emitter.emit(Op.INDEX_LOAD, arg1=base_place, arg2=idx_place, res=t)
                # liberar índice si era temporal
                if getattr(suf.expression(), "_is_temp", False):
                    self.v.emitter.temp_pool.free(idx_place, "*")
                # El resultado pasa a ser el nuevo receptor encadenado
                base_place = t
                base_type = base_type.elem_type
                if isinstance(lit_t, ArrayType):
                    lit_t = lit_t.elem_type
                # marcar place en el sufijo para posibles usos
                self.setPlace(suf, base_place, True)
                continue

            # CallExpr
            if isinstance(suf, CompiscriptParser.CallExprContext):
                if not isinstance(base_type, FunctionType):
                    self.v.appendErr(SemanticError(
                        "Llamada a algo que no es función.",
                        line=ctx.start.line, column=ctx.start.column))
                    base_type = ErrorType()
                    continue

                arg_types = []
                if suf.arguments():
                    for e in suf.arguments().expression():
                        arg_types.append(self.v.visit(e))

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
                base_type = base_type.return_type if ok else ErrorType()
                # No emitimos TAC de call aquí (fase de funciones/RA)
                continue

            # --- PropertyAccessExpr: lectura rvalue encadenada ---
            if isinstance(suf, CompiscriptParser.PropertyAccessExprContext):
                prop_name = suf.Identifier().getText()

                if not isinstance(base_type, ClassType):
                    self.v.appendErr(SemanticError(
                        f"Acceso a propiedades en tipo no-objeto '{base_type}'.",
                        line=ctx.start.line, column=ctx.start.column))
                    base_type = ErrorType()
                    continue

                class_name = base_type.name
                attr_t = self.v.class_handler.get_attribute_type(class_name, prop_name)
                if attr_t is None:
                    # ¿método? semántica lo resolverá como FunctionType; aquí solo lectura de atributo, si no es atributo otra fase lo maneja
                    self.v.appendErr(SemanticError(
                        f"Miembro '{prop_name}' no declarado en clase '{class_name}'.",
                        line=ctx.start.line, column=ctx.start.column))
                    base_type = ErrorType()
                    continue

                # Emisión de lectura de campo: t = base.f
                t = self.v.emitter.temp_pool.newTemp("ref")
                self.v.emitter.emit(Op.FIELD_LOAD, arg1=base_place, res=t, label=prop_name)
                base_place = t
                base_type = attr_t
                self.setPlace(suf, base_place, True)
                continue

        self.setPlace(ctx, base_place, base_place.startswith("t"))
        return base_type