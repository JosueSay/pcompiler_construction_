from antlr4.tree.Tree import TerminalNode
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.symbol_kinds import SymbolCategory
from semantic.custom_types import (
    NullType, ErrorType, ArrayType, IntegerType, VoidType, ClassType
)
from semantic.type_system import isAssignable, isReferenceType
from semantic.registry.type_resolver import resolveTypeCtx, validateKnownTypes
from semantic.errors import SemanticError
from logs.logger import log, logFunction
from utils.ast_utils import walk, isAssignText


class StatementsAnalyzer:

    @logFunction(channel="semantic")
    def __init__(self, v):
        log("===== [statements.py] Inicio (SEMÁNTICO) =====", channel="semantic")
        self.v = v

    # ----------------------------------
    # Helpers de navegación de árbol
    # ----------------------------------
    @logFunction(channel="semantic")
    def findDesc(self, node, klass):
        for ch in walk(node):
            if isinstance(ch, klass):
                return ch
        return None

    @logFunction(channel="semantic")
    def findAllDesc(self, node, klass):
        return [ch for ch in walk(node) if isinstance(ch, klass)]

    @logFunction(channel="semantic")
    def expressionsFromCTX(self, ctx):
        try:
            exprs = ctx.getRuleContexts(CompiscriptParser.ExpressionContext)
            if exprs:
                return list(exprs)
        except Exception:
            pass
        try:
            raw = ctx.expression()
            if raw is None:
                return []
            if isinstance(raw, (list, tuple)):
                return list(raw)
            return [raw]
        except Exception:
            pass
        res = []
        try:
            for ch in ctx.getChildren():
                if isinstance(ch, CompiscriptParser.ExpressionContext):
                    res.append(ch)
                else:
                    res.extend(self.findAllDesc(ch, CompiscriptParser.ExpressionContext))
        except Exception:
            pass
        return res

    @logFunction(channel="semantic")
    def hasTopLevelAssign(self, expr_ctx) -> bool:
        try:
            if self.findDesc(expr_ctx, CompiscriptParser.AssignExprContext) is not None:
                return True
        except Exception:
            pass
        try:
            return isAssignText(expr_ctx.getText() or "")
        except Exception:
            return False

    @logFunction(channel="semantic")
    def rhsOfAssignExpr(self, expr_ctx):
        try:
            assign = self.findDesc(expr_ctx, CompiscriptParser.AssignExprContext)
            if assign is not None:
                rhs = None
                try:
                    rhs = assign.exprNoAssign()
                    if isinstance(rhs, (list, tuple)):
                        rhs = rhs[-1] if rhs else None
                except Exception:
                    rhs = None
                if rhs is not None:
                    return rhs

                n = assign.getChildCount()
                saw_eq = False
                for i in range(n):
                    ch = assign.getChild(i)
                    if isinstance(ch, TerminalNode) and ch.getText() == '=':
                        saw_eq = True
                        continue
                    if saw_eq and (isinstance(ch, CompiscriptParser.ExprNoAssignContext) or
                                   isinstance(ch, CompiscriptParser.ExpressionContext)):
                        return ch
        except Exception:
            pass

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
                    return ch
        except Exception:
            pass

        try:
            raw = expr_ctx.expression()
            exprs = list(raw) if isinstance(raw, (list, tuple)) else ([raw] if raw is not None else [])
            if exprs:
                return exprs[-1]
        except Exception:
            pass

        try:
            last = None
            for ch in expr_ctx.getChildren():
                if isinstance(ch, CompiscriptParser.ExprNoAssignContext) or isinstance(ch, CompiscriptParser.ExpressionContext):
                    last = ch
            return last
        except Exception:
            pass

        return None

    # ----------------------------------
    # Patrones para asignaciones indexadas
    # ----------------------------------
    @logFunction(channel="semantic")
    def matchSimpleIndexAssign(self, lhs_or_expr_node):
        lhs_ctx = self.findDesc(lhs_or_expr_node, CompiscriptParser.LeftHandSideContext)
        if lhs_ctx is None:
            return None
        try:
            lhs_txt = lhs_ctx.getText()
        except Exception:
            return None
        brk = lhs_txt.find('[')
        if brk <= 0:
            return None
        base_txt = lhs_txt[:brk]
        if base_txt == 'this' or '.' in base_txt:
            return None
        idx_node = self.findDesc(lhs_ctx, CompiscriptParser.IndexExprContext)
        if idx_node is None:
            return None
        return (base_txt, idx_node)

    @logFunction(channel="semantic")
    def matchPropertyIndexAssign(self, lhs_or_expr_node):
        lhs_ctx = self.findDesc(lhs_or_expr_node, CompiscriptParser.LeftHandSideContext)
        if lhs_ctx is None:
            return None
        try:
            lhs_txt = lhs_ctx.getText()
        except Exception:
            return None
        brk = lhs_txt.find('[')
        if brk <= 0:
            return None
        base_txt = lhs_txt[:brk]
        if '.' not in base_txt:
            return None
        parts = base_txt.split('.')
        if len(parts) < 2:
            return None
        obj_txt = parts[0]
        prop_chain = parts[1:]
        idx_node = self.findDesc(lhs_ctx, CompiscriptParser.IndexExprContext)
        if idx_node is None:
            return None
        return (obj_txt, prop_chain, idx_node)

    # ----------------------------------
    # SEMÁNTICA de stores indexados (sin TAC)
    # ----------------------------------
    @logFunction(channel="semantic")
    def handleSimpleIndexStore(self, base_name, idx_node, rhs_node, ctx_stmt):
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

    @logFunction(channel="semantic")
    def handleChainedPropertyIndexStore(self, obj_txt, prop_chain, idx_node, rhs_node, ctx_stmt):
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

    @logFunction(channel="semantic")
    def handlePropertyIndexStore(self, obj_txt, prop_name, idx_node, rhs_node, ctx_stmt):
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

    # ------------------------------------------------------------------
    # Sentencia de expresión
    # ------------------------------------------------------------------
    @logFunction(channel="semantic")
    def visitExpressionStatement(self, ctx):
        expr = ctx.expression()
        txt = getattr(expr, "getText", lambda: "")()
        is_assign = self.hasTopLevelAssign(expr) or (
            '=' in txt and not any(op in txt for op in ('==', '!=', '<=', '>='))
        )

        if is_assign:
            m = self.matchSimpleIndexAssign(expr)
            if m is not None:
                base_name, idx_node = m
                rhs_node = self.rhsOfAssignExpr(expr)
                if rhs_node is not None:
                    self.handleSimpleIndexStore(base_name, idx_node, rhs_node, ctx)
                return None

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

            return self.visitAssignment(expr)

        return self.v.visit(expr)

    # ------------------------------------------------------------------
    # Bloques (detección de código muerto)
    # ------------------------------------------------------------------
    @logFunction(channel="semantic")
    def visitBlock(self, ctx):
        # ¿Es el cuerpo directo de una función? (tu driver suele marcarlo así)
        is_fn_body = (getattr(self.v, "_fn_body_block_ctx", None) is ctx)

        # Guardar y limpiar estado de barrera del contexto exterior
        saved_term = getattr(self.v, "stmt_just_terminated", None)
        saved_node = getattr(self.v, "stmt_just_terminator_node", None)
        self.v.stmt_just_terminated = None
        self.v.stmt_just_terminator_node = None

        # Abrir scope si no es el body de función
        if not is_fn_body:
            self.v.scopeManager.enterScope()

        terminated_in_block = False
        terminator_reason = None

        for st in ctx.statement():
            if terminated_in_block:
                # Reporta DeadCode y AÚN ASÍ visita semánticamente el statement
                # para detectar errores como 'this' fuera de clase, etc.
                line = getattr(getattr(st, "start", None), "line", None)
                col  = getattr(getattr(st, "start", None), "column", None)
                self.v.appendErr(SemanticError(
                    f"Código inalcanzable: el flujo terminó por '{terminator_reason}' antes de esta sentencia.",
                    line=line, column=col, error_type="DeadCode"
                ))

                # Visita SEMÁNTICAMENTE (esta fase no emite TAC).
                # Si quieres blindarte de efectos secundarios (p.ej. nuevas
                # declaraciones), podrías activar un flag opcional self.v.in_dead_code.
                self.v.visit(st)
                continue

            # Limpia la barrera antes de cada sentencia
            self.v.stmt_just_terminated = None
            self.v.stmt_just_terminator_node = None

            # Analiza semánticamente la sentencia
            self.v.visit(st)

            # Si la sentencia terminó el flujo (p. ej. 'return'), activa barrera local
            if getattr(self.v, "stmt_just_terminated", None):
                terminated_in_block = True
                terminator_reason = self.v.stmt_just_terminated

        # Cierra scope si aplica
        if not is_fn_body:
            self.v.scopeManager.exitScope()

        # Restaura el estado de barrera del contexto exterior
        self.v.stmt_just_terminated = saved_term
        self.v.stmt_just_terminator_node = saved_node

        return {"terminated": terminated_in_block, "reason": terminator_reason}

    # ------------------------------------------------------------------
    # Declaraciones: let / const
    # ------------------------------------------------------------------
    @logFunction(channel="semantic")
    def visitVariableDeclaration(self, ctx):
        name = ctx.Identifier().getText()
        ann = ctx.typeAnnotation()
        init = ctx.initializer()

        if ann is None:
            self.v.appendErr(SemanticError(
                f"La variable '{name}' debe declarar un tipo (no se permite inferencia).",
                line=ctx.start.line, column=ctx.start.column))
            return

        declared_type = resolveTypeCtx(ann)

        if not validateKnownTypes(declared_type, self.v.known_classes, ctx, f"variable '{name}'", self.v.errors):
            return

        if isinstance(declared_type, VoidType):
            self.v.appendErr(SemanticError(
                f"La variable '{name}' no puede ser de tipo void.",
                line=ctx.start.line, column=ctx.start.column))
            return

        initialized = False
        init_value_type = None
        init_note = None

        if not init:
            if isReferenceType(declared_type):
                initialized = True
                init_value_type = NullType()
                init_note = "default-null"
            else:
                initialized = False
                init_value_type = None
                init_note = "uninitialized"
        else:
            rhs_type = self.v.visit(init.expression())
            if isinstance(rhs_type, ErrorType) or rhs_type is None:
                # Registrar símbolo no inicializado para evitar cascada
                try:
                    self.v.scopeManager.addSymbol(
                        name, declared_type, category=SymbolCategory.VARIABLE,
                        initialized=False, init_value_type=None, init_note="init-error"
                    )
                except Exception:
                    pass
                if self.v.class_stack:
                    current_class = self.v.class_stack[-1]
                    try:
                        already = self.v.class_handler.getAttributeType(current_class, name)
                    except Exception:
                        already = None
                    if already is None:
                        self.v.class_handler.addAttribute(current_class, name, declared_type)
                return

            if not isAssignable(declared_type, rhs_type):
                self.v.appendErr(SemanticError(
                    f"Asignación incompatible: no se puede asignar {rhs_type} a {declared_type} en '{name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                # Declarar como no inicializada para mantener símbolo
                try:
                    self.v.scopeManager.addSymbol(
                        name, declared_type, category=SymbolCategory.VARIABLE,
                        initialized=False, init_value_type=None, init_note="init-error"
                    )
                except Exception:
                    pass
                if self.v.class_stack:
                    current_class = self.v.class_stack[-1]
                    try:
                        already = self.v.class_handler.getAttributeType(current_class, name)
                    except Exception:
                        already = None
                    if already is None:
                        self.v.class_handler.addAttribute(current_class, name, declared_type)
                return

            initialized = True
            init_value_type = rhs_type
            init_note = "explicit"

        try:
            self.v.scopeManager.addSymbol(
                name, declared_type, category=SymbolCategory.VARIABLE,
                initialized=initialized, init_value_type=init_value_type, init_note=init_note
            )
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))
            return

        if self.v.class_stack:
            current_class = self.v.class_stack[-1]
            try:
                already = self.v.class_handler.getAttributeType(current_class, name)
            except Exception:
                already = None
            if already is None:
                self.v.class_handler.addAttribute(current_class, name, declared_type)

    @logFunction(channel="semantic")
    def visitConstantDeclaration(self, ctx):
        name = ctx.Identifier().getText() if ctx.Identifier() else "<unnamed-const>"
        ann = ctx.typeAnnotation()
        expr_ctx = ctx.expression()

        if ann is None:
            self.v.appendErr(SemanticError(
                f"La constante '{name}' debe declarar un tipo.",
                line=ctx.start.line, column=ctx.start.column))
            return

        declared_type = resolveTypeCtx(ann)

        if not validateKnownTypes(declared_type, self.v.known_classes, ctx, f"constante '{name}'", self.v.errors):
            return

        if isinstance(declared_type, VoidType):
            self.v.appendErr(SemanticError(
                f"La constante '{name}' no puede ser de tipo void.",
                line=ctx.start.line, column=ctx.start.column))
            return

        if expr_ctx is None:
            self.v.appendErr(SemanticError(
                f"Constante '{name}' sin inicializar (se requiere '= <expresión>').",
                line=ctx.start.line, column=ctx.start.column))
            return

        rhs_type = self.v.visit(expr_ctx)
        if isinstance(rhs_type, ErrorType) or rhs_type is None:
            try:
                self.v.scopeManager.addSymbol(name, declared_type, category=SymbolCategory.CONSTANT)
            except Exception:
                pass
            if self.v.class_stack:
                current_class = self.v.class_stack[-1]
                try:
                    already = self.v.class_handler.getAttributeType(current_class, name)
                except Exception:
                    already = None
                if already is None:
                    self.v.class_handler.addAttribute(current_class, name, declared_type)
            return

        if not isAssignable(declared_type, rhs_type):
            self.v.appendErr(SemanticError(
                f"Asignación incompatible: no se puede asignar {rhs_type} a {declared_type} en constante '{name}'.",
                line=ctx.start.line, column=ctx.start.column))
            return

        try:
            self.v.scopeManager.addSymbol(name, declared_type, category=SymbolCategory.CONSTANT)
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))
            return

        if self.v.class_stack:
            current_class = self.v.class_stack[-1]
            try:
                already = self.v.class_handler.getAttributeType(current_class, name)
            except Exception:
                already = None
            if already is None:
                self.v.class_handler.addAttribute(current_class, name, declared_type)

    # ------------------------------------------------------------------
    # Asignaciones (sin TAC)
    # ------------------------------------------------------------------
    @logFunction(channel="semantic")
    def visitAssignment(self, ctx):
        is_expr_ctx = isinstance(ctx, CompiscriptParser.ExpressionContext)
        exprs = self.expressionsFromCTX(ctx)
        n = len(exprs)

        if is_expr_ctx:
            if n == 2:
                m = self.matchSimpleIndexAssign(exprs[0])
                if m is not None:
                    base_name, idx_node = m
                    rhs_node = exprs[1]
                    self.handleSimpleIndexStore(base_name, idx_node, rhs_node, ctx)
                    return

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
                        try:
                            name = lhs_ctx.primaryAtom().getText()
                        except Exception:
                            name = None
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

        if n == 1 and ctx.Identifier() is not None:
            name = ctx.Identifier().getText()
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

        if n == 2:
            m = self.matchSimpleIndexAssign(exprs[0])
            if m is not None:
                base_name, idx_node = m
                rhs_node = exprs[1]
                self.handleSimpleIndexStore(base_name, idx_node, rhs_node, ctx)
                return

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
                return

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
    @logFunction(channel="semantic")
    def visitForeachStatement(self, ctx):
        iter_name = ctx.Identifier().getText()

        iter_expr_type = self.v.visit(ctx.expression())

        if isinstance(iter_expr_type, ArrayType):
            elem_type = iter_expr_type.elem_type
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
        except Exception as e:
            self.v.appendErr(SemanticError(str(e), line=ctx.start.line, column=ctx.start.column))

        self.v.visit(ctx.block())
        self.v.scopeManager.exitScope()
        return {"terminated": False, "reason": None}
