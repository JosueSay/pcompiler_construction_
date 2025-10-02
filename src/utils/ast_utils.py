from typing import Any, List, Tuple, Iterable
from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger_semantic import log_function
from semantic.symbol_kinds import SymbolCategory
from semantic.custom_types import (
    BoolType, IntegerType, StringType, ClassType, ArrayType,
    FunctionType, NullType, VoidType, ErrorType
)

# ======================
# Helpers genéricos AST
# ======================

@log_function
def asList(x) -> List[Any]:
    if x is None:
        return []
    try:
        return list(x)
    except TypeError:
        return [x]


@log_function
def maybeCall(x: Any) -> Any:
    return x() if callable(x) else x


@log_function
def safeAttr(ctx: Any, name: str) -> Any:
    val = getattr(ctx, name, None)
    return maybeCall(val)


@log_function
def walk(node) -> Iterable[Any]:
    """Recorrido DFS robusto sobre el árbol ANTLR."""
    try:
        for ch in node.getChildren():
            yield ch
            yield from walk(ch)
    except Exception:
        return


@log_function
def firstExpression(ctx) -> Any | None:
    e = safeAttr(ctx, "expression")
    if e is not None:
        return e
    try:
        for i in range(ctx.getChildCount()):
            ch = ctx.getChild(i)
            if isinstance(ch, CompiscriptParser.ExpressionContext):
                return ch
            try:
                for j in range(ch.getChildCount()):
                    gd = ch.getChild(j)
                    if isinstance(gd, CompiscriptParser.ExpressionContext):
                        return gd
            except Exception:
                continue
    except Exception:
        pass
    return None


@log_function
def splitAssignmentText(text: str) -> Tuple[str | None, str | None]:
    if not text:
        return None, None
    for i, ch in enumerate(text):
        if ch != '=':
            continue
        prevc = text[i - 1] if i > 0 else ''
        nextc = text[i + 1] if i + 1 < len(text) else ''
        if prevc in ('=', '!', '<', '>') or nextc == '=':
            continue
        lhs = text[:i].strip()
        rhs = text[i + 1:].strip()
        return (lhs or None, rhs or None)
    return None, None


@log_function
def isAssignText(text: str) -> bool:
    return bool(
        text and '=' in text and
        ('==' not in text) and ('!=' not in text) and ('<=' not in text) and ('>=' not in text)
    )


@log_function
def collectStmtOrBlock(ctx) -> List[Any]:
    stmts = asList(safeAttr(ctx, "statement"))
    if stmts:
        return stmts

    out: list[Any] = []
    block_ctx = getattr(CompiscriptParser, "BlockContext", None)
    try:
        for i in range(ctx.getChildCount()):
            ch = ctx.getChild(i)
            if isinstance(ch, CompiscriptParser.StatementContext):
                out.append(ch)
            elif block_ctx is not None and isinstance(ch, block_ctx):
                out.append(ch)
            elif type(ch).__name__.endswith("BlockContext"):
                out.append(ch)
    except Exception:
        pass
    return out


@log_function
def firstSwitchDiscriminant(ctx) -> Any | None:
    e = safeAttr(ctx, "expression")
    if e is None:
        return firstExpression(ctx)
    try:
        seq = list(e)
        if seq:
            return seq[0]
    except TypeError:
        pass
    return firstExpression(ctx)


@log_function
def hasDefaultClause(ctx) -> bool:
    default_ctx = getattr(CompiscriptParser, "DefaultClauseContext", None)
    try:
        for i in range(ctx.getChildCount()):
            ch = ctx.getChild(i)
            if default_ctx is not None and isinstance(ch, default_ctx):
                return True
            if type(ch).__name__.lower().startswith("default") and type(ch).__name__.endswith("Context"):
                return True
    except Exception:
        pass
    try:
        txt = ctx.getText()
        if "default" in txt:
            return True
    except Exception:
        pass
    return False


# ======================
# Switch helpers comunes
# ======================

@log_function
def gatherStatements(node) -> List[Any]:
    """Devuelve StatementContext dentro de node (directo o por recorrido)."""
    out: List[Any] = []
    if node is None:
        return out
    stmts = asList(safeAttr(node, "statement"))
    if stmts:
        return stmts
    try:
        for ch in walk(node):
            if isinstance(ch, CompiscriptParser.StatementContext):
                out.append(ch)
    except Exception:
        pass
    return out


@log_function
def firstChildExpression(node) -> Any | None:
    """Primera Expression dentro de node (útil para 'case N:')."""
    if node is None:
        return None
    e = safeAttr(node, "expression")
    if e is not None:
        try:
            seq = list(e)
            if seq:
                return seq[0]
        except TypeError:
            return e
    try:
        for ch in walk(node):
            if isinstance(ch, CompiscriptParser.ExpressionContext):
                return ch
    except Exception:
        pass
    return None


# ======================
# Control de flujo utils
# ======================

@log_function
def extractNotInner(node):
    """Si hay un UnaryExpr con '!' devuelve su hijo interno; si no, None."""
    try:
        if type(node).__name__ in ("UnaryExprContext", "UnaryExpressionContext"):
            if node.getChildCount() >= 2 and node.getChild(0).getText() == "!":
                return node.getChild(1)
        for ch in walk(node):
            if type(ch).__name__ in ("UnaryExprContext", "UnaryExpressionContext"):
                try:
                    if ch.getChildCount() >= 2 and ch.getChild(0).getText() == "!":
                        return ch.getChild(1)
                except Exception:
                    pass
    except Exception:
        pass
    return None


# =====================================
# Utils de place/temporales en nodos AST
# =====================================

@log_function
def setPlace(node, place: str, is_temp: bool) -> None:
    """Guarda en el nodo su 'place' y si es temporal."""
    try:
        setattr(node, "_place", place)
        setattr(node, "_is_temp", is_temp)
    except Exception:
        # si el nodo no admite setattr, simplemente ignorar
        pass


@log_function
def getPlace(node) -> str | None:
    return getattr(node, "_place", None)


@log_function
def isTempNode(node) -> bool:
    return bool(getattr(node, "_is_temp", False))


@log_function
def freeIfTemp(node, temp_pool, kind: str = "*") -> None:
    """Libera el temporal asociado al nodo usando temp_pool."""
    if not isTempNode(node):
        return
    name = getPlace(node)
    if not name:
        return
    try:
        temp_pool.free(name, kind)
    except Exception:
        # liberación best-effort
        pass


@log_function
def deepPlace(node) -> Tuple[str | None, bool]:
    """Busca recursivamente un _place ya calculado en hijos (sin volver a visitar)."""
    if node is None:
        return None, False
    p = getattr(node, "_place", None)
    if p is not None:
        return p, bool(getattr(node, "_is_temp", False))
    try:
        n = node.getChildCount()
    except Exception:
        n = 0
    for i in range(n or 0):
        ch = node.getChild(i)
        p2, it2 = deepPlace(ch)
        if p2 is not None:
            return p2, it2
    return None, False


# ======================
# Símbolos / métodos
# ======================

@log_function
def findFunctionSymbol(scope_manager, name: str):
    """Busca un símbolo de función (nombre simple o calificado)."""
    try:
        for sym in scope_manager.allSymbols():
            if sym.category == SymbolCategory.FUNCTION and sym.name == name:
                return sym
    except Exception:
        pass
    return None


@log_function
def lookupMethodInHierarchy(class_handler, method_registry, class_name: str, method_name: str):
    """
    Busca una firma de método subiendo por la jerarquía de 'class_name'.
    Devuelve (owner, signature) o (None, None).
    """
    try:
        sig = method_registry.lookupMethod(f"{class_name}.{method_name}")
        if sig is not None:
            return class_name, sig
        seen = set()
        curr = class_name
        while curr and curr not in seen:
            seen.add(curr)
            meta = getattr(class_handler, "_classes", {}).get(curr)
            base = getattr(meta, "base", None) if meta is not None else None
            if not base:
                break
            sig = method_registry.lookupMethod(f"{base}.{method_name}")
            if sig is not None:
                return base, sig
            curr = base
    except Exception:
        pass
    return None, None


# ======================
# Tipos → clase temporal
# ======================

@log_function
def typeToTempKind(t) -> str:
    """Convierte un tipo semántico en clase de temporal del temp_pool."""
    if isinstance(t, BoolType): return "bool"
    if isinstance(t, IntegerType): return "int"
    if isinstance(t, (StringType, ClassType, ArrayType, FunctionType, NullType)):
        return "ref"
    # por defecto, comodín
    return "*"


@log_function
def newTempFor(temp_pool, t) -> str:
    """Crea un temporal en temp_pool apropiado para el tipo t."""
    return temp_pool.newTemp(typeToTempKind(t))


def newTemp(*, kind="*", pool=None, v=None):
    """
    Crea un temporal. Debes pasar 'pool=' o 'v='.
    Ejemplos:
      newTemp(kind="ref", pool=self.v.emitter.temp_pool)
      newTemp(kind="int",  v=self.v)
    """
    if pool is None and v is not None:
        pool = getattr(getattr(v, "emitter", None), "temp_pool", None)
    if pool is None:
        raise RuntimeError("newTemp requiere 'pool=' o 'v=' (no llames newTemp(\"*\"))")
    return pool.newTemp(kind)