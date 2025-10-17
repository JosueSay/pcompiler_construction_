from typing import Any, List, Tuple, Iterable
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.symbol_kinds import SymbolCategory
from semantic.custom_types import (
    BoolType, IntegerType, StringType, ClassType, ArrayType,
    FunctionType, NullType
)

# ======================
# Helpers genéricos AST
# ======================

def asList(x) -> List[Any]:
    """
    Convierte cualquier valor en lista.
    - None → []
    - Iterable → list(x)
    - Otro valor → [x]
    """
    if x is None:
        return []
    try:
        return list(x)
    except TypeError:
        return [x]


def maybeCall(x: Any) -> Any:
    """
    Si x es invocable (callable), lo ejecuta.
    Si no, lo devuelve tal cual.
    """
    return x() if callable(x) else x


def safeAttr(ctx: Any, name: str) -> Any:
    """
    getattr(ctx, name) pero tolerante:
    - Si el atributo es callable → lo invoca.
    - Si no existe → devuelve None.
    """
    val = getattr(ctx, name, None)
    return maybeCall(val)


def walk(node) -> Iterable[Any]:
    """
    Recorrido DFS robusto sobre el árbol ANTLR.
    Tolera nodos sin método getChildren().
    """
    try:
        for ch in node.getChildren():
            yield ch
            yield from walk(ch)
    except Exception:
        return


def firstExpression(ctx) -> Any | None:
    """
    Devuelve la primera expresión encontrada en un contexto.
    Heurística usada para if/while/switch donde puede estar anidada.
    """
    e = safeAttr(ctx, "expression")
    if e is not None:
        return e
    try:
        for i in range(ctx.getChildCount()):
            ch = ctx.getChild(i)
            if isinstance(ch, CompiscriptParser.ExpressionContext):
                return ch
            for j in range(ch.getChildCount()):
                gd = ch.getChild(j)
                if isinstance(gd, CompiscriptParser.ExpressionContext):
                    return gd
    except Exception:
        pass
    return None


def splitAssignmentText(text: str) -> Tuple[str | None, str | None]:
    """
    Dado un texto con '=', separa LHS y RHS si es asignación simple.
    Ignora '==', '!=', '<=', '>='.
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


def isAssignText(text: str) -> bool:
    """True si el texto contiene una asignación simple (no comparaciones)."""
    return bool(
        text and '=' in text and
        ('==' not in text) and ('!=' not in text) and ('<=' not in text) and ('>=' not in text)
    )


def collectStmtOrBlock(ctx) -> List[Any]:
    """
    Extrae los statements de un nodo compuesto (if/else/while/for/switch).
    - Busca primero ctx.statement()
    - Luego busca StatementContext o bloques equivalentes.
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


def firstSwitchDiscriminant(ctx) -> Any | None:
    """Devuelve la primera expresión discriminante en un switch."""
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


def hasDefaultClause(ctx) -> bool:
    """True si el switch tiene una cláusula 'default'."""
    try:
        dc = getattr(ctx, "defaultCase", None)
        if callable(dc) and dc() is not None:
            return True
    except Exception:
        pass
    Default = getattr(CompiscriptParser, "DefaultCaseContext", None)
    if Default:
        try:
            for ch in ctx.getChildren():
                if isinstance(ch, Default):
                    return True
        except Exception:
            pass
    return False


def gatherStatements(node) -> List[Any]:
    """Recolecta todos los StatementContext dentro de un nodo (directo o DFS)."""
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


def firstChildExpression(node) -> Any | None:
    """Devuelve la primera expresión encontrada en un nodo (ej: case N:)."""
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


def extractNotInner(node):
    """
    Busca expresiones tipo '!E' y devuelve 'E' (interno).
    Útil para simplificar condiciones en TAC.
    """
    try:
        if type(node).__name__ in ("UnaryExprContext", "UnaryExpressionContext"):
            if node.getChildCount() >= 2 and node.getChild(0).getText() == "!":
                return node.getChild(1)
        for ch in walk(node):
            if type(ch).__name__ in ("UnaryExprContext", "UnaryExpressionContext"):
                if ch.getChildCount() >= 2 and ch.getChild(0).getText() == "!":
                    return ch.getChild(1)
    except Exception:
        pass
    return None


def setPlace(node, place: str, is_temp: bool) -> None:
    """Anota en el nodo su 'place' (nombre TAC) y si es temporal."""
    try:
        setattr(node, "_place", place)
        setattr(node, "_is_temp", is_temp)
    except Exception:
        pass


def getPlace(node) -> str | None:
    """Devuelve el 'place' anotado en el nodo, o None si no existe."""
    return getattr(node, "_place", None)


def isTempNode(node) -> bool:
    """True si el nodo está marcado como temporal."""
    return bool(getattr(node, "_is_temp", False))


def freeIfTemp(node, temp_pool, kind: str = "*") -> bool:
    """
    Libera el temporal asociado al nodo (si existe).
    Devuelve:
      - True  si efectivamente liberó un temporal
      - False si no había temporal o si falló la liberación
    """
    if not isTempNode(node):
        return False
    name = getPlace(node)
    if not name:
        return False
    try:
        temp_pool.free(name, kind)
        return True
    except Exception:
        return False


def deepPlace(node) -> Tuple[str | None, bool]:
    """
    Busca hacia abajo un '_place' ya calculado.
    Devuelve (place, is_temp) o (None, False).
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


def findFunctionSymbol(scope_manager, name: str):
    """Busca un símbolo de función por nombre en el scope manager."""
    try:
        for sym in scope_manager.allSymbols():
            if sym.category == SymbolCategory.FUNCTION and sym.name == name:
                return sym
    except Exception:
        pass
    return None


def lookupMethodInHierarchy(class_handler, method_registry, class_name: str, method_name: str):
    """
    Busca un método en la jerarquía de clases.
    Devuelve (owner_class, signature) o (None, None).
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


def typeToTempKind(t) -> str:
    """
    Mapea un tipo semántico a la clase de temporal del TempPool:
      - bool    → "bool"
      - integer → "int"
      - string/class/array/function/null → "ref"
      - otro    → "*"
    """
    if isinstance(t, BoolType): return "bool"
    if isinstance(t, IntegerType): return "int"
    if isinstance(t, (StringType, ClassType, ArrayType, FunctionType, NullType)):
        return "ref"
    return "*"
