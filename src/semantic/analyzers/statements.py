from antlr4.tree.Tree import TerminalNode
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.symbol_kinds import SymbolCategory
from semantic.custom_types import NullType, ErrorType, ArrayType, IntegerType, VoidType, ClassType
from semantic.type_system import isAssignable, isReferenceType
from semantic.registry.type_resolver import resolve_annotated_type, validate_known_types
from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic, log_function
from ir.tac import Op


class StatementsAnalyzer:
    """
    Sentencias (declaraciones, asignaciones, bloques, foreach) con:
      - Chequeo semántico completo (como en la versión previa).
      - Emisión TAC donde corresponde (inicializadores y asignaciones).
      - Detección de 'código muerto' coherente con control de flujo.
      - Limpieza de temporales por sentencia.
    """

    @log_function
    def __init__(self, v):
        log_semantic("===== [Statements.py] Inicio =====")
        log_semantic(f"__init__ -> Recibido v={v}")
        self.v = v

    # ----------------------------------
    # Helpers para navegar el parse tree
    # ----------------------------------
    @log_function
    def findDesc(self, node, klass):
        log_semantic(f"findDesc -> node={node}, klass={klass}")
        try:
            for ch in node.getChildren():
                if isinstance(ch, klass):
                    log_semantic(f"findDesc -> encontrado {ch}")
                    return ch
                sub = self.findDesc(ch, klass)
                if sub is not None:
                    return sub
        except Exception as e:
            log_semantic(f"findDesc -> excepción {e}")
            return None
        return None

    @log_function
    def findAllDesc(self, node, klass):
        log_semantic(f"findAllDesc -> node={node}, klass={klass}")
        res = []
        try:
            for ch in node.getChildren():
                if isinstance(ch, klass):
                    res.append(ch)
                else:
                    res.extend(self.findAllDesc(ch, klass))
        except Exception as e:
            log_semantic(f"findAllDesc -> excepción {e}")
            pass
        return res

    @log_function
    def expressionsFromCTX(self, ctx):
        log_semantic(f"expressionsFromCTX -> ctx={ctx}")
        # 1) intento con getRuleContexts (si existe)
        try:
            exprs = ctx.getRuleContexts(CompiscriptParser.ExpressionContext)
            if exprs:
                log_semantic(f"expressionsFromCTX -> exprs encontrados (getRuleContexts)={exprs}")
                return list(exprs)
        except Exception:
            pass

        # 2) intento con ctx.expression() (puede devolver lista o único)
        try:
            raw = ctx.expression()
            if raw is None:
                return []
            if isinstance(raw, (list, tuple)):
                return list(raw)
            return [raw]
        except Exception:
            pass

        # 3) fallback: buscar descendientes que sean ExpressionContext
        try:
            res = []
            for ch in ctx.getChildren():
                if isinstance(ch, CompiscriptParser.ExpressionContext):
                    res.append(ch)
                else:
                    res.extend(self.findAllDesc(ch, CompiscriptParser.ExpressionContext))
            return res
        except Exception:
            return []

    @log_function
    def hasTopLevelAssign(self, expr_ctx) -> bool:
        log_semantic(f"hasTopLevelAssign -> expr_ctx={expr_ctx}")
        # 1) preferente: ¿existe un AssignExpr en este árbol?
        try:
            if self.findDesc(expr_ctx, CompiscriptParser.AssignExprContext) is not None:
                return True
        except Exception:
            pass
        # 2) fallback textual (tu heurística)
        try:
            s = expr_ctx.getText()
        except Exception:
            return False
        if not s:
            return False
        for i, ch in enumerate(s):
            if ch != '=':
                continue
            prev = s[i-1] if i > 0 else ''
            nxt  = s[i+1] if i+1 < len(s) else ''
            if prev not in ('=', '!', '<', '>') and nxt != '=':
                log_semantic("hasTopLevelAssign -> '=' encontrado (fallback)")
                return True
        return False

    @log_function
    def matchSimpleIndexAssign(self, lhs_or_expr_node):
        log_semantic(f"matchSimpleIndexAssign -> lhs_or_expr_node={lhs_or_expr_node}")
        lhs_ctx = self.findDesc(lhs_or_expr_node, CompiscriptParser.LeftHandSideContext)
        if lhs_ctx is None:
            return None

        # Texto del LHS (ej: "a[i]", "this.data[i]")
        try:
            lhs_txt = lhs_ctx.getText()
        except Exception:
            return None

        # Debe verse como VAR[...], sin puntos y sin 'this'
        brk = lhs_txt.find('[')
        if brk <= 0:
            return None
        base_txt = lhs_txt[:brk]

        # Si es 'this' o contiene '.' (p. ej. this.data[i], a.b[i]), NO usar el atajo
        if base_txt == 'this' or '.' in base_txt:
            return None

        # Asegura que realmente hay un IndexExpr
        idx_node = self.findDesc(lhs_ctx, CompiscriptParser.IndexExprContext)
        if idx_node is None:
            return None

        # Base es un identificador simple
        return (base_txt, idx_node)

    @log_function
    def rhsOfAssignExpr(self, expr_ctx):
        log_semantic(f"rhsOfAssignExpr -> expr_ctx={expr_ctx}")

        # 0) Si hay un AssignExpr debajo, su RHS es exprNoAssign()
        try:
            assign = self.findDesc(expr_ctx, CompiscriptParser.AssignExprContext)
            if assign is not None:
                # camino feliz: método del parser
                try:
                    rhs = assign.exprNoAssign()
                    if isinstance(rhs, (list, tuple)):
                        rhs = rhs[-1]
                    if rhs is not None:
                        log_semantic(f"rhsOfAssignExpr -> RHS por AssignExpr.exprNoAssign() {rhs}")
                        return rhs
                except Exception:
                    pass

                # fallback: tomar el primer hijo después de '=' que sea ExprNoAssign / Expression
                try:
                    n = assign.getChildCount()
                    saw_eq = False
                    for i in range(n):
                        ch = assign.getChild(i)
                        if isinstance(ch, TerminalNode) and ch.getText() == '=':
                            saw_eq = True
                            continue
                        if saw_eq and (isinstance(ch, CompiscriptParser.ExprNoAssignContext) or
                                    isinstance(ch, CompiscriptParser.ExpressionContext)):
                            log_semantic(f"rhsOfAssignExpr -> RHS por hijos AssignExpr {ch}")
                            return ch
                except Exception:
                    pass
        except Exception:
            pass

        # a) hijos toplevel (aceptando ExprNoAssign además de Expression)
        try:
            n = expr_ctx.getChildCount()
            kids = [expr_ctx.getChild(i) for i in range(n)]
            saw_eq = False
            for ch in kids:
                if isinstance(ch, TerminalNode) and ch.getText() == '=':
                    saw_eq = True
                    continue
                if saw_eq and (isinstance(ch, CompiscriptParser.ExprNoAssignContext) or
                            isinstance(ch, CompiscriptParser.ExpressionContext)):
                    log_semantic(f"rhsOfAssignExpr -> RHS encontrado (toplevel) {ch}")
                    return ch
        except Exception:
            pass

        # b) última subexpresión (si aplica)
        try:
            raw = expr_ctx.expression()
            exprs = list(raw) if isinstance(raw, (list, tuple)) else ([raw] if raw is not None else [])
            if len(exprs) >= 1:
                log_semantic(f"rhsOfAssignExpr -> fallback por lista/último: len={len(exprs)}")
                return exprs[-1]
        except Exception:
            pass

        # c) último descendiente que sea ExprNoAssign / Expression
        try:
            last = None
            for ch in expr_ctx.getChildren():
                if isinstance(ch, CompiscriptParser.ExprNoAssignContext) or isinstance(ch, CompiscriptParser.ExpressionContext):
                    last = ch
            if last is not None:
                log_semantic(f"rhsOfAssignExpr -> RHS por descendiente final {last}")
                return last
        except Exception:
            pass

        # d) fallback textual: emparejar por texto pero buscando también ExprNoAssign
        try:
            s = expr_ctx.getText() or ""
            if s:
                # localizar '=' de nivel superior
                eq_pos = None
                for i, ch in enumerate(s):
                    if ch != '=':
                        continue
                    prev = s[i-1] if i > 0 else ''
                    nxt  = s[i+1] if i+1 < len(s) else ''
                    if prev not in ('=', '!', '<', '>') and nxt != '=':
                        eq_pos = i
                        break
                if eq_pos is not None and eq_pos+1 < len(s):
                    rhs_txt = s[eq_pos+1:]
                    cands  = self.findAllDesc(expr_ctx, CompiscriptParser.ExpressionContext)
                    cands += self.findAllDesc(expr_ctx, CompiscriptParser.ExprNoAssignContext)
                    exact = [c for c in cands if getattr(c, "getText", lambda: "")() == rhs_txt]
                    if exact:
                        log_semantic(f"rhsOfAssignExpr -> RHS por texto (exact) {exact[-1]}")
                        return exact[-1]
                    suffix = [c for c in cands if getattr(c, "getText", lambda: "")().endswith(rhs_txt)]
                    if suffix:
                        suffix.sort(key=lambda c: len(getattr(c, "getText", lambda: "")()))
                        log_semantic(f"rhsOfAssignExpr -> RHS por texto (suffix) {suffix[0]}")
                        return suffix[0]
        except Exception:
            pass

        log_semantic("rhsOfAssignExpr -> RHS NO encontrado")
        return None

    @log_function
    def typeOfSilent(self, expr_ctx):
        log_semantic(f"typeOfSilent -> expr_ctx={expr_ctx}")
        old = self.v.emitter.flow_terminated
        self.v.emitter.flow_terminated = True
        try:
            t = self.v.visit(expr_ctx)
        finally:
            self.v.emitter.flow_terminated = old
            self.v.emitter.temp_pool.resetPerStatement()
        return t

    @log_function
    def handleSimpleIndexStore(self, base_name, idx_node, rhs_node, ctx_stmt):
        log_semantic(f"handleSimpleIndexStore -> inicio: {base_name}[{idx_node.getText()}] = {rhs_node.getText()}")

        # 0) variable debe existir y no ser const
        sym = self.v.scopeManager.lookup(base_name)
        if sym is None:
            self.v.appendErr(SemanticError(
                f"Uso de variable no declarada: '{base_name}'",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            log_semantic(f"[INDEX_STORE] ERROR: variable no declarada '{base_name}'")
            return
        if getattr(sym, "category", None) == SymbolCategory.CONSTANT:
            self.v.appendErr(SemanticError(
                f"No se puede modificar la constante '{base_name}'.",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            log_semantic(f"[INDEX_STORE] ERROR: intento de modificar constante '{base_name}'")
            return

        arr_t = getattr(sym, "type", None)

        # 1) normaliza la expresión del índice
        try:
            idx_expr = idx_node.expression()
        except Exception:
            idx_expr = None
        if idx_expr is None:
            idx_expr = idx_node

        # 2) visita de tipos (no debe emitir stores todavía)
        idx_t = self.v.visit(idx_expr)
        rhs_t = self.v.visit(rhs_node)

        # 3) validaciones de tipos
        if not isinstance(arr_t, ArrayType):
            self.v.appendErr(SemanticError(
                f"Asig. indexada sobre un no-arreglo: '{arr_t}'.",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            log_semantic(f"[INDEX_STORE] ERROR: no es un arreglo '{arr_t}'")
            return

        if not isinstance(idx_t, IntegerType):
            self.v.appendErr(SemanticError(
                f"Índice no entero en asig. de arreglo: se encontró {idx_t}.",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            log_semantic(f"[INDEX_STORE] ERROR: índice no entero '{idx_t}'")
            return

        elem_t = arr_t.elem_type
        if rhs_t is None or isinstance(rhs_t, ErrorType) or not isAssignable(elem_t, rhs_t):
            self.v.appendErr(SemanticError(
                f"Asignación incompatible: no se puede asignar {rhs_t} a {elem_t} en {base_name}[i].",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            log_semantic(f"[INDEX_STORE] ERROR: tipos incompatibles rhs:{rhs_t} elem:{elem_t}")
            return

        # 4) obtener places y emitir INDEX_STORE
        p_idx, it_idx = self.v.exprs.deepPlace(idx_expr)
        idx_place = p_idx or idx_expr.getText()
        p_rhs, it_rhs = self.v.exprs.deepPlace(rhs_node)
        rhs_place = p_rhs or rhs_node.getText()
        log_semantic(f"[INDEX_STORE] tipos -> arr:{arr_t}, idx:{idx_t}, rhs:{rhs_t}")
        log_semantic(f"[INDEX_STORE] deepPlace -> idx='{idx_place}', rhs='{rhs_place}'")
        
        
        t_len, l_ok = self.v.emitter.emitBoundsCheck(idx_place, base_name)

        self.v.emitter.emit(Op.INDEX_STORE, arg1=base_name, res=rhs_place, label=idx_place)
        log_semantic(f"[INDEX_STORE] emitido: {base_name}[{idx_place}] = {rhs_place}")
        
        self.v.emitter.temp_pool.free(t_len, "*")

        # 5) liberar temporales usados en idx/rhs si aplica
        if it_idx:
            self.v.emitter.temp_pool.free(idx_place, "*")
        if it_rhs:
            self.v.emitter.temp_pool.free(rhs_place, "*")
            
    @log_function
    def matchPropertyIndexAssign(self, lhs_or_expr_node):
        """
        Detecta LHS de la forma  OBJ.PROP[ idx ]  (p. ej. this.data[i], b.buf[j])
        Retorna: (obj_txt, prop_name, idx_node)  o None
        """
        log_semantic(f"matchPropertyIndexAssign -> lhs_or_expr_node={lhs_or_expr_node}")

        lhs_ctx = self.findDesc(lhs_or_expr_node, CompiscriptParser.LeftHandSideContext)
        if lhs_ctx is None:
            return None

        try:
            lhs_txt = lhs_ctx.getText()  # ej: "this.data[i]"
        except Exception:
            return None

        brk = lhs_txt.find('[')
        if brk <= 0:
            return None
        base_txt = lhs_txt[:brk]        # "this.data" | "obj.prop" | "a.b.c" (rechazaremos anidados)
        if '.' not in base_txt:
            return None  # esto lo maneja matchSimpleIndexAssign

        # Aceptamos exactamente OBJ.PROP (un solo '.'); si hay más niveles, que lo maneje el camino general
        parts = base_txt.split('.')
        if len(parts) < 2:
            return None  # se requieren al menos 2 partes: obj + alguna propiedad

        obj_txt = parts[0]              # "a" | "this"
        prop_chain = parts[1:]          # ["b", "c"]

        idx_node = self.findDesc(lhs_ctx, CompiscriptParser.IndexExprContext)
        if idx_node is None:
            return None

        return (obj_txt, prop_chain, idx_node)

    @log_function
    def handleChainedPropertyIndexStore(self, obj_txt, prop_chain, idx_node, rhs_node, ctx_stmt):
        """
        Genera:
            t1 = FIELD_LOAD obj.p1
            t2 = FIELD_LOAD t1.p2
            ...
            t_arr = FIELD_LOAD t_{n-1}.pn         ; debe ser ArrayType
            ; bounds check
            t_len = len t_arr
            if idx<0 goto L_oob
            if idx>=t_len goto L_oob
            goto L_ok
          L_oob: call __bounds_error, 0
          L_ok:  t_arr[idx] = rhs
        Libera temporales usados (idx, rhs, t_len y t_arr).
        """

        log_semantic(f"[CHAIN_INDEX_STORE] inicio: {obj_txt}.{'.'.join(prop_chain)}[{idx_node.getText()}] = {rhs_node.getText()}")

        # 1) Resolver tipo/place del objeto base ('this' o identificador)
        if obj_txt == 'this':
            obj_place = 'this'
            if not self.v.class_stack:
                self.v.appendErr(SemanticError("Uso de 'this' fuera de una clase.",
                                            line=ctx_stmt.start.line, column=ctx_stmt.start.column))
                return
            base_type = ClassType(self.v.class_stack[-1])
        else:
            sym = self.v.scopeManager.lookup(obj_txt)
            if sym is None:
                self.v.appendErr(SemanticError(f"Uso de variable no declarada: '{obj_txt}'.",
                                            line=ctx_stmt.start.line, column=ctx_stmt.start.column))
                return

            # ✅ comprobación robusta de constante
            cat = getattr(sym, "category", None)
            if cat == SymbolCategory.CONSTANT or getattr(cat, "name", None) == "CONSTANT" or cat == "CONSTANT":
                self.v.appendErr(SemanticError(f"No se puede modificar la constante '{obj_txt}'.",
                                            line=ctx_stmt.start.line, column=ctx_stmt.start.column))
                return

            obj_place = obj_txt
            base_type = getattr(sym, "type", None)


        # 2) Recorrer la cadena de propiedades haciendo FIELD_LOAD
        curr_place = obj_place
        curr_type  = base_type
        prev_temp_to_free = None

        for k, prop_name in enumerate(prop_chain):
            if not isinstance(curr_type, ClassType):
                self.v.appendErr(SemanticError(
                    f"Acceso a propiedad '{prop_name}' sobre tipo no-objeto: {curr_type}.",
                    line=ctx_stmt.start.line, column=ctx_stmt.start.column))
                # liberar temp pendiente
                if prev_temp_to_free:
                    self.v.emitter.temp_pool.free(prev_temp_to_free, "*")
                return

            attr_t = self.v.class_handler.get_attribute_type(curr_type.name, prop_name)
            if attr_t is None:
                self.v.appendErr(SemanticError(
                    f"La clase {curr_type} no tiene un atributo '{prop_name}'.",
                    line=ctx_stmt.start.line, column=ctx_stmt.start.column))
                if prev_temp_to_free:
                    self.v.emitter.temp_pool.free(prev_temp_to_free, "*")
                return

            t_next = self.v.exprs.newTempFor(attr_t)
            qfld = self.v.emitter.emit(Op.FIELD_LOAD, arg1=curr_place, res=t_next, label=prop_name)
            log_semantic(f"[CHAIN_INDEX_STORE] FIELD_LOAD: {curr_place}.{prop_name} -> {t_next}")

            # Metadatos opcionales (offset/owner)
            try:
                off = self.v.class_handler.get_field_offset(curr_type.name, prop_name)
                if qfld is not None and off is not None:
                    setattr(qfld, "_field_offset", off)
                    setattr(qfld, "_field_owner", curr_type.name)
            except Exception:
                pass

            # liberar el temp previo si era un temp intermedio
            if prev_temp_to_free and prev_temp_to_free != obj_place:
                self.v.emitter.temp_pool.free(prev_temp_to_free, "*")

            prev_temp_to_free = t_next
            curr_place = t_next
            curr_type  = attr_t

        # 3) Al final de la cadena, esperamos un ArrayType
        if not isinstance(curr_type, ArrayType):
            self.v.appendErr(SemanticError(
                f"Índice aplicado sobre un miembro que no es arreglo: {curr_type}.",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            if prev_temp_to_free:
                self.v.emitter.temp_pool.free(prev_temp_to_free, "*")
            return

        arr_place = curr_place
        arr_type  = curr_type

        # 4) Tipos de idx y rhs (sin emitir aún)
        try:
            idx_expr = idx_node.expression()
        except Exception:
            idx_expr = idx_node

        idx_t = self.v.visit(idx_expr)
        rhs_t = self.v.visit(rhs_node)
        if not isinstance(idx_t, IntegerType):
            self.v.appendErr(SemanticError(
                f"Índice no entero en asig. de arreglo: se encontró {idx_t}.",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            self.v.emitter.temp_pool.free(arr_place, "*")
            return

        elem_t = arr_type.elem_type
        if rhs_t is None or isinstance(rhs_t, ErrorType) or not isAssignable(elem_t, rhs_t):
            self.v.appendErr(SemanticError(
                f"Asignación incompatible: no se puede asignar {rhs_t} a {elem_t}.",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            self.v.emitter.temp_pool.free(arr_place, "*")
            return

        # 5) deepPlace para idx y rhs
        p_idx, it_idx = self.v.exprs.deepPlace(idx_expr)
        idx_place = p_idx or idx_expr.getText()
        p_rhs, it_rhs = self.v.exprs.deepPlace(rhs_node)
        rhs_place = p_rhs or rhs_node.getText()

        # 6) Bounds check + store
        t_len, _ = self.v.emitter.emitBoundsCheck(idx_place, arr_place)
        self.v.emitter.emit(Op.INDEX_STORE, arg1=arr_place, res=rhs_place, label=idx_place)
        log_semantic(f"[CHAIN_INDEX_STORE] emitido: {arr_place}[{idx_place}] = {rhs_place}")

        # 7) Liberaciones
        self.v.emitter.temp_pool.free(t_len, "*")
        if it_idx:
            self.v.emitter.temp_pool.free(idx_place, "*")
        if it_rhs:
            self.v.emitter.temp_pool.free(rhs_place, "*")
        self.v.emitter.temp_pool.free(arr_place, "*")


    @log_function
    def handlePropertyIndexStore(self, obj_txt, prop_name, idx_node, rhs_node, ctx_stmt):
        """
        Genera: t_arr = (FIELD_LOAD obj.prop); INDEX_STORE t_arr[idx] = rhs
        Tipado y chequeos siguiendo tu estilo.
        """
        log_semantic(f"handlePropertyIndexStore -> inicio: {obj_txt}.{prop_name}[{idx_node.getText()}] = {rhs_node.getText()}")

        # 1) Resolver tipo/‘place’ del objeto (solo soportamos 'this' o un identificador de clase)
        if obj_txt == 'this':
            obj_place = 'this'
            # tipo de 'this' es la clase actual
            if not self.v.class_stack:
                self.v.appendErr(SemanticError(f"Uso de 'this' fuera de una clase.", line=ctx_stmt.start.line, column=ctx_stmt.start.column))
                return
            obj_type = self.v.class_stack[-1]  # nombre de clase
            obj_type = ClassType(obj_type)
        else:
            sym = self.v.scopeManager.lookup(obj_txt)
            if sym is None:
                self.v.appendErr(SemanticError(
                    f"Uso de variable no declarada: '{obj_txt}'",
                    line=ctx_stmt.start.line, column=ctx_stmt.start.column))
                return
            if getattr(sym, "category", None) == SymbolCategory.CONSTANT:
                self.v.appendErr(SemanticError(
                    f"No se puede modificar la constante '{obj_txt}'.",
                    line=ctx_stmt.start.line, column=ctx_stmt.start.column))
                return
            obj_place = obj_txt
            obj_type = getattr(sym, "type", None)

            # si no es objeto, error claro
            if not isinstance(obj_type, ClassType):
                self.v.appendErr(SemanticError(
                    f"Asig. indexada a propiedad en no-objeto: '{obj_type}'.",
                    line=ctx_stmt.start.line, column=ctx_stmt.start.column))
                return


        # 2) Verificar que prop exista y sea arreglo
        try:
            field_t = self.v.class_handler.get_attribute_type(obj_type.name, prop_name)
        except Exception:
            field_t = None
        if field_t is None:
            self.v.appendErr(SemanticError(
                f"La clase {obj_type} no tiene un atributo '{prop_name}'.",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            return
        if not isinstance(field_t, ArrayType):
            self.v.appendErr(SemanticError(
                f"Asig. indexada sobre un no-arreglo: '{obj_txt}.{prop_name}' es {field_t}.",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            return

        # 3) Normalizar/visitar índice y rhs (sin emitir stores todavía)
        try:
            idx_expr = idx_node.expression()
        except Exception:
            idx_expr = idx_node
        idx_t = self.v.visit(idx_expr)
        rhs_t = self.v.visit(rhs_node)

        if not isinstance(idx_t, IntegerType):
            self.v.appendErr(SemanticError(
                f"Índice no entero en asig. de arreglo: se encontró {idx_t}.",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            return
        elem_t = field_t.elem_type
        if rhs_t is None or isinstance(rhs_t, ErrorType) or not isAssignable(elem_t, rhs_t):
            self.v.appendErr(SemanticError(
                f"Asignación incompatible: no se puede asignar {rhs_t} a {elem_t} en {obj_txt}.{prop_name}[i].",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            return

        # 4) FIELD_LOAD obj.prop -> t_arr
        t_arr = self.v.exprs.newTempFor(field_t)
        qfld = self.v.emitter.emit(Op.FIELD_LOAD, arg1=obj_place, res=t_arr, label=prop_name)
        log_semantic(f"[PROP_INDEX_STORE] FIELD_LOAD: {obj_txt}.{prop_name} -> {t_arr}")
        
        try:
            off = self.v.class_handler.get_field_offset(obj_type.name, prop_name)
            if qfld is not None and off is not None:
                setattr(qfld, "_field_offset", off)
                setattr(qfld, "_field_owner", obj_type.name)
        except Exception:
            pass

        # 5) deepPlace de idx y rhs
        p_idx, it_idx = self.v.exprs.deepPlace(idx_expr)
        idx_place = p_idx or idx_expr.getText()
        p_rhs, it_rhs = self.v.exprs.deepPlace(rhs_node)
        rhs_place = p_rhs or rhs_node.getText()
        log_semantic(f"[PROP_INDEX_STORE] tipos -> arr:{field_t}, idx:{idx_t}, rhs:{rhs_t}")
        log_semantic(f"[PROP_INDEX_STORE] deepPlace -> idx='{idx_place}', rhs='{rhs_place}'")

        t_len, l_ok = self.v.emitter.emitBoundsCheck(idx_place, t_arr)

        # 6) INDEX_STORE t_arr[idx] = rhs
        self.v.emitter.emit(Op.INDEX_STORE, arg1=t_arr, res=rhs_place, label=idx_place)
        log_semantic(f"[PROP_INDEX_STORE] emitido: {t_arr}[{idx_place}] = {rhs_place}")
        
        self.v.emitter.temp_pool.free(t_len, "*")

        # 7) liberar temporales
        if it_idx:
            self.v.emitter.temp_pool.free(idx_place, "*")
        if it_rhs:
            self.v.emitter.temp_pool.free(rhs_place, "*")

        # liberar el temp del arreglo cargado
        self.v.emitter.temp_pool.free(t_arr, "*")
            

    # ------------------------------------------------------------------
    # Sentencia de expresión
    # ------------------------------------------------------------------
    @log_function
    def visitExpressionStatement(self, ctx):
        log_semantic(f"visitExpressionStatement -> ctx={ctx}")
        
        expr = ctx.expression()
        txt = getattr(expr, "getText", lambda: "")()
        log_semantic(f"[stmt] visitExpressionStatement: '{txt}'")

        # Detectar si la expresión es un assignment
        is_assign = self.hasTopLevelAssign(expr) or (
            '=' in txt and not any(op in txt for op in ('==','!=','<=','>='))
        )
        log_semantic(f"[stmt] detectado assignment={is_assign}")

        if is_assign:
            # 1) v[i] = rhs
            m = self.matchSimpleIndexAssign(expr)
            if m is not None:
                base_name, idx_node = m
                rhs_node = self.rhsOfAssignExpr(expr)
                if rhs_node is not None:
                    self.handleSimpleIndexStore(base_name, idx_node, rhs_node, ctx)
                    self.v.emitter.temp_pool.resetPerStatement()
                    return None

            # 2) obj.prop[i] = rhs  o cadenas largas obj.p1.p2...[i] = rhs
            mp = self.matchPropertyIndexAssign(expr)
            if mp is not None:
                obj_txt, prop_chain, idx_node = mp
                rhs_node = self.rhsOfAssignExpr(expr)
                if rhs_node is not None:
                    if len(prop_chain) == 1:
                        # caso antiguo (una sola propiedad)
                        self.handlePropertyIndexStore(obj_txt, prop_chain[0], idx_node, rhs_node, ctx)
                    else:
                        # cadenas largas
                        self.handleChainedPropertyIndexStore(obj_txt, prop_chain, idx_node, rhs_node, ctx)
                    self.v.emitter.temp_pool.resetPerStatement()
                    return None

            # 3) fallback para cualquier otra asignación
            self.visitAssignment(expr)
            self.v.emitter.temp_pool.resetPerStatement()
            return None

        # Si no es assignment, simplemente visitamos la expresión
        t = self.v.visit(expr)
        log_semantic(f"[stmt] visitExpressionStatement: tipo expr='{t}'")
        self.v.emitter.temp_pool.resetPerStatement()
        return t



    # ------------------------------------------------------------------
    # Bloques (con detección de código muerto)
    # ------------------------------------------------------------------
    @log_function
    def visitBlock(self, ctx):
        log_semantic(f"visitBlock -> ctx={ctx}")

        is_fn_body = (getattr(self.v, "_fn_body_block_ctx", None) is ctx)
        log_semantic(f"[block] es cuerpo de función: {is_fn_body}")

        if not is_fn_body:
            self.v.scopeManager.enterScope()
            log_semantic("[scope] scope entrado")

        terminated_in_block = False
        terminator_reason = None

        for st in ctx.statement():
            if terminated_in_block:
                try:
                    line = st.start.line
                    col = st.start.column
                except Exception:
                    line = None
                    col = None

                self.v.appendErr(SemanticError(
                    f"Código inalcanzable: el flujo terminó por '{terminator_reason}' antes de esta sentencia.",
                    line=line, column=col, error_type="DeadCode"))
                log_semantic(f"[deadcode] línea={line}, columna={col}, razón='{terminator_reason}'")

                # activar barrera de emisión en este tramo muerto
                self.v.emitter.markFlowTerminated()
                log_semantic("[emitter] flujo marcado como terminado (dead code)")

                self.v.visit(st)
                continue

            # Reset de flags de terminación por sentencia
            self.v.stmt_just_terminated = None
            self.v.stmt_just_terminator_node = None

            # Visitar sentencia
            log_semantic(f"[stmt] visitando sentencia: {st}")
            self.v.visit(st)

            # ¿Terminó el flujo?
            if self.v.stmt_just_terminated:
                terminated_in_block = True
                terminator_reason = self.v.stmt_just_terminated
                log_semantic(f"[block] flujo terminado por: {terminator_reason}")

        if not is_fn_body:
            size = self.v.scopeManager.exitScope()
            log_semantic(f"[scope] bloque cerrado; frame_size={size} bytes")

        log_semantic(f"[block] salida visitBlock -> terminated={terminated_in_block}, reason={terminator_reason}")
        return {"terminated": terminated_in_block, "reason": terminator_reason}


    # ------------------------------------------------------------------
    # Declaraciones: let / const (con emisión TAC para inicializadores)
    # ------------------------------------------------------------------
    @log_function
    def visitVariableDeclaration(self, ctx):
        name = ctx.Identifier().getText()
        ann = ctx.typeAnnotation()
        init = ctx.initializer()
        log_semantic(f"[var.decl] visitVariableDeclaration -> name='{name}', typeAnn={ann}, init={init}")

        if ann is None:
            self.v.appendErr(SemanticError(
                f"La variable '{name}' debe declarar un tipo (no se permite inferencia).",
                line=ctx.start.line, column=ctx.start.column))
            log_semantic(f"[var.decl] ERROR: tipo no declarado")
            self.v.emitter.temp_pool.resetPerStatement()
            return

        declared_type = resolve_annotated_type(ann)
        log_semantic(f"[var.decl] tipo declarado: {declared_type}")

        if not validate_known_types(declared_type, self.v.known_classes, ctx, f"variable '{name}'", self.v.errors):
            log_semantic(f"[var.decl] ERROR: tipo desconocido o inválido")
            self.v.emitter.temp_pool.resetPerStatement()
            return

        if isinstance(declared_type, VoidType):
            self.v.appendErr(SemanticError(
                f"La variable '{name}' no puede ser de tipo void.",
                line=ctx.start.line, column=ctx.start.column))
            log_semantic(f"[var.decl] ERROR: tipo void no permitido")
            self.v.emitter.temp_pool.resetPerStatement()
            return

        initialized = False
        init_value_type = None
        init_note = None

        # Sin inicializador
        if not init:
            if isReferenceType(declared_type):
                initialized = True
                init_value_type = NullType()
                init_note = "default-null"
            else:
                initialized = False
                init_value_type = None
                init_note = "uninitialized"
            log_semantic(f"[var.decl] inicialización implícita -> {init_note}")
        else:
            # Con inicializador
            rhs_type = self.v.visit(init.expression())
            log_semantic(f"[var.decl] RHS type -> {rhs_type}")

            if isinstance(rhs_type, ErrorType) or rhs_type is None:
                log_semantic(f"[var.decl] ERROR: inicializador inválido")
                if self.v.class_stack:
                    current_class = self.v.class_stack[-1]
                    try:
                        self.v.scopeManager.addSymbol(
                            name, declared_type, category=SymbolCategory.VARIABLE,
                            initialized=False, init_value_type=None, init_note="init-error"
                        )
                    except Exception:
                        pass
                    try:
                        already = self.v.class_handler.get_attribute_type(current_class, name)
                    except Exception:
                        already = None
                    if already is None:
                        self.v.class_handler.add_attribute(current_class, name, declared_type)

                self.v.emitter.temp_pool.resetPerStatement()
                return

            if not isAssignable(declared_type, rhs_type):
                self.v.appendErr(SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_type} a {declared_type} en '{name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                log_semantic(f"[var.decl] ERROR: tipos incompatibles")
                if self.v.class_stack:
                    current_class = self.v.class_stack[-1]
                    try:
                        self.v.scopeManager.addSymbol(
                            name, declared_type, category=SymbolCategory.VARIABLE,
                            initialized=False, init_value_type=None, init_note="init-error"
                        )
                    except Exception:
                        pass
                    try:
                        already = self.v.class_handler.get_attribute_type(current_class, name)
                    except Exception:
                        already = None
                    if already is None:
                        self.v.class_handler.add_attribute(current_class, name, declared_type)

                self.v.emitter.temp_pool.resetPerStatement()
                return

            initialized = True
            init_value_type = rhs_type
            init_note = "explicit"
            log_semantic(f"[var.decl] inicialización explícita -> {rhs_type}")

        # Declarar símbolo
        try:
            sym = self.v.scopeManager.addSymbol(
                name, declared_type, category=SymbolCategory.VARIABLE,
                initialized=initialized, init_value_type=init_value_type, init_note=init_note
            )
            log_semantic(f"[var.decl] Variable declarada: {name}, tipo={declared_type}, initialized={initialized}, note={init_note}")
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))
            log_semantic(f"[var.decl] ERROR al declarar variable: {e}")
            self.v.emitter.temp_pool.resetPerStatement()
            return

        # Registrar atributo de clase (si procede)
        if self.v.class_stack:
            current_class = self.v.class_stack[-1]
            try:
                already = self.v.class_handler.get_attribute_type(current_class, name)
            except Exception:
                already = None
            if already is None:
                self.v.class_handler.add_attribute(current_class, name, declared_type)
                log_semantic(f"[class.attr] {current_class}.{name}: {declared_type}")


        # TAC del inicializador
        if init is not None:
            p, _ = self.v.exprs.deepPlace(init.expression())
            rhs_place = p or init.expression().getText()
            self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=name)
            log_semantic(f"[TAC] emitido: {name} = {rhs_place}")

        # Limpiar temporales por sentencia
        self.v.emitter.temp_pool.resetPerStatement()

    @log_function
    def visitConstantDeclaration(self, ctx):
        name = ctx.Identifier().getText() if ctx.Identifier() else "<unnamed-const>"
        ann = ctx.typeAnnotation()
        expr_ctx = ctx.expression()
        log_semantic(f"[const.decl] visitConstantDeclaration -> name='{name}', typeAnn={ann}, expr={expr_ctx}")

        if ann is None:
            self.v.appendErr(SemanticError(
                f"La constante '{name}' debe declarar un tipo.",
                line=ctx.start.line, column=ctx.start.column))
            log_semantic(f"[const.decl] ERROR: tipo no declarado")
            self.v.emitter.temp_pool.resetPerStatement()
            return

        declared_type = resolve_annotated_type(ann)
        log_semantic(f"[const.decl] tipo declarado: {declared_type}")

        if not validate_known_types(declared_type, self.v.known_classes, ctx, f"constante '{name}'", self.v.errors):
            log_semantic(f"[const.decl] ERROR: tipo desconocido o inválido")
            self.v.emitter.temp_pool.resetPerStatement()
            return

        if isinstance(declared_type, VoidType):
            self.v.appendErr(SemanticError(
                f"La constante '{name}' no puede ser de tipo void.",
                line=ctx.start.line, column=ctx.start.column))
            log_semantic(f"[const.decl] ERROR: tipo void no permitido")
            self.v.emitter.temp_pool.resetPerStatement()
            return

        if expr_ctx is None:
            self.v.appendErr(SemanticError(
                f"Constante '{name}' sin inicializar (se requiere '= <expresión>').",
                line=ctx.start.line, column=ctx.start.column))
            log_semantic(f"[const.decl] ERROR: inicializador faltante")
            self.v.emitter.temp_pool.resetPerStatement()
            return

        rhs_type = self.v.visit(expr_ctx)
        log_semantic(f"[const.decl] RHS type -> {rhs_type}")

        if isinstance(rhs_type, ErrorType) or rhs_type is None:
            log_semantic(f"[const.decl] ERROR: inicializador inválido")
            try:
                self.v.scopeManager.addSymbol(name, declared_type, category=SymbolCategory.CONSTANT)
            except Exception:
                pass
            if self.v.class_stack:
                current_class = self.v.class_stack[-1]
                try:
                    already = self.v.class_handler.get_attribute_type(current_class, name)
                except Exception:
                    already = None
                if already is None:
                    self.v.class_handler.add_attribute(current_class, name, declared_type)

            self.v.emitter.temp_pool.resetPerStatement()
            return

        if not isAssignable(declared_type, rhs_type):
            self.v.appendErr(SemanticError(
                f"Asignación incompatible: no se puede asignar {rhs_type} a {declared_type} en constante '{name}'.",
                line=ctx.start.line, column=ctx.start.column))
            log_semantic(f"[const.decl] ERROR: tipos incompatibles")
            self.v.emitter.temp_pool.resetPerStatement()
            return

        # Declarar símbolo
        try:
            sym = self.v.scopeManager.addSymbol(name, declared_type, category=SymbolCategory.CONSTANT)
            log_semantic(f"[const.decl] Constante declarada: {name}, tipo={declared_type}, tamaño={sym.width} bytes")
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))
            log_semantic(f"[const.decl] ERROR al declarar constante: {e}")
            self.v.emitter.temp_pool.resetPerStatement()
            return

        # Registrar atributo de clase (si procede)
        if self.v.class_stack:
            current_class = self.v.class_stack[-1]
            try:
                already = self.v.class_handler.get_attribute_type(current_class, name)
            except Exception:
                already = None
            if already is None:
                self.v.class_handler.add_attribute(current_class, name, declared_type)
                log_semantic(f"[class.attr] {current_class}.{name}: {declared_type}")


        # TAC del inicializador
        p, _ = self.v.exprs.deepPlace(expr_ctx)
        rhs_place = p or expr_ctx.getText()
        self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=name)
        log_semantic(f"[TAC] emitido: {name} = {rhs_place}")

        # Limpiar temporales por sentencia
        self.v.emitter.temp_pool.resetPerStatement()


    # ------------------------------------------------------------------
    # Asignaciones: var = expr  |  obj.prop = expr
    # ------------------------------------------------------------------
    @log_function
    def visitAssignment(self, ctx):
        """
        Soporta:
        1) Identifier '=' expression ';'
        2) expression '.' Identifier '=' expression ';'   (asignación a propiedad)
        3) Indexación: arr[i] = expr
        """
        # Detectar tipo de ctx: puede venir de fallback con ExpressionContext
        is_expr_ctx = isinstance(ctx, CompiscriptParser.ExpressionContext)
        exprs = self.expressionsFromCTX(ctx)
        log_semantic(f"[assign] visitAssignment: ctx_type={type(ctx).__name__}, n_exprs={len(exprs)}, texto='{ctx.getText()}'")
        n = len(exprs)

        # --- Caso especial cuando el fallback nos pasa ExpressionContext ---
        if is_expr_ctx:
            # Prioridad 1: indexación simple  v[i] = expr
            if n == 2:
                m = self.matchSimpleIndexAssign(exprs[0])
                if m is not None:
                    base_name, idx_node = m
                    rhs_node = exprs[1]
                    # Validaciones y emisión (reusa la lógica de store simple)
                    self.handleSimpleIndexStore(base_name, idx_node, rhs_node, ctx)
                    self.v.emitter.temp_pool.resetPerStatement()
                    return

                # Prioridad 2: identificador simple  id = expr
                name = None
                lhs_ctx = self.findDesc(exprs[0], CompiscriptParser.LeftHandSideContext)
                if lhs_ctx is not None:
                    has_suffix = False
                    try:
                        sufs = lhs_ctx.suffixOp()
                        has_suffix = (sufs is not None) and (len(sufs) > 0)
                    except Exception:
                        pass
                    if not has_suffix:
                        # 1) intento clásico
                        try:
                            name = lhs_ctx.primaryAtom().getText()
                        except Exception:
                            name = None
                        # 2) buscar un IdentifierExpr “pelado” como respaldo
                        if not name:
                            try:
                                ident = self.findDesc(lhs_ctx, CompiscriptParser.IdentifierExprContext)
                                if ident is not None:
                                    name = ident.getText()
                            except Exception:
                                pass

                if name:
                    sym = self.v.scopeManager.lookup(name)
                    if sym is None:
                        self.v.appendErr(SemanticError(
                            f"Uso de variable no declarada: '{name}'",
                            line=ctx.start.line, column=ctx.start.column))
                        log_semantic(f"[assign] ERROR: variable no declarada '{name}'")
                        self.v.emitter.temp_pool.resetPerStatement()
                        return
                    if sym.category == SymbolCategory.CONSTANT:
                        self.v.appendErr(SemanticError(
                            f"No se puede modificar la constante '{name}'.",
                            line=ctx.start.line, column=ctx.start.column))
                        log_semantic(f"[assign] ERROR: intento de modificar constante '{name}'")
                        self.v.emitter.temp_pool.resetPerStatement()
                        return

                    rhs_type = self.v.visit(exprs[1])
                    log_semantic(f"[assign] RHS type -> {rhs_type}")

                    if rhs_type is None or isinstance(rhs_type, ErrorType):
                        self.v.emitter.temp_pool.resetPerStatement()
                        return
                    if not isAssignable(sym.type, rhs_type):
                        self.v.appendErr(SemanticError(
                            f"Asignación incompatible: no se puede asignar {rhs_type} a {sym.type} en '{name}'.",
                            line=ctx.start.line, column=ctx.start.column))
                        log_semantic(f"[assign] ERROR: tipos incompatibles para '{name}'")
                        self.v.emitter.temp_pool.resetPerStatement()
                        return

                    p, _ = self.v.exprs.deepPlace(exprs[1])
                    rhs_place = p or exprs[1].getText()
                    self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=name)
                    log_semantic(f"[TAC] emitido: {name} = {rhs_place}")
                    self.v.emitter.temp_pool.resetPerStatement()
                    return

            # Si llegamos aquí, no reconocimos patrón en ExpressionContext
            log_semantic("[assign] ExpressionContext sin patrón reconocido (no index, no ident simple); nada emitido")
            self.v.emitter.temp_pool.resetPerStatement()
            return

        # --- A partir de aquí: comportamiento original con AssignmentContext ---

        # (1) variable simple
        if n == 1 and ctx.Identifier() is not None:
            name = ctx.Identifier().getText()
            sym = self.v.scopeManager.lookup(name)
            if sym is None:
                self.v.appendErr(SemanticError(
                    f"Uso de variable no declarada: '{name}'",
                    line=ctx.start.line, column=ctx.start.column))
                log_semantic(f"[assign] ERROR: variable no declarada '{name}'")
                self.v.emitter.temp_pool.resetPerStatement()
                return
            if sym.category == SymbolCategory.CONSTANT:
                self.v.appendErr(SemanticError(
                    f"No se puede modificar la constante '{name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                log_semantic(f"[assign] ERROR: intento de modificar constante '{name}'")
                self.v.emitter.temp_pool.resetPerStatement()
                return

            rhs_type = self.v.visit(exprs[0])
            log_semantic(f"[assign] RHS type -> {rhs_type}")

            if rhs_type is None or isinstance(rhs_type, ErrorType):
                self.v.emitter.temp_pool.resetPerStatement()
                return
            if not isAssignable(sym.type, rhs_type):
                self.v.appendErr(SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_type} a {sym.type} en '{name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                log_semantic(f"[assign] ERROR: tipos incompatibles para '{name}'")
                self.v.emitter.temp_pool.resetPerStatement()
                return

            p, _ = self.v.exprs.deepPlace(exprs[0])
            rhs_place = p or exprs[0].getText()
            self.v.emitter.emit(Op.ASSIGN, arg1=rhs_place, res=name)
            log_semantic(f"[TAC] emitido: {name} = {rhs_place}")
            self.v.emitter.temp_pool.resetPerStatement()
            return

        # (0) escritura indexada simple: v[i] = expr
        if n == 2:
            m = self.matchSimpleIndexAssign(exprs[0])
            if m is not None:
                base_name, idx_node = m
                rhs_node = exprs[1]

                sym = self.v.scopeManager.lookup(base_name)
                if sym is None:
                    self.v.appendErr(SemanticError(
                        f"Uso de variable no declarada: '{base_name}'",
                        line=ctx.start.line, column=ctx.start.column))
                    log_semantic(f"[INDEX_STORE] ERROR: variable no declarada '{base_name}'")
                    self.v.emitter.temp_pool.resetPerStatement()
                    return

                arr_t = sym.type
                if not isinstance(arr_t, ArrayType):
                    self.v.appendErr(SemanticError(
                        f"Asig. indexada sobre un no-arreglo: '{arr_t}'.",
                        line=ctx.start.line, column=ctx.start.column))
                    log_semantic(f"[INDEX_STORE] ERROR: no es un arreglo '{arr_t}'")
                    self.v.emitter.temp_pool.resetPerStatement()
                    return

                # Usar la expresión interna del índice
                try:
                    idx_expr = idx_node.expression()
                except Exception:
                    idx_expr = None
                if idx_expr is None:
                    idx_expr = idx_node

                idx_t = self.v.visit(idx_expr)
                rhs_t = self.v.visit(rhs_node)
                elem_t = arr_t.elem_type

                if not isinstance(idx_t, IntegerType):
                    self.v.appendErr(SemanticError(
                        f"Índice no entero en asig. de arreglo: se encontró {idx_t}.",
                        line=ctx.start.line, column=ctx.start.column))
                    self.v.emitter.temp_pool.resetPerStatement()
                    return

                if rhs_t is None or isinstance(rhs_t, ErrorType) or not isAssignable(elem_t, rhs_t):
                    self.v.appendErr(SemanticError(
                        f"Asignación incompatible: no se puede asignar {rhs_t} a {elem_t} en {base_name}[i].",
                        line=ctx.start.line, column=ctx.start.column))
                    self.v.emitter.temp_pool.resetPerStatement()
                    return

                p_idx, it_idx = self.v.exprs.deepPlace(idx_expr)
                idx_place = p_idx or idx_expr.getText()
                p_rhs, it_rhs = self.v.exprs.deepPlace(rhs_node)
                rhs_place = p_rhs or rhs_node.getText()

                log_semantic(f"[INDEX_STORE] inicio: {base_name}[{idx_place}] = {rhs_place}")
                log_semantic(f"[INDEX_STORE] tipos -> arr:{arr_t}, idx:{idx_t}, rhs:{rhs_t}")
                log_semantic(f"[INDEX_STORE] deepPlace -> idx='{idx_place}', rhs='{rhs_place}'")

                # --- Bounds check antes del store ---
                t_len, _ = self.v.emitter.emitBoundsCheck(idx_place, base_name)
                self.v.emitter.emit(Op.INDEX_STORE, arg1=base_name, res=rhs_place, label=idx_place)
                log_semantic(f"[INDEX_STORE] emitido: {base_name}[{idx_place}] = {rhs_place}")

                if it_idx:
                    self.v.emitter.temp_pool.free(idx_place, "*")
                if it_rhs:
                    self.v.emitter.temp_pool.free(rhs_place, "*")
                self.v.emitter.temp_pool.free(t_len, "*")
                self.v.emitter.temp_pool.resetPerStatement()
                return


        # (2) propiedad: obj.prop = expr (solo cuando hay Identifier() en ctx)
        if n == 2:
            lhs_obj = exprs[0]
            rhs_exp = exprs[1]

            prop_tok = getattr(ctx, "Identifier", lambda: None)()
            try:
                prop_name = prop_tok.getText() if prop_tok is not None else "<prop>"
            except Exception:
                prop_name = "<prop>"

            obj_t = self.v.visit(lhs_obj)
            if not isinstance(obj_t, ClassType):
                self.v.appendErr(SemanticError(
                    f"Asig. a propiedad en no-objeto: '{obj_t}'.",
                    line=ctx.start.line, column=ctx.start.column))
                log_semantic(f"[assign.prop] ERROR: '{lhs_obj}' no es objeto")
                self.v.emitter.temp_pool.resetPerStatement()
                return

            class_name = obj_t.name
            prop_t = self.v.class_handler.get_attribute_type(class_name, prop_name)
            if prop_t is None:
                self.v.appendErr(SemanticError(
                    f"Miembro '{prop_name}' no declarado en clase '{class_name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                log_semantic(f"[assign.prop] ERROR: atributo '{prop_name}' no encontrado en '{class_name}'")
                self.v.emitter.temp_pool.resetPerStatement()
                return

            rhs_t = self.v.visit(rhs_exp)
            if rhs_t is None or isinstance(rhs_t, ErrorType) or not isAssignable(prop_t, rhs_t):
                self.v.appendErr(SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_t} a {prop_t} en '{class_name}.{prop_name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                log_semantic(f"[assign.prop] ERROR: tipos incompatibles para '{class_name}.{prop_name}'")
                self.v.emitter.temp_pool.resetPerStatement()
                return

            p_obj, _ = self.v.exprs.deepPlace(lhs_obj)
            obj_place = p_obj or lhs_obj.getText()
            p_rhs, _ = self.v.exprs.deepPlace(rhs_exp)
            rhs_place = p_rhs or rhs_exp.getText()

            q = self.v.emitter.emit(Op.FIELD_STORE, arg1=obj_place, res=rhs_place, label=prop_name)
            log_semantic(f"[FIELD_STORE] emitido: {obj_place}.{prop_name} = {rhs_place}")

            try:
                off = self.v.class_handler.get_field_offset(class_name, prop_name)
                if q is not None and off is not None:
                    setattr(q, "_field_offset", off)
                    setattr(q, "_field_owner", class_name)
            except Exception:
                pass

            self.v.emitter.temp_pool.resetPerStatement()
            return


    # ------------------------------------------------------------------
    # foreach (semántica + scope)
    # ------------------------------------------------------------------
    @log_function
    def visitForeachStatement(self, ctx):
        iter_name = ctx.Identifier().getText()
        log_semantic(f"[foreach] inicio: iterador='{iter_name}'")

        iter_expr_type = self.v.visit(ctx.expression())
        log_semantic(f"[foreach] tipo de expresión iterada -> {iter_expr_type}")

        if isinstance(iter_expr_type, ArrayType):
            elem_type = iter_expr_type.elem_type
        else:
            if not isinstance(iter_expr_type, ErrorType):
                self.v.appendErr(SemanticError(
                    f"foreach requiere un arreglo; se encontró {iter_expr_type}.",
                    line=ctx.start.line, column=ctx.start.column))
                log_semantic(f"[foreach] ERROR: expresión no es arreglo -> {iter_expr_type}")
            elem_type = ErrorType()

        self.v.scopeManager.enterScope()
        log_semantic("[scope] nuevo scope foreach iniciado")

        try:
            sym = self.v.scopeManager.addSymbol(
                iter_name, elem_type, category=SymbolCategory.VARIABLE,
                initialized=True, init_value_type=elem_type, init_note="foreach-var"
            )
            log_semantic(f"Foreach var '{iter_name}' declarada con tipo: {elem_type}, tamaño: {sym.width} bytes (note=foreach-var)")
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))
            log_semantic(f"[foreach] ERROR al declarar variable iteradora '{iter_name}': {e}")

        # Visitar cuerpo del foreach (bloque)
        self.v.visit(ctx.block())

        size = self.v.scopeManager.exitScope()
        log_semantic(f"[scope] foreach cerrado; frame_size={size} bytes")

        self.v.emitter.temp_pool.resetPerStatement()
        log_semantic(f"[foreach] finalizado: iterador='{iter_name}'")
        return {"terminated": False, "reason": None}

