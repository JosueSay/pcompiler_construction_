from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import ArrayType, ErrorType, FunctionType, ClassType, VoidType
from logs.logger import log, logFunction
from utils.ast_utils import getPlace, setPlace, deepPlace, typeToTempKind
from ir.tac import Op


class TacLValues:
    """
    Emite TAC para expresiones de lado izquierdo (LeftHandSide) y sus sufijos:
      - Indexación:    a[i]
      - Llamadas:      f(a, b)  / método enlazado a un receptor
      - Propiedades:   obj.campo  (lectura) / preparación de método para llamada

    Supone que la fase semántica ya validó tipos y registró metadatos necesarios.
    No hace chequeos semánticos; sólo baja a quads.
    """

    @logFunction(channel="tac")
    def __init__(self, v):
        log("[tac_lvalues] init", channel="tac")
        self.v = v

    # --------------------------- núcleo ----------------------------
    @logFunction(channel="tac")
    def visitLeftHandSide(self, ctx: CompiscriptParser.LeftHandSideContext):
        """
        Aplica, en orden, cada sufijo del LHS produciendo los cuádruplos adecuados.
        Publica en el nodo final su _place (temporal o receptor) para usos posteriores.
        """
        log(f"[lvalues][TAC] enter LHS: '{ctx.getText()}'", channel="tac")

        # 1) Átomo base (identificador, this, new, literal, (expr), etc.)
        base_node = ctx.primaryAtom()
        self.v.visit(base_node)  # asegura _place en el átomo
        base_place = getPlace(base_node) or base_node.getText()

        # 2) Inferencia del tipo base (clave para decidir qué emitir)
        base_type = getattr(base_node, "_type", None)

        # this -> ClassType del owner del método actual
        if base_type is None and base_place == "this":
            owner = getattr(self.v, "current_method_owner", None)
            if owner:
                base_type = ClassType(owner)

        # Identificador u otros: intenta resolver por símbolos
        if base_type is None:
            try:
                sym = self.v.scopeManager.lookup(base_place)
            except Exception:
                sym = None

            if sym is not None:
                from semantic.symbol_kinds import SymbolCategory
                if sym.category == SymbolCategory.FUNCTION:
                    # Construir FunctionType con firma real y label para llamadas directas
                    ftype = FunctionType(sym.param_types or [], sym.return_type or VoidType())
                    setattr(ftype, "_label", getattr(sym, "label", None) or f"f_{sym.name}")
                    base_type = ftype
                else:
                    base_type = getattr(sym, "type", None)

        # 3) Aplicar cada sufijo en orden
        for suf in ctx.suffixOp():

            # 3.a) Indexación: a[i] -> INDEX_LOAD (con bounds opcional)
            if isinstance(suf, CompiscriptParser.IndexExprContext):
                if isinstance(base_type, ErrorType):
                    continue

                self.v.visit(suf.expression())
                idx_place = getattr(suf.expression(), "_place", suf.expression().getText())

                elem_t = base_type.elem_type if isinstance(base_type, ArrayType) else None
                temp_kind = typeToTempKind(elem_t) if elem_t is not None else "*"
                t_val = self.v.emitter.temp_pool.newTemp(temp_kind)

                # Bounds check best-effort (si el emitter lo soporta)
                try:
                    t_len, _l_ok = self.v.emitter.emitBoundsCheck(idx_place, base_place)
                except Exception:
                    t_len = None

                self.v.emitter.emit(Op.INDEX_LOAD, arg1=base_place, arg2=idx_place, res=t_val)

                if t_len:
                    self.v.emitter.temp_pool.free(t_len, "*")
                if getattr(suf.expression(), "_is_temp", False):
                    self.v.emitter.temp_pool.free(idx_place, "*")

                base_place = t_val
                base_type = elem_t if elem_t is not None else base_type
                setPlace(suf, base_place, True)
                continue

            # 3.b) Llamadas: f(...), incluyendo métodos enlazados a receptor
            if isinstance(suf, CompiscriptParser.CallExprContext):
                if isinstance(base_type, ErrorType):
                    continue

                args_nodes = list(suf.arguments().expression()) if suf.arguments() else []
                for e in args_nodes:
                    self.v.visit(e)

                n_params = 0

                # Método enlazado: pasar receptor como primer parámetro
                recv_place = getattr(base_type, "_recv_place", None)
                if recv_place is not None:
                    self.v.emitter.emit(Op.PARAM, arg1=recv_place)
                    n_params += 1

                # Parámetros explícitos
                for e in args_nodes:
                    p, is_tmp = deepPlace(e)
                    aplace = p or e.getText()
                    self.v.emitter.emit(Op.PARAM, arg1=aplace)
                    if is_tmp:
                        self.v.emitter.temp_pool.free(aplace, "*")
                    n_params += 1

                # ¿Closure materializado?
                clos_place = getattr(base_type, "_closure_place", None)
                ret_t = getattr(base_type, "return_type", None) or VoidType()

                if clos_place:
                    # Llamada a closure
                    if isinstance(ret_t, VoidType):
                        self.v.emitter.emit(Op.CALLC, arg1=clos_place, arg2=str(n_params))
                        base_place = ""
                        setPlace(suf, "", False)
                    else:
                        t_ret = self.v.emitter.temp_pool.newTemp(typeToTempKind(ret_t))
                        self.v.emitter.emit(Op.CALLC, arg1=clos_place, arg2=str(n_params), res=t_ret)
                        base_place = t_ret
                        setPlace(suf, t_ret, True)

                    if isinstance(clos_place, str) and clos_place.startswith("t"):
                        self.v.emitter.temp_pool.free(clos_place, "*")
                    if isinstance(recv_place, str) and recv_place.startswith("t"):
                        self.v.emitter.temp_pool.free(recv_place, "*")

                    base_type = ret_t
                    continue

                # Llamada directa (función/método con label)
                f_label = getattr(base_type, "_label", None)
                if f_label is None:
                    base_name = getattr(ctx.primaryAtom(), "_place", None) or ctx.primaryAtom().getText()
                    try:
                        fsym = self.v.scopeManager.lookup(base_name)
                        f_label = getattr(fsym, "label", None) or f"f_{base_name}"
                    except Exception:
                        f_label = f"f_{base_name}"

                if isinstance(ret_t, VoidType):
                    self.v.emitter.emit(Op.CALL, arg1=f_label, arg2=str(n_params))
                    base_place = ""
                    setPlace(suf, "", False)
                else:
                    t_ret = self.v.emitter.temp_pool.newTemp(typeToTempKind(ret_t))
                    self.v.emitter.emit(Op.CALL, arg1=f_label, arg2=str(n_params), res=t_ret)
                    base_place = t_ret
                    setPlace(suf, t_ret, True)

                if isinstance(recv_place, str) and recv_place.startswith("t"):
                    self.v.emitter.temp_pool.free(recv_place, "*")

                base_type = ret_t
                continue

            # 3.c) Acceso a propiedad: obj.f  -> FIELD_LOAD  |  método enlazado
            if isinstance(suf, CompiscriptParser.PropertyAccessExprContext):
                prop_name = suf.Identifier().getText()

                # Atributo de clase -> FIELD_LOAD
                attr_t = None
                if isinstance(base_type, ClassType):
                    attr_t = self.v.class_handler.getAttributeType(base_type.name, prop_name)

                if attr_t is not None:
                    t_val = self.v.emitter.temp_pool.newTemp(typeToTempKind(attr_t))
                    q = self.v.emitter.emit(Op.FIELD_LOAD, arg1=base_place, res=t_val, label=prop_name)

                    # Anotar offset/owner si está disponible
                    try:
                        off = self.v.class_handler.getFieldOffset(base_type.name, prop_name)
                        if q is not None and off is not None:
                            setattr(q, "_field_offset", off)
                            setattr(q, "_field_owner", base_type.name)
                    except Exception:
                        pass

                    base_place = t_val
                    base_type = attr_t
                    setPlace(suf, base_place, True)
                    continue

                # Método: construir FunctionType enlazado al receptor
                owner = getattr(base_type, "name", None)
                sig = self.v.method_registry.lookupMethod(f"{owner}.{prop_name}") if owner else None
                if sig is None and owner:
                    # Subir por herencia hasta encontrarlo
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
                        setattr(ftype, "_bound_receiver", getattr(base_type, "name", None))
                        setattr(ftype, "_method_name", prop_name)
                        setattr(ftype, "_recv_place", base_place)
                        setattr(ftype, "_decl_owner", owner or getattr(base_type, "name", None))
                        qname = f"{owner}.{prop_name}" if owner else prop_name
                        fsym = self.v.scopeManager.lookup(qname)
                        if fsym is not None and getattr(fsym, "label", None):
                            setattr(ftype, "_label", fsym.label)
                        else:
                            setattr(ftype, "_label", f"f_{owner}_{prop_name}" if owner else f"f_{prop_name}")
                    except Exception:
                        pass

                    base_type = ftype
                    # Mantenemos base_place como receptor para la futura call()
                    setPlace(suf, base_place, isinstance(base_place, str) and base_place.startswith("t"))
                    continue

                # Ni atributo ni método conocido: no emitimos error aquí (semántica lo reporta)
                continue

        # 4) Publicar place final
        setPlace(ctx, base_place, isinstance(base_place, str) and str(base_place).startswith("t"))
        log(f"[lvalues][TAC] exit LHS: type={base_type}, place={base_place}", channel="tac")
        return base_type
