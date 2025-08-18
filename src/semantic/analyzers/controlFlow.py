from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import BoolType, ErrorType, ClassType, ArrayType
from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic

def _as_list(x):
    """
    Normaliza llamadas de ANTLR que pueden devolver una lista de contexts o un solo context.
    - None -> []
    - [ctx, ...] -> list(ctxs)
    - ctx -> [ctx]
    """
    if x is None:
        return []
    try:
        # Si ya es iterable de contexts, conviértelo a lista
        return list(x)
    except TypeError:
        # No es iterable: asume un único contexto
        return [x]

class ControlFlowAnalyzer:
    """
    Reglas semánticas de control de flujo:
      - Condiciones de if/while/do-while/for/switch deben ser boolean.
      - break/continue solo dentro de bucles.
      - switch: tipos de los 'case' compatibles con el scrutinee.
    Incluye alias para adaptarse a distintas variantes de nombres de reglas
    sin modificar la gramática original.
    """

    def __init__(self, v):
        self.v = v  # VisitorCPS

    # -------------------------
    # Utilidades
    # -------------------------
    def _require_boolean(self, cond_t, ctx, who: str):
        if isinstance(cond_t, ErrorType):
            return
        if not isinstance(cond_t, BoolType):
            self.v._append_err(SemanticError(
                f"La condición de {who} debe ser boolean, no {cond_t}.",
                line=ctx.start.line, column=ctx.start.column))

    def _same_type(self, a, b):
        """
        Igualdad estricta de tipos para switch/case.
        (Sin subtipado/herencia; si en el futuro hay herencia se ajusta aquí.)
        """
        if isinstance(a, ErrorType) or isinstance(b, ErrorType):
            return True  # evitar cascada
        if type(a) is type(b):
            if isinstance(a, ClassType):
                return a.name == b.name
            if isinstance(a, ArrayType):
                return self._same_type(a.elem_type, b.elem_type)
            return True
        return False

    def _walk(self, node):
        """Recorrido DFS ligero para buscar nodos hijos."""
        try:
            for ch in node.getChildren():
                yield ch
                yield from self._walk(ch)
        except Exception:
            return

    def _collect_case_exprs(self, ctx):
        """
        Intenta recoger todas las expresiones que aparecen en 'case ...:'.
        Soporta varias formas de gramática:
          - ctx.caseBlock().caseClause().expression()
          - o buscando nodos cuyo nombre de clase contenga 'Case' y tengan expression()
        """
        exprs = []

        # Forma más común: switch() -> caseBlock -> caseClause* -> expression*
        cb = getattr(ctx, "caseBlock", None)
        if callable(cb):
            cb = cb()
        if cb:
            caseClause = getattr(cb, "caseClause", None)
            if callable(caseClause):
                for c in _as_list(caseClause()):
                    get_exprs = getattr(c, "expression", None)
                    if callable(get_exprs):
                        exprs.extend(_as_list(get_exprs()))

        # Fallback: caminar y tomar cualquier nodo 'Case*' que exponga expression()
        if not exprs:
            for n in self._walk(ctx):
                cname = n.__class__.__name__.lower()
                if "case" in cname:
                    get_exprs = getattr(n, "expression", None)
                    if callable(get_exprs):
                        exprs.extend(_as_list(get_exprs()))
        return exprs

    # -------------------------
    # if
    # -------------------------
    def visitIfStatement(self, ctx: CompiscriptParser.IfStatementContext):
        cond_t = self.v.visit(ctx.expression())
        self._require_boolean(cond_t, ctx, "if")
        if ctx.block(0): self.v.visit(ctx.block(0))
        if ctx.block(1): self.v.visit(ctx.block(1))
        return None

    # -------------------------
    # while
    # -------------------------
    def visitWhileStatement(self, ctx: CompiscriptParser.WhileStatementContext):
        cond_t = self.v.visit(ctx.expression())
        self._require_boolean(cond_t, ctx, "while")
        self.v.loop_depth += 1
        self.v.visit(ctx.block())
        self.v.loop_depth -= 1
        return None

    # -------------------------
    # do-while
    # -------------------------
    def visitDoWhileStatement(self, ctx: CompiscriptParser.DoWhileStatementContext):
        self.v.loop_depth += 1
        self.v.visit(ctx.block())
        self.v.loop_depth -= 1
        cond_t = self.v.visit(ctx.expression())
        self._require_boolean(cond_t, ctx, "do-while")
        return None

    # -------------------------
    # for
    # -------------------------
    def visitForStatement(self, ctx: CompiscriptParser.ForStatementContext):
        # init
        if getattr(ctx, "forInitializer", None) and ctx.forInitializer():
            self.v.visit(ctx.forInitializer())

        # cond (si se puede obtener)
        cond_expr = None
        if hasattr(ctx, "condition") and ctx.condition():
            cond_expr = ctx.condition()
        else:
            exprs = _as_list(getattr(ctx, "expression", lambda: None)())
            cond_expr = exprs[0] if exprs else None

        if cond_expr is not None:
            cond_t = self.v.visit(cond_expr)
            self._require_boolean(cond_t, ctx, "for")

        # update
        if getattr(ctx, "forUpdate", None) and ctx.forUpdate():
            self.v.visit(ctx.forUpdate())

        self.v.loop_depth += 1
        self.v.visit(ctx.block())
        self.v.loop_depth -= 1
        return None

    # -------------------------
    # break / continue
    # -------------------------
    def visitBreakStatement(self, ctx: CompiscriptParser.BreakStatementContext):
        if self.v.loop_depth <= 0:
            self.v._append_err(SemanticError(
                "'break' fuera de un bucle.",
                line=ctx.start.line, column=ctx.start.column))
        return None

    def visitContinueStatement(self, ctx: CompiscriptParser.ContinueStatementContext):
        if self.v.loop_depth <= 0:
            self.v._append_err(SemanticError(
                "'continue' fuera de un bucle.",
                line=ctx.start.line, column=ctx.start.column))
        return None

    # -------------------------
    # switch
    # -------------------------
    def visitSwitchStatement(self, ctx):
        """
        Validación de tipos de 'case':
          - Cada case expr debe ser del mismo tipo que el scrutinee.
        Permitimos fall-through (sin warning por ahora).
        """
        # scrutinee
        get_expr = getattr(ctx, "expression", None)
        scrutinee_ctx = None
        if callable(get_expr):
            exprs = _as_list(get_expr())
            scrutinee_ctx = exprs[0] if exprs else None
        scrutinee_t = self.v.visit(scrutinee_ctx) if scrutinee_ctx else ErrorType()

        # recolectar cases y validar
        for e in self._collect_case_exprs(ctx):
            et = self.v.visit(e)
            if isinstance(et, ErrorType) or isinstance(scrutinee_t, ErrorType):
                continue
            if not self._same_type(scrutinee_t, et):
                self.v._append_err(SemanticError(
                    f"Tipo de 'case' ({et}) incompatible con el 'switch' ({scrutinee_t}).",
                    line=e.start.line, column=e.start.column))

        # visitar el cuerpo para activar otras validaciones
        for n in self._walk(ctx):
            try:
                self.v.visit(n)
            except Exception:
                pass
        return None

    # ------ ALIAS para distintas gramáticas ------
    def visitSwitchStmt(self, ctx):      # alias común
        return self.visitSwitchStatement(ctx)

    def visitSwitch(self, ctx):          # otro alias típico
        return self.visitSwitchStatement(ctx)

    def visitCaseStatement(self, ctx):   # por si el switch se modela diferente
        return self.visitSwitchStatement(ctx)
