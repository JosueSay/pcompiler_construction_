from typing import Any, List, Tuple, Iterable
from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger import logFunction
from semantic.symbol_kinds import SymbolCategory
from semantic.custom_types import (
    BoolType, IntegerType, StringType, ClassType, ArrayType,
    FunctionType, NullType
)

# ======================
# Helpers genéricos AST
# ======================

@logFunction(channel="tac")
def asList(x) -> List[Any]:
    """Convierte en lista: None -> [], secuencias iterables -> list(x), resto -> [x]."""
    if x is None:
        return []
    try:
        return list(x)
    except TypeError:
        return [x]


@logFunction(channel="tac")
def maybeCall(x: Any) -> Any:
    """Si x es callable, lo invoca; si no, devuelve x."""
    return x() if callable(x) else x


@logFunction(channel="tac")
def safeAttr(ctx: Any, name: str) -> Any:
    """getattr(ctx, name) con tolerancia a que sea callable (lo invoca)."""
    val = getattr(ctx, name, None)
    return maybeCall(val)


@logFunction(channel="tac")
def walk(node) -> Iterable[Any]:
    """DFS robusto sobre el árbol ANTLR (tolera nodos sin getChildren)."""
    try:
        for ch in node.getChildren():
            yield ch
            yield from walk(ch)
    except Exception:
        return


@logFunction(channel="tac")
def firstExpression(ctx) -> Any | None:
    """Devuelve la primera Expression por convención: ctx.expression() o primer hijo expression."""
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


@logFunction(channel="tac")
def splitAssignmentText(text: str) -> Tuple[str | None, str | None]:
    """
    Separa LHS y RHS de un texto con '=' simple, ignorando '==', '!=', '<=', '>='.
    Devuelve (lhs, rhs) o (None, None) si no hay asignación sencilla.
    """
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


@logFunction(channel="tac")
def isAssignText(text: str) -> bool:
    """True si el texto contiene una asignación simple (no comparaciones)."""
    return bool(
        text and '=' in text and
        ('==' not in text) and ('!=' not in text) and ('<=' not in text) and ('>=' not in text)
    )


@logFunction(channel="tac")
def collectStmtOrBlock(ctx) -> List[Any]:
    """
    Devuelve los statements “visibles” de un if/else/while/for/switch:
    - Primero intenta ctx.statement()
    - Luego busca StatementContext o bloques compatibles entre hijos.
    """
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


@logFunction(channel="tac")
def firstSwitchDiscriminant(ctx) -> Any | None:
    """Para switch: devuelve la primera expresión discriminante razonable."""
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


@logFunction(channel="tac")
def hasDefaultClause(ctx) -> bool:
    """Heurística para detectar si un switch tiene 'default'."""
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

@logFunction(channel="tac")
def gatherStatements(node) -> List[Any]:
    """Recolecta StatementContext dentro de un nodo (directo o por recorrido DFS)."""
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


@logFunction(channel="tac")
def firstChildExpression(node) -> Any | None:
    """Devuelve la primera Expression dentro de un nodo (útil para 'case N:')."""
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

@logFunction(channel="tac")
def extractNotInner(node):
    """
    Si encuentra un UnaryExpr con prefijo '!' devuelve su hijo interno.
    Útil para simplificar condiciones en TAC (if !E ...).
    """
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

@logFunction(channel="tac")
def setPlace(node, place: str, is_temp: bool) -> None:
    """Anota en el nodo su 'place' (texto de TAC) y si es temporal."""
    try:
        setattr(node, "_place", place)
        setattr(node, "_is_temp", is_temp)
    except Exception:
        pass  # algunos nodos podrían no admitir setattr


@logFunction(channel="tac")
def getPlace(node) -> str | None:
    """Lee el 'place' previamente anotado en el nodo (o None)."""
    return getattr(node, "_place", None)


@logFunction(channel="tac")
def isTempNode(node) -> bool:
    """True si el nodo está marcado como temporal."""
    return bool(getattr(node, "_is_temp", False))


@logFunction(channel="tac")
def freeIfTemp(node, temp_pool, kind: str = "*") -> None:
    """Libera el temporal asociado al nodo usando el TempPool proporcionado."""
    if not isTempNode(node):
        return
    name = getPlace(node)
    if not name:
        return
    try:
        temp_pool.free(name, kind)
    except Exception:
        pass  # best-effort


@logFunction(channel="tac")
def deepPlace(node) -> Tuple[str | None, bool]:
    """
    Busca hacia abajo un '_place' ya calculado (sin volver a visitar).
    Devuelve (place, is_temp). Si no encuentra, (None, False).
    """
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

@logFunction(channel="tac")
def findFunctionSymbol(scope_manager, name: str):
    """Busca un símbolo de función por nombre (simple o calificado)."""
    try:
        for sym in scope_manager.allSymbols():
            if sym.category == SymbolCategory.FUNCTION and sym.name == name:
                return sym
    except Exception:
        pass
    return None


@logFunction(channel="tac")
def lookupMethodInHierarchy(class_handler, method_registry, class_name: str, method_name: str):
    """
    Busca la firma de un método subiendo por la jerarquía de 'class_name'.
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

@logFunction(channel="tac")
def typeToTempKind(t) -> str:
    """
    Mapea un tipo semántico a la “clase” de temporal del TempPool:
      - bool    -> "bool"
      - integer -> "int"
      - string / class / array / function / null -> "ref"
      - resto   -> "*"
    """
    if isinstance(t, BoolType): return "bool"
    if isinstance(t, IntegerType): return "int"
    if isinstance(t, (StringType, ClassType, ArrayType, FunctionType, NullType)):
        return "ref"
    return "*"
