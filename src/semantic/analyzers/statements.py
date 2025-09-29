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
                log_semantic(f"hasTopLevelAssign -> '=' encontrado en top level")
                return True
        return False

    @log_function
    def matchSimpleIndexAssign(self, lhs_or_expr_node):
        log_semantic(f"matchSimpleIndexAssign -> lhs_or_expr_node={lhs_or_expr_node}")
        lhs_ctx = self.findDesc(lhs_or_expr_node, CompiscriptParser.LeftHandSideContext)
        if lhs_ctx is None:
            return None

        idx_node = self.findDesc(lhs_ctx, CompiscriptParser.IndexExprContext)
        if idx_node is not None:
            base_name = lhs_ctx.primaryAtom().getText()
            log_semantic(f"matchSimpleIndexAssign -> encontrado {base_name}[{idx_node.getText()}]")
            return (base_name, idx_node)

        return None

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

        # usar la expresión interna del índice si existe
        try:
            idx_expr = idx_node.expression()
        except Exception:
            idx_expr = None
        if idx_expr is None:
            idx_expr = idx_node

        sym = self.v.scopeManager.lookup(base_name)
        if sym is None:
            log_semantic(f"handleSimpleIndexStore -> ERROR variable no declarada: {base_name}")
            return

        arr_t = sym.type
        idx_t = self.v.visit(idx_expr)
        rhs_t = self.v.visit(rhs_node)
        log_semantic(f"handleSimpleIndexStore -> tipos -> arr:{arr_t}, idx:{idx_t}, rhs:{rhs_t}")

        p_idx, it_idx = self.v.exprs.deepPlace(idx_expr)
        idx_place = p_idx or idx_expr.getText()
        p_rhs, it_rhs = self.v.exprs.deepPlace(rhs_node)
        rhs_place = p_rhs or rhs_node.getText()
        log_semantic(f"handleSimpleIndexStore -> deepPlace -> idx='{idx_place}', rhs='{rhs_place}'")

        self.v.emitter.emit(Op.INDEX_STORE, arg1=base_name, res=rhs_place, label=idx_place)
        log_semantic(f"handleSimpleIndexStore -> emitido: {base_name}[{idx_place}] = {rhs_place}")


    # ------------------------------------------------------------------
    # Sentencia de expresión
    # ------------------------------------------------------------------
    @log_function
    def visitExpressionStatement(self, ctx):
        log_semantic(f"visitExpressionStatement -> ctx={ctx}")
        
        expr = ctx.expression()
        txt = getattr(expr, "getText", lambda: "")()
        log_semantic(f"[stmt] visitExpressionStatement: '{txt}'")

        is_assign = self.hasTopLevelAssign(expr) or ('=' in txt and not any(op in txt for op in ('==','!=','<=','>=')))
        log_semantic(f"[stmt] detectado assignment={is_assign}")

        if is_assign:
            log_semantic("[stmt] assignment detectado")

            # Caso simple indexado
            m = self.matchSimpleIndexAssign(expr)
            if m is not None:
                base_name, idx_node = m
                rhs_node = self.rhsOfAssignExpr(expr)
                if rhs_node is not None:
                    log_semantic(f"[stmt] matchSimpleIndexAssign -> base='{base_name}', idx='{idx_node.getText()}', rhs='{rhs_node.getText()}'")
                    self.handleSimpleIndexStore(base_name, idx_node, rhs_node, ctx)
                    log_semantic("[stmt] salida visitExpressionStatement (INDEX_STORE emitido)")
                    return None

            # Fallback
            log_semantic("[stmt] fallback visitAssignment(expr)")
            self.visitAssignment(expr)
            self.v.emitter.temp_pool.resetPerStatement()
            return None

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
                    # sin sufijos -> identificador pelado
                    has_suffix = False
                    try:
                        sufs = lhs_ctx.suffixOp()
                        has_suffix = (sufs is not None) and (len(sufs) > 0)
                    except Exception:
                        pass
                    if not has_suffix:
                        try:
                            name = lhs_ctx.primaryAtom().getText()
                        except Exception:
                            name = None

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

                self.v.emitter.emit(Op.INDEX_STORE, arg1=base_name, res=rhs_place, label=idx_place)
                log_semantic(f"[INDEX_STORE] emitido: {base_name}[{idx_place}] = {rhs_place}")

                if it_idx:
                    self.v.emitter.temp_pool.free(idx_place, "*")
                if it_rhs:
                    self.v.emitter.temp_pool.free(rhs_place, "*")
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

