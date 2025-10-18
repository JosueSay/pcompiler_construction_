from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import ArrayType, ErrorType, FunctionType, ClassType, VoidType
from logs.logger import log
from utils.ast_utils import getPlace, setPlace, deepPlace, typeToTempKind
from ir.tac import Op
from ir.addr_format import place_of_symbol
from semantic.symbol_kinds import SymbolCategory

class TacLValues:
    """
    Emite TAC para expresiones de lado izquierdo (LeftHandSide) y sus sufijos:
      - Indexación:    a[i]
      - Llamadas:      f(a, b) / método enlazado a un receptor
      - Propiedades:   obj.campo (lectura) / preparación de método para llamada

    Procesa suffixOp en orden izquierda→derecha y prepara correctamente el
    “método enlazado” (receiver + label) antes del CallExpr.
    """

    def __init__(self, v):
        """
        Inicializa el generador de TAC para LValues.
        :param v: Visitador/contexto que contiene emitter, scopeManager, etc.
        """
        self.v = v
        log("=" * 60, channel="tac")
        log("↳ [TacLValues] initialized", channel="tac")
        log("=" * 60, channel="tac")

    def resolveFieldOffset(self, owner: str, field: str):
        """
        Devuelve el offset numérico del campo si está disponible.
        Prioriza self.v.class_layout; si no existe, intenta usar class_handler.getFieldOffset.
        Si falla, retorna None (el caller decidirá cómo degradar).
        """
        # 1) Intentar en class_layout (construido por TacGenerator.buildClassLayout)
        try:
            layout = getattr(self.v, "class_layout", {}) or {}
            off = layout.get(owner, {}).get(field)
            if isinstance(off, int):
                log(f"\t[TAC_LVALUES][resolveFieldOffset] from layout: owner={owner}, field={field}, offset={off}", channel="tac")
                return off
        except Exception:
            pass

        # 2) Intentar via class_handler (semántica, si lo expone)
        try:
            ch = getattr(self.v, "class_handler", None)
            if ch is not None and hasattr(ch, "getFieldOffset"):
                off = ch.getFieldOffset(owner, field)
                if isinstance(off, int):
                    log(f"\t[TAC_LVALUES][resolveFieldOffset] from class_handler: owner={owner}, field={field}, offset={off}", channel="tac")
                    return off
        except Exception:
            pass

        log(f"\t[TAC_LVALUES][resolveFieldOffset] not found: owner={owner}, field={field}", channel="tac")
        return None

    # --------------------------- util interno ----------------------------
    def symType(self, name: str):
        """Resuelve el tipo de un símbolo local/global probando varios nombres de atributo."""
        try:
            sym = self.v.scopeManager.lookup(name)
        except Exception:
            sym = None
        if not sym:
            return None
        for attr in ("type", "decl_type", "var_type", "declared_type", "inferred_type",
                     "value_type", "init_value_type"):
            t = getattr(sym, attr, None)
            if t is not None:
                return t
        return None

    def visitLeftHandSide(self, ctx: CompiscriptParser.LeftHandSideContext):
        log(f"\t[TAC_LVALUES] enter LHS: '{ctx.getText()}'", channel="tac")

        # 1) Átomo base
        base_node = ctx.primaryAtom()
        self.v.visit(base_node)
        p0, is_tmp0 = deepPlace(base_node)
        base_place = p0 or base_node.getText()
        base_is_temp = bool(is_tmp0)

        log(f"\t[TAC_LVALUES] base_node: place={base_place}, is_temp={base_is_temp}", channel="tac")

        
        try:
            base_txt = base_node.getText()
        except Exception:
            base_txt = base_place

        if (
            base_place == base_txt
            and isinstance(base_txt, str)
            and base_txt not in ("this",)
            and "." not in base_txt
            and "[" not in base_txt
        ):
            try:
                sym = self.v.scopeManager.lookup(base_txt)
                if sym is not None and getattr(sym, "category", None) != SymbolCategory.FUNCTION:
                    addr = place_of_symbol(sym)
                    base_place = addr
                    base_is_temp = False
                    setPlace(base_node, addr, False)
            except Exception:
                pass

        # 2) Tipo base (de semántica / símbolos)
        base_type = getattr(base_node, "_type", None)
        if base_type is None and base_place == "this":
            owner = getattr(self.v, "current_method_owner", None)
            if owner:
                base_type = ClassType(owner)
        if base_type is None:
            # buscar tipo del símbolo con heurística robusta
            st = self.symType(base_place)
            if st is not None:
                base_type = st
            else:
                # función global
                try:
                    sym = self.v.scopeManager.lookup(base_place)
                except Exception:
                    sym = None
                if sym is not None:
                    from semantic.symbol_kinds import SymbolCategory
                    if sym.category == SymbolCategory.FUNCTION:
                        ftype = FunctionType(getattr(sym, "param_types", []) or [],
                                             getattr(sym, "return_type", None) or VoidType())
                        setattr(ftype, "_label", getattr(sym, "label", None) or f"{sym.name}")
                        base_type = ftype

        # 3) Sufijos encadenados (ordenados por tokenIndex izq→der)
        try:
            sufs = list(ctx.suffixOp())
            sufs.sort(key=lambda n: getattr(getattr(n, "start", None), "tokenIndex", 0))
        except Exception:
            sufs = list(ctx.suffixOp())

        for suf in sufs:

            # 3.a) Indexación a[i]
            if isinstance(suf, CompiscriptParser.IndexExprContext):
                if isinstance(base_type, ErrorType):
                    continue

                log(f"\t[TAC_LVALUES] IndexExpr: base={base_place}", channel="tac")
                idx_expr = suf.expression()
                self.v.visit(idx_expr)
                p_idx, is_idx_tmp = deepPlace(idx_expr)
                idx_place = p_idx or idx_expr.getText()

                elem_t = base_type.elem_type if isinstance(base_type, ArrayType) else None
                temp_kind = typeToTempKind(elem_t) if elem_t is not None else "*"
                t_val = self.v.emitter.temp_pool.newTemp(temp_kind)

                try:
                    t_len, _ = self.v.emitter.emitBoundsCheck(idx_place, base_place)
                except Exception:
                    t_len = None

                self.v.emitter.emit(Op.INDEX_LOAD, arg1=base_place, arg2=idx_place, res=t_val)

                if t_len:
                    self.v.emitter.temp_pool.free(t_len, "*")
                if is_idx_tmp:
                    self.v.emitter.temp_pool.free(idx_place, "*")
                if base_is_temp:
                    self.v.emitter.temp_pool.free(base_place, "*")

                base_place = t_val
                base_is_temp = True
                base_type = elem_t if elem_t is not None else base_type
                setPlace(suf, base_place, True)
                # ← anotar tipo en el nodo del sufijo
                try:
                    setattr(suf, "_type", base_type)
                except Exception:
                    pass
                continue

            # 3.b) Llamadas: f(...), y métodos enlazados
            if isinstance(suf, CompiscriptParser.CallExprContext):
                if isinstance(base_type, ErrorType):
                    continue

                log(f"\t[TAC_LVALUES] CallExpr: base={base_place}", channel="tac")
                # Evalúa argumentos
                args_nodes = list(suf.arguments().expression()) if suf.arguments() else []
                for e in args_nodes:
                    self.v.visit(e)
                    
                expected_params = None
                # a) Si es método enlazado, podemos reconstruir la firma desde method_registry
                owner = getattr(base_type, "_decl_owner", None) or getattr(base_type, "_bound_receiver", None)
                mname = getattr(base_type, "_method_name", None)
                if owner and mname:
                    sig = self.v.method_registry.lookupMethod(f"{owner}.{mname}")
                    if sig:
                        param_types, _ret = sig
                        # param_types incluye 'this' como primer parámetro → restamos 1 para args explícitos
                        expected_params = max(0, len(param_types) - 1)

                # b) Si es función global (FunctionType con param_types)
                elif isinstance(base_type, FunctionType):
                    try:
                        expected_params = len(getattr(base_type, "param_types", []) or [])
                    except Exception:
                        expected_params = None

                # Log de desajuste
                if expected_params is not None and expected_params != len(args_nodes):
                    log(f"\t[TAC_LVALUES][warn] arity mismatch: expected={expected_params}, passed={len(args_nodes)} "
                        f"for call base='{base_place}'", channel="tac")

                n_params = 0

                # Receiver (si es método enlazado)
                recv_place = getattr(base_type, "_recv_place", None)
                recv_is_temp = bool(getattr(base_type, "_recv_is_temp", False))
                if recv_place is not None:
                    self.v.emitter.emit(Op.PARAM, arg1=recv_place)
                    n_params += 1

                # Args explícitos
                for e in args_nodes:
                    p, is_tmp = deepPlace(e)
                    aplace = p or e.getText()
                    self.v.emitter.emit(Op.PARAM, arg1=aplace)
                    if is_tmp:
                        self.v.emitter.temp_pool.free(aplace, "*")
                    n_params += 1

                # Closure?
                is_function_type = isinstance(base_type, FunctionType)
                can_be_closure = is_function_type and recv_place is None and base_is_temp
                ret_t = getattr(base_type, "return_type", None) or VoidType()

                callee_text = getattr(ctx.primaryAtom(), "getText", lambda: str(base_place))()
                is_method = (recv_place is not None) or (getattr(base_type, "_method_name", None) is not None)
                label_preview = getattr(base_type, "_label", None)
                log(f"\t[TacLValues][call] callee={callee_text}, is_method={is_method}, "
                    f"expected_params={expected_params}, passed={len(args_nodes)}, "
                    f"label={label_preview}", channel="tac")

                if can_be_closure:
                    clos_place = base_place
                    if isinstance(ret_t, VoidType):
                        self.v.emitter.emitCallC(clos_place, n_params)
                        base_place = ""
                        base_is_temp = False
                        setPlace(suf, "", False)
                    else:
                        t_ret = self.v.emitter.temp_pool.newTemp(typeToTempKind(ret_t))
                        self.v.emitter.emitCallC(clos_place, n_params, dst=t_ret)
                        base_place = t_ret
                        base_is_temp = True
                        setPlace(suf, t_ret, True)

                    base_type = ret_t
                    if recv_place is not None and recv_is_temp:
                        self.v.emitter.temp_pool.free(recv_place, "*")
                    self.v.emitter.temp_pool.free(clos_place, "*")
                    continue

                # Llamada directa (función o método)
                f_label = getattr(base_type, "_label", None)
                if f_label is None:
                    owner = getattr(base_type, "_decl_owner", None)
                    mname = getattr(base_type, "_method_name", None)
                    if owner and mname:
                        f_label = f"{owner}_{mname}"
                    else:
                        base_name = getattr(ctx.primaryAtom(), "_place", None) or ctx.primaryAtom().getText()
                        try:
                            fsym = self.v.scopeManager.lookup(base_name)
                            f_label = getattr(fsym, "label", None) or f"{base_name}"
                        except Exception:
                            f_label = f"{base_name}"

                log(f"\t[TacLValues][call] callee={callee_text}, is_method={is_method}, "
                    f"expected_params={expected_params}, passed={len(args_nodes)}, "
                    f"label={f_label}", channel="tac")

                if isinstance(ret_t, VoidType):
                    self.v.emitter.emitCall(f_label, n_params)
                    base_place = ""
                    base_is_temp = False
                    setPlace(suf, "", False)
                else:
                    t_ret = self.v.emitter.temp_pool.newTemp(typeToTempKind(ret_t))
                    self.v.emitter.emitCall(f_label, n_params, dst=t_ret)
                    base_place = t_ret
                    base_is_temp = True
                    setPlace(suf, t_ret, True)

                if recv_place is not None and recv_is_temp:
                    self.v.emitter.temp_pool.free(recv_place, "*")

                base_type = ret_t
                try:
                    setattr(suf, "_type", base_type)
                except Exception:
                    pass

                log(f"\t[TAC_LVALUES] CallExpr result: place={base_place}", channel="tac")
                continue

            # 3.c) Acceso a propiedad: campo o método enlazado
            if isinstance(suf, CompiscriptParser.PropertyAccessExprContext):
                prop_name = suf.Identifier().getText()
                log(f"\t[TAC_LVALUES] PropertyAccessExpr: {prop_name} on base={base_place}", channel="tac")

                # Campo de clase → FIELD_LOAD
                attr_t = None
                if isinstance(base_type, ClassType):
                    attr_t = self.v.class_handler.getAttributeType(base_type.name, prop_name)

                if attr_t is not None:
                    
                    t_val = self.v.emitter.temp_pool.newTemp(typeToTempKind(attr_t))

                    owner_name = base_type.name
                    off = self.resolveFieldOffset(owner_name, prop_name)

                    label_for_emit = off if isinstance(off, int) else prop_name  # fallback seguro

                    log(
                        f"\t[TAC_LVALUES] FIELD_LOAD resolve: owner={owner_name}, field={prop_name}, "
                        f"offset={off}, using_label={label_for_emit}",
                        channel="tac"
                    )

                    q = self.v.emitter.emit(Op.FIELD_LOAD, arg1=base_place, res=t_val, label=label_for_emit)

                    # Guardar metadatos útiles para depuración/backends
                    try:
                        if q is not None:
                            if isinstance(off, int):
                                setattr(q, "_field_offset", off)
                            setattr(q, "_field_owner", owner_name)
                            setattr(q, "_field_name", prop_name)
                    except Exception:
                        pass


                    if base_is_temp:
                        self.v.emitter.temp_pool.free(base_place, "*")

                    base_place = t_val
                    base_is_temp = True
                    base_type = attr_t
                    setPlace(suf, base_place, True)
                    # ← anotar tipo en el nodo del sufijo (y opcional log)
                    try:
                        setattr(suf, "_type", base_type)
                    except Exception:
                        pass
                    continue

                # Método (con herencia)
                owner = getattr(base_type, "name", None)
                if owner is None:
                    st = self.symType(base_place)
                    if isinstance(st, ClassType):
                        owner = st.name
                    elif base_place == "this":
                        owner = getattr(self.v, "current_method_owner", None)

                sig = self.v.method_registry.lookupMethod(f"{owner}.{prop_name}") if owner else None
                if sig is None and owner:
                    curr, seen = owner, set()
                    while curr and curr not in seen and sig is None:
                        seen.add(curr)
                        sig = self.v.method_registry.lookupMethod(f"{curr}.{prop_name}")
                        if sig:
                            owner = curr
                            break
                        curr = getattr(self.v.class_handler._classes.get(curr), "base", None)

                if sig:
                    param_types, ret_t = sig
                    ret_t = ret_t or VoidType()
                    params_wo_this = param_types[1:] if len(param_types) > 0 else []

                    ftype = FunctionType(params_wo_this, ret_t)
                    try:
                        setattr(ftype, "_bound_receiver", owner)
                        setattr(ftype, "_method_name", prop_name)
                        setattr(ftype, "_recv_place", base_place)
                        setattr(ftype, "_recv_is_temp", base_is_temp)
                        setattr(ftype, "_decl_owner", owner)

                        qname = f"{owner}.{prop_name}" if owner else prop_name
                        fsym = self.v.scopeManager.lookup(qname)
                        if fsym is not None and getattr(fsym, "label", None):
                            setattr(ftype, "_label", fsym.label)
                        else:
                            setattr(ftype, "_label", f"{owner}_{prop_name}" if owner else f"{prop_name}")
                    except Exception:
                        pass

                    base_type = ftype
                    setPlace(suf, base_place, base_is_temp)
                    continue

                # Ni atributo ni método: ya reportado por semántica
                log(f"\t[TAC_LVALUES] PropertyAccessExpr result: place={base_place}", channel="tac")
                continue

        # 4) Place final
        setPlace(ctx, base_place, base_is_temp)
        try:
            setattr(ctx, "_type", base_type)
        except Exception:
            pass
        log(f"\t[TAC_LVALUES] exit LHS: type={base_type}, place={base_place}", channel="tac")
        return base_type
