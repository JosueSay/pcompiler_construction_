from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import ArrayType, IntegerType, ErrorType, FunctionType, ClassType, VoidType
from semantic.type_system import isAssignable
from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic, log_function
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

    @log_function
    def __init__(self, v):
        log_semantic("===== [Lvalues.py] Inicio =====")
        self.v = v

    # --------- helpers de place/temporales (coherentes con expressions) ---------
    @log_function
    def setPlace(self, node, place: str, is_temp: bool) -> None:
        log_semantic(f"setPlace: node={node}, place={place}, is_temp={is_temp}")
        try:
            setattr(node, "_place", place)
            setattr(node, "_is_temp", is_temp)
        except Exception:
            log_semantic(f"setPlace: failed to set attributes on node {node}")
            pass

    @log_function
    def getPlace(self, node) -> str | None:
        p = getattr(node, "_place", None)
        log_semantic(f"getPlace: node={node}, place={p}")
        return p

    @log_function
    def isTempNode(self, node) -> bool:
        temp = bool(getattr(node, "_is_temp", False))
        log_semantic(f"isTempNode: node={node}, is_temp={temp}")
        return temp

    @log_function
    def freeIfTemp(self, node) -> None:
        if not self.isTempNode(node):
            log_semantic(f"freeIfTemp: node={node} is not temp, skipping")
            return
        name = self.getPlace(node)
        if not name:
            log_semantic(f"freeIfTemp: node={node} has no place, skipping")
            return
        log_semantic(f"freeIfTemp: freeing temp {name}")
        self.v.emitter.temp_pool.free(name, "*")

    # --------------------------- núcleo ----------------------------
    @log_function
    def visitLeftHandSide(self, ctx: CompiscriptParser.LeftHandSideContext):
        log_semantic(f"[lvalue] enter LHS: '{ctx.getText()}'")

        # Evaluar el receptor base (primaryAtom)
        base_type = self.v.visit(ctx.primaryAtom())
        base_node = ctx.primaryAtom()
        base_place = self.getPlace(base_node) or base_node.getText()
        log_semantic(f"[lvalue] base_type={base_type}, base_place={base_place}")

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
            log_semantic(f"[lvalue] failed to infer literal type for {base_node}")
            pass

        # Recorrer sufijos encadenados
        for suf in ctx.suffixOp():
            log_semantic(f"[lvalue] processing suffix: {suf.getText()} with base_type={base_type}")

            if isinstance(base_type, ErrorType):
                log_semantic("[lvalue] previous error propagated, skipping suffix processing")
                continue

            # --- [a[i]]: IndexExpr -> lectura rvalue encadenada ---
            if isinstance(suf, CompiscriptParser.IndexExprContext):
                log_semantic(f"[lvalue] IndexExpr detected on base_type={base_type}")
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
                                base_type = ErrorType()
                                continue
                    except Exception:
                        log_semantic(f"[lvalue] failed to validate static index {idx_txt}")

                idx_place = getattr(suf.expression(), "_place", suf.expression().getText())
                t = self.v.emitter.temp_pool.newTemp(self.v.exprs.typeToTempKind(base_type.elem_type))
                
                t_len, l_ok = self.v.emitter.emitBoundsCheck(idx_place, base_place)
                
                log_semantic(f"[lvalue] emitting INDEX_LOAD: {base_place}[{idx_place}] -> {t}")
                self.v.emitter.emit(Op.INDEX_LOAD, arg1=base_place, arg2=idx_place, res=t)
                
                self.v.emitter.temp_pool.free(t_len, "*")
                
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
                log_semantic(f"[lvalue] CallExpr detected on base_type={base_type}")
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

                recv_place = None
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

                for e in args_nodes:
                    p, is_tmp = self.v.exprs.deepPlace(e)
                    aplace = p or e.getText()
                    self.v.emitter.emit(Op.PARAM, arg1=aplace)
                    if is_tmp:
                        self.v.emitter.temp_pool.free(aplace, "*")
                    n_params += 1

                clos_place = getattr(base_type, "_closure_place", None)
                if clos_place:
                    log_semantic(f"[lvalue] calling closure at {clos_place}")
                    ret_t = base_type.return_type
                    if isinstance(ret_t, VoidType):
                        self.v.emitter.emit(Op.CALLC, arg1=clos_place, arg2=str(n_params))
                        base_place = ""
                        self.setPlace(suf, "", False)
                        base_type = ret_t
                    else:
                        t = self.v.emitter.temp_pool.newTemp(self.v.exprs.typeToTempKind(ret_t))
                        self.v.emitter.emit(Op.CALLC, arg1=clos_place, arg2=str(n_params), res=t)
                        base_place = t
                        base_type  = ret_t
                        self.setPlace(suf, t, True)

                    if isinstance(clos_place, str) and clos_place.startswith("t"):
                        self.v.emitter.temp_pool.free(clos_place, "*")
                    if recv_place and isinstance(recv_place, str) and recv_place.startswith("t"):
                        self.v.emitter.temp_pool.free(recv_place, "*")
                    continue

                if f_label is None:
                    base_name = getattr(ctx.primaryAtom(), "_place", None) or ctx.primaryAtom().getText()
                    fsym = self.v.scopeManager.lookup(base_name)
                    f_label = getattr(fsym, "label", None) or f"f_{base_name}"

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
                if recv_place and isinstance(recv_place, str) and recv_place.startswith("t"):
                    self.v.emitter.temp_pool.free(recv_place, "*")
                continue

            # --- acceso a propiedad/método ---
            if isinstance(suf, CompiscriptParser.PropertyAccessExprContext):
                prop_name = suf.Identifier().getText()
                log_semantic(f"[lvalue] PropertyAccessExpr detected: {prop_name}")

                if not isinstance(base_type, ClassType):
                    self.v.appendErr(SemanticError(
                        f"Acceso a propiedades en tipo no-objeto '{base_type}'.",
                        line=ctx.start.line, column=ctx.start.column))
                    base_type = ErrorType()
                    continue

                class_name = base_type.name
                attr_t = self.v.class_handler.get_attribute_type(class_name, prop_name)
                if attr_t is not None:
                    t = self.v.emitter.temp_pool.newTemp(self.v.exprs.typeToTempKind(attr_t))
                    log_semantic(f"[lvalue] emitting FIELD_LOAD: {base_place}.{prop_name} -> {t}")
                    q = self.v.emitter.emit(Op.FIELD_LOAD, arg1=base_place, res=t, label=prop_name)
                    try:
                        off = self.v.class_handler.get_field_offset(class_name, prop_name)
                        if q is not None and off is not None:
                            setattr(q, "_field_offset", off)
                            setattr(q, "_field_owner", class_name)
                    except Exception:
                        log_semantic(f"[lvalue] failed to set field metadata for {prop_name}")
                    base_place = t
                    base_type  = attr_t
                    self.setPlace(suf, base_place, True)
                    lit_t = None
                    continue

                # --- método ---
                sig = self.v.method_registry.lookup(f"{class_name}.{prop_name}")
                owner = class_name if sig else None
                if sig is None:
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
                    try:
                        setattr(ftype, "_bound_receiver", class_name)
                        setattr(ftype, "_method_name", prop_name)
                        setattr(ftype, "_recv_place", base_place)
                        setattr(ftype, "_decl_owner", owner or class_name)
                        qname = f"{owner}.{prop_name}" if owner else f"{class_name}.{prop_name}"
                        fsym = self.v.scopeManager.lookup(qname)
                        if fsym is not None and getattr(fsym, "label", None):
                            setattr(ftype, "_label", fsym.label)
                        else:
                            setattr(ftype, "_label", f"f_{owner or class_name}_{prop_name}")
                    except Exception:
                        log_semantic(f"[lvalue] failed to set method metadata for {prop_name}")
                    base_type = ftype
                    self.setPlace(suf, base_place, base_place.startswith("t"))
                    continue

                self.v.appendErr(SemanticError(
                    f"Miembro '{prop_name}' no declarado en clase '{class_name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                base_type = ErrorType()

        self.setPlace(ctx, base_place, isinstance(base_place, str) and base_place.startswith("t"))
        log_semantic(f"[lvalue] exit LHS: base_type={base_type}, base_place={base_place}")
        return base_type
