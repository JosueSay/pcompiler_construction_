from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import ArrayType, IntegerType, ErrorType, FunctionType, ClassType, VoidType
from semantic.symbol_kinds import SymbolCategory
from semantic.type_system import isAssignable
from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic
from ir.tac import Op

class LValuesAnalyzer:
    """
    Procesa leftHandSide y aplica suffixOps: index, call, property.
    - Mantiene validaciones semánticas completas (atributos y métodos con herencia).
    - Emite TAC para lecturas rvalue encadenadas:
        * a[i]      => INDEX_LOAD
        * obj.f     => FIELD_LOAD (solo si 'f' es atributo; si es método => FunctionType)
    - Conserva y propaga '_place' y marca temporales para que otras fases puedan usarlos.
    """

    def __init__(self, v):
        self.v = v

    # --------- helpers de place/temporales (coherentes con expressions) ---------
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
        # Usamos comodín de clase al liberar desde aquí
        self.v.emitter.temp_pool.free(name, "*")

    # --------------------------- núcleo ----------------------------

    def visitLeftHandSide(self, ctx: CompiscriptParser.LeftHandSideContext):
        # Evaluar el receptor base (primaryAtom)
        log_semantic(f"[lvalue] enter LHS: '{ctx.getText()}'")
        base_type = self.v.visit(ctx.primaryAtom())
        base_node = ctx.primaryAtom()
        base_place = self.getPlace(base_node) or base_node.getText()

        # Pista opcional: tipo literal para validar rangos estáticos en indexaciones
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

        # Recorrer sufijos encadenados
        for suf in ctx.suffixOp():
            if isinstance(base_type, ErrorType):
                # Arrastramos el error pero seguimos para recolectar más diagnósticos
                continue

            # --- [a[i]]: IndexExpr -> lectura rvalue encadenada ---
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

                # Validación estática de rango si venimos de literal y el índice es entero literal
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

                # TAC: t = base[index]
                idx_place = getattr(suf.expression(), "_place", suf.expression().getText())
                t = self.v.emitter.temp_pool.newTemp(self.v.exprs.typeToTempKind(base_type.elem_type))
                self.v.emitter.emit(Op.INDEX_LOAD, arg1=base_place, arg2=idx_place, res=t)
                # liberar temporal del índice si aplica
                if getattr(suf.expression(), "_is_temp", False):
                    self.v.emitter.temp_pool.free(idx_place, "*")

                base_place = t
                base_type = base_type.elem_type
                if isinstance(lit_t, ArrayType):
                    lit_t = lit_t.elem_type
                self.setPlace(suf, base_place, True)
                continue

            # --- CallExpr: emitir TAC de llamada ---
            if isinstance(suf, CompiscriptParser.CallExprContext):
                if not isinstance(base_type, FunctionType):
                    self.v.appendErr(SemanticError(
                        "Llamada a algo que no es función.",
                        line=ctx.start.line, column=ctx.start.column))
                    base_type = ErrorType()
                    continue
                
                # --- VALIDACIÓN semántica (conteo y tipos) ---
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
                
                recv_place = None


                # 1) param implícito 'this' si es método
                n_params = 0
                f_label  = getattr(base_type, "_label", None)
                if hasattr(base_type, "_recv_place"):
                    recv_place = getattr(base_type, "_recv_place")
                    self.v.emitter.emit(Op.PARAM, arg1=recv_place)
                    n_params += 1
                    if f_label is None:
                        owner = getattr(base_type, "_decl_owner", None) or getattr(base_type, "_bound_receiver", None)
                        mname = getattr(base_type, "_method_name", None)
                        f_label = f"f_{owner}_{mname}"

                # 2) params de usuario (izq→der)
                args = args_nodes     # <- usa los mismos
                for e in args:
                    p, is_tmp = self.v.exprs.deepPlace(e)
                    aplace = p or e.getText()
                    self.v.emitter.emit(Op.PARAM, arg1=aplace)
                    if is_tmp:
                        self.v.emitter.temp_pool.free(aplace, "*")
                    n_params += 1

                # === ¿Es una closure? ===
                clos_place = getattr(base_type, "_closure_place", None)

                if clos_place:
                    # Llamada a *closure*: callc <closure>, n
                    ret_t = base_type.return_type
                    if isinstance(ret_t, VoidType):
                        self.v.emitter.emit(Op.CALLC, arg1=clos_place, arg2=str(n_params))
                        base_place = ""   # nada que encadenar
                        self.setPlace(suf, "", False)
                        base_type = ret_t
                    else:
                        t = self.v.emitter.temp_pool.newTemp(self.v.exprs.typeToTempKind(ret_t))
                        self.v.emitter.emit(Op.CALLC, arg1=clos_place, arg2=str(n_params), res=t)
                        base_place = t
                        base_type  = ret_t
                        self.setPlace(suf, t, True)

                    # liberar closure temp si fue temporal
                    if isinstance(clos_place, str) and clos_place.startswith("t"):
                        self.v.emitter.temp_pool.free(clos_place, "*")

                    # liberar 'this' implícito si fue temporal
                    if recv_place and isinstance(recv_place, str) and recv_place.startswith("t"):
                        self.v.emitter.temp_pool.free(recv_place, "*")
                    continue

                # === Llamada *directa* a función (sin closure) ===
                # 3) label de funciones libres si no lo tenemos
                if f_label is None:
                    base_name = getattr(ctx.primaryAtom(), "_place", None) or ctx.primaryAtom().getText()
                    fsym = self.v.scopeManager.lookup(base_name)
                    f_label = getattr(fsym, "label", None) or f"f_{base_name}"

                # 4) emitir call y propagar place
                ret_t = base_type.return_type
                if isinstance(ret_t, VoidType):
                    self.v.emitter.emit(Op.CALL, arg1=f_label, arg2=str(n_params))
                    base_place = ""
                    self.setPlace(suf, "", False)
                    base_type = ret_t
                else:
                    t = self.v.emitter.temp_pool.newTemp(self.v.exprs.typeToTempKind(ret_t))
                    self.v.emitter.emit(Op.CALL, arg1=f_label, arg2=str(n_params), res=t)
                    base_place = t
                    base_type  = ret_t
                    self.setPlace(suf, t, True)

                # liberar 'this' implícito si fue temporal
                if recv_place and isinstance(recv_place, str) and recv_place.startswith("t"):
                    self.v.emitter.temp_pool.free(recv_place, "*")
                continue


            # --- acceso a propiedad/método: expr.Identifier ---
            if isinstance(suf, CompiscriptParser.PropertyAccessExprContext):
                prop_name = suf.Identifier().getText()

                if not isinstance(base_type, ClassType):
                    self.v.appendErr(SemanticError(
                        f"Acceso a propiedades en tipo no-objeto '{base_type}'.",
                        line=ctx.start.line, column=ctx.start.column))
                    base_type = ErrorType()
                    continue

                class_name = base_type.name

                # 1) ¿Atributo? (con lookup por herencia)
                attr_t = self.v.class_handler.get_attribute_type(class_name, prop_name)
                if attr_t is not None:
                    # t = base.f   (lectura de atributo)
                    t = self.v.emitter.temp_pool.newTemp(self.v.exprs.typeToTempKind(attr_t))
                    q = self.v.emitter.emit(Op.FIELD_LOAD, arg1=base_place, res=t, label=prop_name)
                    # hook opcional de offset (no afecta al TAC textual)
                    try:
                        off = self.v.class_handler.get_field_offset(class_name, prop_name)
                        if q is not None and off is not None:
                            setattr(q, "_field_offset", off)      # metadata para CG
                            setattr(q, "_field_owner", class_name) # opcional, por si ayuda
                    except Exception:
                        pass

                    base_place = t
                    base_type  = attr_t
                    self.setPlace(suf, base_place, True)
                    lit_t = None
                    continue

                # 2) ¿Método? (resuelve a FunctionType; NO emite TAC aquí)
                #    Intentamos: method_registry qname en esta clase o en la jerarquía,
                #    o un símbolo con nombre calificado "<cls>.<m>".
                sig = self.v.method_registry.lookup(f"{class_name}.{prop_name}")
                owner = class_name if sig is not None else None
                if sig is None:
                    # subir por bases
                    curr, seen = class_name, set()
                    while curr and curr not in seen and sig is None:
                        seen.add(curr)
                        sig = self.v.method_registry.lookup(f"{curr}.{prop_name}")
                        if sig:
                            owner = curr
                            break
                        curr = getattr(self.v.class_handler._classes.get(curr), "base", None)

                if sig:
                    param_types, ret_t = sig
                    ret_t = ret_t or VoidType()
                    params_wo_this = param_types[1:] if len(param_types) > 0 else []
                    ftype = FunctionType(params_wo_this, ret_t)

                    # anotar receptor y label para la llamada
                    try:
                        setattr(ftype, "_bound_receiver", class_name)
                        setattr(ftype, "_method_name", prop_name)
                        setattr(ftype, "_recv_place", base_place)
                        setattr(ftype, "_decl_owner", owner or class_name)
                        # intenta tomar label desde la tabla, si existe:
                        qname = f"{owner}.{prop_name}" if owner else f"{class_name}.{prop_name}"
                        fsym = self.v.scopeManager.lookup(qname)
                        if fsym is not None and getattr(fsym, "label", None):
                            setattr(ftype, "_label", fsym.label)
                        else:
                            setattr(ftype, "_label", f"f_{owner or class_name}_{prop_name}")
                    except Exception:
                        pass

                    base_type = ftype
                    # no cambiamos base_place (no hay FIELD_LOAD de métodos)
                    self.setPlace(suf, base_place, base_place.startswith("t"))
                    continue

                # 3) Nada encontrado: error
                self.v.appendErr(SemanticError(
                    f"Miembro '{prop_name}' no declarado en clase '{class_name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                base_type = ErrorType()
                continue

        # Al terminar el encadenamiento, fija el place del LHS completo
        self.setPlace(ctx, base_place, isinstance(base_place, str) and base_place.startswith("t"))
        return base_type
