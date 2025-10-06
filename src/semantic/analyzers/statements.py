from antlr4.tree.Tree import TerminalNode
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.symbol_kinds import SymbolCategory
from semantic.custom_types import (
    NullType, ErrorType, ArrayType, IntegerType, VoidType, ClassType
)
from semantic.type_system import isAssignable, isReferenceType
from semantic.registry.type_resolver import resolveTypeCtx, validateKnownTypes
from semantic.errors import SemanticError
from logs.logger import log
from utils.ast_utils import walk, isAssignText


class StatementsAnalyzer:

    def __init__(self, v):
        log("\n" + "="*80, channel="semantic")
        log("===== [StatementsAnalyzer] Inicio SEMÁNTICO =====", channel="semantic")
        log("="*80 + "\n", channel="semantic")
        self.v = v

    # ----------------------------------
    # Helpers de navegación de árbol
    # ----------------------------------
    def findDesc(self, node, klass):
        """Busca el primer descendiente de tipo 'klass'"""
        for ch in walk(node):
            if isinstance(ch, klass):
                log(f"[findDesc] encontrado: {klass.__name__} en nodo {node}", channel="semantic")
                return ch
        return None

    def findAllDesc(self, node, klass):
        """Devuelve todos los descendientes de tipo 'klass'"""
        results = [ch for ch in walk(node) if isinstance(ch, klass)]
        log(f"[findAllDesc] encontrados {len(results)} nodos de tipo {klass.__name__}", channel="semantic")
        return results

    def expressionsFromCTX(self, ctx):
        """Extrae todas las expresiones dentro de un contexto"""
        exprs = []
        try:
            raw_exprs = ctx.getRuleContexts(CompiscriptParser.ExpressionContext)
            if raw_exprs:
                exprs = list(raw_exprs)
        except Exception:
            pass

        if not exprs:
            try:
                raw = ctx.expression()
                if raw is None:
                    return []
                exprs = list(raw) if isinstance(raw, (list, tuple)) else [raw]
            except Exception:
                pass

        if not exprs:
            try:
                for ch in ctx.getChildren():
                    if isinstance(ch, CompiscriptParser.ExpressionContext):
                        exprs.append(ch)
                    else:
                        exprs.extend(self.findAllDesc(ch, CompiscriptParser.ExpressionContext))
            except Exception:
                pass

        log(f"[expressionsFromCTX] extraídas {len(exprs)} expresiones de {ctx}", channel="semantic")
        return exprs

    def hasTopLevelAssign(self, expr_ctx) -> bool:
        """Detecta si hay asignación al nivel superior"""
        try:
            assign_found = self.findDesc(expr_ctx, CompiscriptParser.AssignExprContext) is not None
            if assign_found:
                log(f"[hasTopLevelAssign] asignación detectada en {expr_ctx}", channel="semantic")
                return True
        except Exception:
            pass
        try:
            result = isAssignText(expr_ctx.getText() or "")
            log(f"[hasTopLevelAssign] resultado por texto: {result}", channel="semantic")
            return result
        except Exception:
            return False

    def rhsOfAssignExpr(self, expr_ctx):
        """Obtiene el lado derecho de la asignación"""
        rhs = None
        try:
            assign = self.findDesc(expr_ctx, CompiscriptParser.AssignExprContext)
            if assign:
                try:
                    rhs = assign.exprNoAssign()
                    if isinstance(rhs, (list, tuple)):
                        rhs = rhs[-1] if rhs else None
                except Exception:
                    rhs = None

                if rhs:
                    log(f"[rhsOfAssignExpr] RHS encontrado en assignExprContext: {rhs}", channel="semantic")
                    return rhs

                # fallback: buscar después del '='
                for i in range(assign.getChildCount()):
                    ch = assign.getChild(i)
                    if isinstance(ch, TerminalNode) and ch.getText() == '=':
                        rhs = assign.getChild(i + 1) if (i + 1) < assign.getChildCount() else None
                        if rhs:
                            log(f"[rhsOfAssignExpr] RHS encontrado tras '=': {rhs}", channel="semantic")
                            return rhs
        except Exception:
            pass

        # último recurso: buscar última expresión
        try:
            children_exprs = [ch for ch in expr_ctx.getChildren()
                              if isinstance(ch, (CompiscriptParser.ExprNoAssignContext,
                                                 CompiscriptParser.ExpressionContext))]
            if children_exprs:
                rhs = children_exprs[-1]
                log(f"[rhsOfAssignExpr] RHS fallback última expresión: {rhs}", channel="semantic")
                return rhs
        except Exception:
            pass

        log(f"[rhsOfAssignExpr] RHS no encontrado en {expr_ctx}", channel="semantic")
        return None

    # ----------------------------------
    # Patrones para asignaciones indexadas
    # ----------------------------------

    def matchSimpleIndexAssign(self, lhs_or_expr_node):
        lhs_ctx = self.findDesc(lhs_or_expr_node, CompiscriptParser.LeftHandSideContext)
        if lhs_ctx is None:
            log("[matchSimpleIndexAssign] No se encontró LeftHandSideContext", channel="semantic")
            return None

        try:
            lhs_txt = lhs_ctx.getText()
        except Exception:
            log("[matchSimpleIndexAssign] Error al obtener texto del LHS", channel="semantic")
            return None

        brk = lhs_txt.find('[')
        if brk <= 0:
            log(f"[matchSimpleIndexAssign] No es una asignación simple indexada: {lhs_txt}", channel="semantic")
            return None

        base_txt = lhs_txt[:brk]
        if base_txt == 'this' or '.' in base_txt:
            log(f"[matchSimpleIndexAssign] Base inválida para simple index assign: {base_txt}", channel="semantic")
            return None

        idx_node = self.findDesc(lhs_ctx, CompiscriptParser.IndexExprContext)
        if idx_node is None:
            log(f"[matchSimpleIndexAssign] No se encontró IndexExprContext en {lhs_txt}", channel="semantic")
            return None

        log(f"[matchSimpleIndexAssign] Asignación simple detectada: base={base_txt}, idx_node={idx_node}", channel="semantic")
        return (base_txt, idx_node)


    def matchPropertyIndexAssign(self, lhs_or_expr_node):
        lhs_ctx = self.findDesc(lhs_or_expr_node, CompiscriptParser.LeftHandSideContext)
        if lhs_ctx is None:
            log("[matchPropertyIndexAssign] No se encontró LeftHandSideContext", channel="semantic")
            return None

        try:
            lhs_txt = lhs_ctx.getText()
        except Exception:
            log("[matchPropertyIndexAssign] Error al obtener texto del LHS", channel="semantic")
            return None

        brk = lhs_txt.find('[')
        if brk <= 0:
            log(f"[matchPropertyIndexAssign] No es una asignación con propiedad indexada: {lhs_txt}", channel="semantic")
            return None

        base_txt = lhs_txt[:brk]
        if '.' not in base_txt:
            log(f"[matchPropertyIndexAssign] Base sin propiedad: {base_txt}", channel="semantic")
            return None

        parts = base_txt.split('.')
        if len(parts) < 2:
            log(f"[matchPropertyIndexAssign] Cadena de propiedad inválida: {base_txt}", channel="semantic")
            return None

        obj_txt = parts[0]
        prop_chain = parts[1:]

        idx_node = self.findDesc(lhs_ctx, CompiscriptParser.IndexExprContext)
        if idx_node is None:
            log(f"[matchPropertyIndexAssign] No se encontró IndexExprContext en {lhs_txt}", channel="semantic")
            return None

        log(f"[matchPropertyIndexAssign] Asignación indexada a propiedad detectada: obj={obj_txt}, prop_chain={prop_chain}, idx_node={idx_node}", channel="semantic")
        return (obj_txt, prop_chain, idx_node)

    # ----------------------------------
    # SEMÁNTICA de stores indexados (sin TAC)
    # ----------------------------------

    def handleSimpleIndexStore(self, base_name, idx_node, rhs_node, ctx_stmt):
        log(f"[handleSimpleIndexStore] Base={base_name}, idx_node={idx_node}, rhs_node={rhs_node}", channel="semantic")
        
        sym = self.v.scopeManager.lookup(base_name)
        if sym is None:
            self.v.appendErr(SemanticError(
                f"Uso de variable no declarada: '{base_name}'",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            return

        if getattr(sym, "category", None) == SymbolCategory.CONSTANT:
            self.v.appendErr(SemanticError(
                f"No se puede modificar la constante '{base_name}'.",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            return

        arr_t = getattr(sym, "type", None)

        try:
            idx_expr = idx_node.expression()
        except Exception:
            idx_expr = idx_node

        idx_t = self.v.visit(idx_expr)
        rhs_t = self.v.visit(rhs_node)

        if not isinstance(arr_t, ArrayType):
            self.v.appendErr(SemanticError(
                f"Asig. indexada sobre un no-arreglo: '{arr_t}'.",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            return

        if not isinstance(idx_t, IntegerType):
            self.v.appendErr(SemanticError(
                f"Índice no entero en asig. de arreglo: se encontró {idx_t}.",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            return

        elem_t = arr_t.elem_type
        if rhs_t is None or isinstance(rhs_t, ErrorType) or not isAssignable(elem_t, rhs_t):
            self.v.appendErr(SemanticError(
                f"Asignación incompatible: no se puede asignar {rhs_t} a {elem_t} en {base_name}[i].",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            return

        log(f"[handleSimpleIndexStore] Asignación válida: {base_name}[i] <- {rhs_t}", channel="semantic")


    def handleChainedPropertyIndexStore(self, obj_txt, prop_chain, idx_node, rhs_node, ctx_stmt):
        log(f"[handleChainedPropertyIndexStore] obj={obj_txt}, prop_chain={prop_chain}, idx_node={idx_node}, rhs_node={rhs_node}", channel="semantic")
        
        if obj_txt == 'this':
            if not self.v.class_stack:
                self.v.appendErr(SemanticError(
                    "Uso de 'this' fuera de una clase.",
                    line=ctx_stmt.start.line, column=ctx_stmt.start.column))
                return
            curr_type = ClassType(self.v.class_stack[-1])
        else:
            sym = self.v.scopeManager.lookup(obj_txt)
            if sym is None:
                self.v.appendErr(SemanticError(
                    f"Uso de variable no declarada: '{obj_txt}'.",
                    line=ctx_stmt.start.line, column=ctx_stmt.start.column))
                return
            if getattr(sym, "category", None) == SymbolCategory.CONSTANT:
                self.v.appendErr(SemanticError(
                    f"No se puede modificar la constante '{obj_txt}'.",
                    line=ctx_stmt.start.line, column=ctx_stmt.start.column))
                return
            curr_type = getattr(sym, "type", None)

        for prop_name in prop_chain:
            if not isinstance(curr_type, ClassType):
                self.v.appendErr(SemanticError(
                    f"Acceso a propiedad '{prop_name}' sobre tipo no-objeto: {curr_type}.",
                    line=ctx_stmt.start.line, column=ctx_stmt.start.column))
                return
            attr_t = self.v.class_handler.getAttributeType(curr_type.name, prop_name)
            if attr_t is None:
                self.v.appendErr(SemanticError(
                    f"La clase {curr_type} no tiene un atributo '{prop_name}'.",
                    line=ctx_stmt.start.line, column=ctx_stmt.start.column))
                return
            curr_type = attr_t

        if not isinstance(curr_type, ArrayType):
            self.v.appendErr(SemanticError(
                f"Índice aplicado sobre un miembro que no es arreglo: {curr_type}.",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            return

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

        elem_t = curr_type.elem_type
        if rhs_t is None or isinstance(rhs_t, ErrorType) or not isAssignable(elem_t, rhs_t):
            self.v.appendErr(SemanticError(
                f"Asignación incompatible: no se puede asignar {rhs_t} a {elem_t}.",
                line=ctx_stmt.start.line, column=ctx_stmt.start.column))
            return

        log(f"[handleChainedPropertyIndexStore] Asignación válida en propiedad indexada", channel="semantic")


    def handlePropertyIndexStore(self, obj_txt, prop_name, idx_node, rhs_node, ctx_stmt):
        log(f"[handlePropertyIndexStore] obj={obj_txt}, prop_name={prop_name}, idx_node={idx_node}, rhs_node={rhs_node}", channel="semantic")
        
        if obj_txt == 'this':
            if not self.v.class_stack:
                self.v.appendErr(SemanticError(
                    "Uso de 'this' fuera de una clase.",
                    line=ctx_stmt.start.line, column=ctx_stmt.start.column))
                return
            obj_type = ClassType(self.v.class_stack[-1])
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
            obj_type = getattr(sym, "type", None)
            if not isinstance(obj_type, ClassType):
                self.v.appendErr(SemanticError(
                    f"Asig. indexada a propiedad en no-objeto: '{obj_type}'.",
                    line=ctx_stmt.start.line, column=ctx_stmt.start.column))
                return

        field_t = self.v.class_handler.getAttributeType(obj_type.name, prop_name)
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

        log(f"[handlePropertyIndexStore] Asignación válida en {obj_txt}.{prop_name}[i]", channel="semantic")


    # ------------------------------------------------------------------
    # Sentencia de expresión
    # ------------------------------------------------------------------

    def visitExpressionStatement(self, ctx):
        expr = ctx.expression()
        txt = getattr(expr, "getText", lambda: "")()
        
        # Determinar si es asignación "top-level"
        is_assign = self.hasTopLevelAssign(expr) or (
            '=' in txt and not any(op in txt for op in ('==', '!=', '<=', '>='))
        )
        
        log(f"[visitExpressionStatement] Texto={txt}, is_assign={is_assign}", channel="semantic")

        if is_assign:
            # Caso de asignación simple de índice
            m = self.matchSimpleIndexAssign(expr)
            if m is not None:
                base_name, idx_node = m
                rhs_node = self.rhsOfAssignExpr(expr)
                if rhs_node is not None:
                    self.handleSimpleIndexStore(base_name, idx_node, rhs_node, ctx)
                return None

            # Caso de asignación sobre propiedad indexada
            mp = self.matchPropertyIndexAssign(expr)
            if mp is not None:
                obj_txt, prop_chain, idx_node = mp
                rhs_node = self.rhsOfAssignExpr(expr)
                if rhs_node is not None:
                    if len(prop_chain) == 1:
                        self.handlePropertyIndexStore(obj_txt, prop_chain[0], idx_node, rhs_node, ctx)
                    else:
                        self.handleChainedPropertyIndexStore(obj_txt, prop_chain, idx_node, rhs_node, ctx)
                return None

            # Otro tipo de asignación (por ejemplo variable = expr)
            return self.visitAssignment(expr)

        # No es asignación: simplemente visitar la expresión
        return self.v.visit(expr)


    # ------------------------------------------------------------------
    # Bloques (detección de código muerto)
    # ------------------------------------------------------------------
    def visitBlock(self, ctx):
        log("visitBlock: inicio de bloque", channel="semantic")
        is_fn_body = (getattr(self.v, "_fn_body_block_ctx", None) is ctx)
        log(f"visitBlock: es cuerpo de función? {is_fn_body}", channel="semantic")

        # Guardar estado exterior y limpiar
        saved_term = getattr(self.v, "stmt_just_terminated", None)
        saved_node = getattr(self.v, "stmt_just_terminator_node", None)
        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None

        # Abrir nuevo scope si no es el cuerpo directo de una función
        if not is_fn_body:
            self.v.scopeManager.enterScope()
            log("visitBlock: scope abierto", channel="semantic")

        terminated_in_block = False
        terminator_reason = None

        for st in ctx.statement():
            if terminated_in_block:
                # Reporta DeadCode pero sigue visitando semánticamente
                line = getattr(getattr(st, "start", None), "line", None)
                col  = getattr(getattr(st, "start", None), "column", None)
                self.v.appendErr(SemanticError(
                    f"Código inalcanzable: el flujo terminó por '{terminator_reason}' antes de esta sentencia.",
                    line=line, column=col, error_type="DeadCode"
                ))
                log(f"visitBlock: DeadCode detectado en línea {line}, columna {col}", channel="semantic")

                self.v.visit(st)  # visita semántica para efectos secundarios
                continue

            # Limpiar barrera antes de procesar la sentencia
            self.v.stmt_just_terminated = None
            self.v.stmt_just_terminator_node = None

            # Visita semántica
            log(f"visitBlock: visitando sentencia {getattr(st, 'getText', lambda: str(st))()}", channel="semantic")
            self.v.visit(st)

            # Si la sentencia terminó el flujo (p. ej. 'return')
            if getattr(self.v, "stmt_just_terminated", None):
                terminated_in_block = True
                terminator_reason = self.v.stmt_just_terminated
                log(f"visitBlock: flujo terminado por '{terminator_reason}'", channel="semantic")

        # Cerrar scope si aplica
        if not is_fn_body:
            self.v.scopeManager.exitScope()
            log("visitBlock: scope cerrado", channel="semantic")

        # Restaurar estado exterior
        self.v.stmt_just_terminated = saved_term
        self.v.stmt_just_terminator_node = saved_node
        log("visitBlock: fin de bloque", channel="semantic")

        return {"terminated": terminated_in_block, "reason": terminator_reason}


    # ------------------------------------------------------------------
    # Declaraciones: let / const
    # ------------------------------------------------------------------
    
    def visitVariableDeclaration(self, ctx):
        name = ctx.Identifier().getText()
        log(f"visitVariableDeclaration: inicio para '{name}'", channel="semantic")
        ann = ctx.typeAnnotation()
        init = ctx.initializer()

        # Validar existencia de tipo
        if ann is None:
            self.v.appendErr(SemanticError(
                f"La variable '{name}' debe declarar un tipo (no se permite inferencia).",
                line=ctx.start.line, column=ctx.start.column
            ))
            return

        declared_type = resolveTypeCtx(ann)
        log(f"visitVariableDeclaration: tipo declarado '{declared_type}'", channel="semantic")

        # Validar tipos conocidos
        if not validateKnownTypes(declared_type, self.v.known_classes, ctx, f"variable '{name}'", self.v.errors):
            return

        if isinstance(declared_type, VoidType):
            self.v.appendErr(SemanticError(
                f"La variable '{name}' no puede ser de tipo void.",
                line=ctx.start.line, column=ctx.start.column
            ))
            return

        # Determinar estado de inicialización
        initialized = False
        init_value_type = None
        init_note = None

        if not init:
            if isReferenceType(declared_type):
                initialized = True
                init_value_type = NullType()
                init_note = "default-null"
                log(f"visitVariableDeclaration: variable referencial inicializada a null", channel="semantic")
            else:
                initialized = False
                init_note = "uninitialized"
                log(f"visitVariableDeclaration: variable no inicializada", channel="semantic")
        else:
            rhs_type = self.v.visit(init.expression())
            log(f"visitVariableDeclaration: tipo de expresión RHS '{rhs_type}'", channel="semantic")

            if isinstance(rhs_type, ErrorType) or rhs_type is None:
                try:
                    self.v.scopeManager.addSymbol(
                        name, declared_type, category=SymbolCategory.VARIABLE,
                        initialized=False, init_value_type=None, init_note="init-error"
                    )
                except Exception:
                    pass
                if self.v.class_stack:
                    current_class = self.v.class_stack[-1]
                    if self.v.class_handler.getAttributeType(current_class, name) is None:
                        self.v.class_handler.addAttribute(current_class, name, declared_type)
                return

            if not isAssignable(declared_type, rhs_type):
                self.v.appendErr(SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_type} a {declared_type} en '{name}'.",
                    line=ctx.start.line, column=ctx.start.column
                ))
                try:
                    self.v.scopeManager.addSymbol(
                        name, declared_type, category=SymbolCategory.VARIABLE,
                        initialized=False, init_value_type=None, init_note="init-error"
                    )
                except Exception:
                    pass
                if self.v.class_stack:
                    current_class = self.v.class_stack[-1]
                    if self.v.class_handler.getAttributeType(current_class, name) is None:
                        self.v.class_handler.addAttribute(current_class, name, declared_type)
                return

            initialized = True
            init_value_type = rhs_type
            init_note = "explicit"
            log(f"visitVariableDeclaration: inicialización válida con tipo '{rhs_type}'", channel="semantic")

        # Agregar símbolo al scope
        try:
            self.v.scopeManager.addSymbol(
                name, declared_type, category=SymbolCategory.VARIABLE,
                initialized=initialized, init_value_type=init_value_type, init_note=init_note
            )
            log(f"visitVariableDeclaration: símbolo '{name}' agregado al scope", channel="semantic")
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))
            return

        if self.v.class_stack:
            current_class = self.v.class_stack[-1]
            if self.v.class_handler.getAttributeType(current_class, name) is None:
                self.v.class_handler.addAttribute(current_class, name, declared_type)
                log(f"visitVariableDeclaration: atributo '{name}' registrado en clase '{current_class}'", channel="semantic")


    def visitConstantDeclaration(self, ctx):
        name = ctx.Identifier().getText() if ctx.Identifier() else "<unnamed-const>"
        log(f"visitConstantDeclaration: inicio para '{name}'", channel="semantic")
        ann = ctx.typeAnnotation()
        expr_ctx = ctx.expression()

        if ann is None:
            self.v.appendErr(SemanticError(
                f"La constante '{name}' debe declarar un tipo.",
                line=ctx.start.line, column=ctx.start.column
            ))
            return

        declared_type = resolveTypeCtx(ann)
        log(f"visitConstantDeclaration: tipo declarado '{declared_type}'", channel="semantic")

        if not validateKnownTypes(declared_type, self.v.known_classes, ctx, f"constante '{name}'", self.v.errors):
            return

        if isinstance(declared_type, VoidType):
            self.v.appendErr(SemanticError(
                f"La constante '{name}' no puede ser de tipo void.",
                line=ctx.start.line, column=ctx.start.column
            ))
            return

        if expr_ctx is None:
            self.v.appendErr(SemanticError(
                f"Constante '{name}' sin inicializar (se requiere '= <expresión>').",
                line=ctx.start.line, column=ctx.start.column
            ))
            return

        rhs_type = self.v.visit(expr_ctx)
        log(f"visitConstantDeclaration: tipo de expresión RHS '{rhs_type}'", channel="semantic")

        if isinstance(rhs_type, ErrorType) or rhs_type is None:
            try:
                self.v.scopeManager.addSymbol(name, declared_type, category=SymbolCategory.CONSTANT)
            except Exception:
                pass
            if self.v.class_stack:
                current_class = self.v.class_stack[-1]
                if self.v.class_handler.getAttributeType(current_class, name) is None:
                    self.v.class_handler.addAttribute(current_class, name, declared_type)
            return

        if not isAssignable(declared_type, rhs_type):
            self.v.appendErr(SemanticError(
                f"Asignación incompatible: no se puede asignar {rhs_type} a {declared_type} en constante '{name}'.",
                line=ctx.start.line, column=ctx.start.column
            ))
            return

        try:
            self.v.scopeManager.addSymbol(name, declared_type, category=SymbolCategory.CONSTANT)
            log(f"visitConstantDeclaration: símbolo '{name}' agregado al scope", channel="semantic")
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))
            return

        if self.v.class_stack:
            current_class = self.v.class_stack[-1]
            if self.v.class_handler.getAttributeType(current_class, name) is None:
                self.v.class_handler.addAttribute(current_class, name, declared_type)
                log(f"visitConstantDeclaration: atributo '{name}' registrado en clase '{current_class}'", channel="semantic")


    # ------------------------------------------------------------------
    # Asignaciones (sin TAC)
    # ------------------------------------------------------------------
    def visitAssignment(self, ctx):
        log("visitAssignment: inicio", channel="semantic")
        is_expr_ctx = isinstance(ctx, CompiscriptParser.ExpressionContext)
        exprs = self.expressionsFromCTX(ctx)
        n = len(exprs)
        log(f"visitAssignment: {n} expresiones detectadas", channel="semantic")

        # Caso: contexto de expresión con dos expresiones (lhs = rhs)
        if is_expr_ctx and n == 2:
            log("visitAssignment: intento de asignación lhs=rhs", channel="semantic")
            m = self.matchSimpleIndexAssign(exprs[0])
            if m is not None:
                base_name, idx_node = m
                rhs_node = exprs[1]
                log(f"visitAssignment: índice simple {base_name}[i]", channel="semantic")
                self.handleSimpleIndexStore(base_name, idx_node, rhs_node, ctx)
                return

            # Intentar asignación a variable simple
            name = None
            lhs_ctx = self.findDesc(exprs[0], CompiscriptParser.LeftHandSideContext)
            if lhs_ctx:
                try:
                    has_suffix = bool(lhs_ctx.suffixOp() or [])
                except Exception:
                    has_suffix = False

                if not has_suffix:
                    try:
                        name = lhs_ctx.primaryAtom().getText()
                    except Exception:
                        name = None
                    if not name:
                        ident = self.findDesc(lhs_ctx, CompiscriptParser.IdentifierExprContext)
                        if ident: name = ident.getText()

            if name:
                log(f"visitAssignment: variable simple '{name}'", channel="semantic")
                sym = self.v.scopeManager.lookup(name)
                if sym is None:
                    self.v.appendErr(SemanticError(
                        f"Uso de variable no declarada: '{name}'",
                        line=ctx.start.line, column=ctx.start.column))
                    return
                if sym.category == SymbolCategory.CONSTANT:
                    self.v.appendErr(SemanticError(
                        f"No se puede modificar la constante '{name}'.",
                        line=ctx.start.line, column=ctx.start.column))
                    return

                rhs_type = self.v.visit(exprs[1])
                if rhs_type is None or isinstance(rhs_type, ErrorType):
                    return
                if not isAssignable(sym.type, rhs_type):
                    self.v.appendErr(SemanticError(
                        f"Asignación incompatible: no se puede asignar {rhs_type} a {sym.type} en '{name}'.",
                        line=ctx.start.line, column=ctx.start.column))
                    return
            return

        # Caso: asignación a variable simple desde expresión única
        if n == 1 and ctx.Identifier() is not None:
            name = ctx.Identifier().getText()
            log(f"visitAssignment: asignación a variable simple desde expr única '{name}'", channel="semantic")
            sym = self.v.scopeManager.lookup(name)
            if sym is None:
                self.v.appendErr(SemanticError(
                    f"Uso de variable no declarada: '{name}'",
                    line=ctx.start.line, column=ctx.start.column))
                return
            if sym.category == SymbolCategory.CONSTANT:
                self.v.appendErr(SemanticError(
                    f"No se puede modificar la constante '{name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                return

            rhs_type = self.v.visit(exprs[0])
            if rhs_type is None or isinstance(rhs_type, ErrorType):
                return
            if not isAssignable(sym.type, rhs_type):
                self.v.appendErr(SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_type} a {sym.type} en '{name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                return
            return

        # Caso general: dos expresiones (lhs = rhs) para propiedades
        if n == 2:
            m = self.matchSimpleIndexAssign(exprs[0])
            if m is not None:
                base_name, idx_node = m
                rhs_node = exprs[1]
                log(f"visitAssignment: índice simple {base_name}[i]", channel="semantic")
                self.handleSimpleIndexStore(base_name, idx_node, rhs_node, ctx)
                return

            lhs_obj = exprs[0]
            rhs_exp = exprs[1]

            try:
                prop_name = getattr(ctx, "Identifier", lambda: None)()
                prop_name = prop_name.getText() if prop_name else "<prop>"
            except Exception:
                prop_name = "<prop>"

            obj_t = self.v.visit(lhs_obj)
            if not isinstance(obj_t, ClassType):
                self.v.appendErr(SemanticError(
                    f"Asig. a propiedad en no-objeto: '{obj_t}'.",
                    line=ctx.start.line, column=ctx.start.column))
                return
            log(f"visitAssignment: asignación a propiedad '{prop_name}' de clase '{obj_t.name}'", channel="semantic")

            class_name = obj_t.name
            prop_t = self.v.class_handler.getAttributeType(class_name, prop_name)
            if prop_t is None:
                self.v.appendErr(SemanticError(
                    f"Miembro '{prop_name}' no declarado en clase '{class_name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                return

            rhs_t = self.v.visit(rhs_exp)
            if rhs_t is None or isinstance(rhs_t, ErrorType) or not isAssignable(prop_t, rhs_t):
                self.v.appendErr(SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_t} a {prop_t} en '{class_name}.{prop_name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                return


    # ------------------------------------------------------------------
    # foreach (semántica + scope)
    # ------------------------------------------------------------------
    def visitForeachStatement(self, ctx):
        iter_name = ctx.Identifier().getText()
        log(f"visitForeachStatement: variable de iteración '{iter_name}'", channel="semantic")
        iter_expr_type = self.v.visit(ctx.expression())

        if isinstance(iter_expr_type, ArrayType):
            elem_type = iter_expr_type.elem_type
            log(f"visitForeachStatement: tipo de elemento '{elem_type}'", channel="semantic")
        else:
            if not isinstance(iter_expr_type, ErrorType):
                self.v.appendErr(SemanticError(
                    f"foreach requiere un arreglo; se encontró {iter_expr_type}.",
                    line=ctx.start.line, column=ctx.start.column))
            elem_type = ErrorType()

        self.v.scopeManager.enterScope()
        try:
            self.v.scopeManager.addSymbol(
                iter_name, elem_type, category=SymbolCategory.VARIABLE,
                initialized=True, init_value_type=elem_type, init_note="foreach-var"
            )
            log(f"visitForeachStatement: símbolo '{iter_name}' agregado al scope", channel="semantic")
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))

        self.v.visit(ctx.block())
        self.v.scopeManager.exitScope()
        log(f"visitForeachStatement: scope cerrado para '{iter_name}'", channel="semantic")
        return {"terminated": False, "reason": None}
