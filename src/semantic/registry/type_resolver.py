from typing import Any
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import IntegerType, StringType, BoolType, VoidType, ClassType, ArrayType
from semantic.errors import SemanticError
from logs.logger import log, logFunction


@logFunction
def unwrapTypeCtx(type_ctx: Any) -> Any | None:
    """
    Normaliza un nodo de tipo del parser:
    acepta `TypeAnnotationContext` o `TypeContext` y devuelve siempre un `TypeContext`.
    """
    if type_ctx is None:
        return None

    # Caso 1: viene como TypeAnnotationContext -> tomar su type_()
    try:
        if isinstance(type_ctx, CompiscriptParser.TypeAnnotationContext):
            return type_ctx.type_()
    except Exception:
        pass

    # Caso 2: objeto con método type_() que devuelve el TypeContext
    try:
        getter = getattr(type_ctx, "type_", None)
        if callable(getter):
            inner = getter()
            if inner is not None:
                return inner
    except Exception:
        pass

    # Caso 3: ya es el TypeContext
    return type_ctx


@logFunction
def baseText(tctx: Any) -> str:
    """
    Extrae el texto del tipo base (sin sufijos `[]`) a partir de un `TypeContext`.
    Intenta primero la subregla `baseType()`, luego `Identifier()`,
    y por último hace un corte textual por '['.
    """
    if tctx is None:
        return ""

    # Camino feliz: regla baseType()
    try:
        getb = getattr(tctx, "baseType", None)
        if callable(getb):
            b = getb()
            if b is not None:
                return b.getText()
    except Exception:
        pass

    # Fallback: intentar con Identifier() si existe
    try:
        if hasattr(tctx, "Identifier") and callable(tctx.Identifier):
            ids = tctx.Identifier()
            if isinstance(ids, list) and ids:
                return ids[0].getText()
            if ids is not None:
                return ids.getText()
    except Exception:
        pass

    # Fallback final: cortar por '[' del texto completo
    try:
        txt = tctx.getText() or ""
        return txt.split('[')[0] if '[' in txt else txt
    except Exception:
        return ""


@logFunction
def countArrayDims(tctx: Any) -> int:
    """
    Cuenta pares '[]' en el `TypeContext`.
    Prefiere recorrer la estructura; si falla, recurre al conteo textual.
    """
    if tctx is None:
        return 0

    # Intento estructural
    dims = 0
    try:
        n = tctx.getChildCount()
    except Exception:
        n = 0

    i = 0
    while i + 1 < n:
        try:
            c0 = tctx.getChild(i).getText()
            c1 = tctx.getChild(i + 1).getText()
            if c0 == '[' and c1 == ']':
                dims += 1
                i += 2
                continue
        except Exception:
            pass
        i += 1

    if dims > 0:
        return dims

    # Fallback textual
    try:
        txt = tctx.getText() or ""
        return txt.count("[]") if "[]" in txt else txt.count('[')
    except Exception:
        return 0


@logFunction
def resolveTypeCtx(type_ctx: Any) -> Any | None:
    """
    Convierte un `TypeAnnotationContext`/`TypeContext` en un tipo semántico.
    Soporta sufijos de arreglo `[]` (p.ej. `Integer[][]`).
    """
    tctx = unwrapTypeCtx(type_ctx)
    if tctx is None:
        return None

    base_txt = (baseText(tctx) or "").strip()
    lowered = base_txt.lower()

    if lowered == "integer":
        t = IntegerType()
    elif lowered == "string":
        t = StringType()
    elif lowered == "boolean":
        t = BoolType()
    elif lowered == "void":
        t = VoidType()
    else:
        # Identificador de clase
        t = ClassType(base_txt)

    dims = countArrayDims(tctx)
    for _ in range(dims):
        t = ArrayType(t)

    return t


@logFunction
def validateKnownTypes(t: Any, known_classes: set[str], ctx: Any, where: str, errors_list: list[SemanticError] | None = None) -> bool:
    """
    Reglas mínimas de sanidad:
      - No permitir arreglos de `void`.
      - Si el tipo base es `ClassType`, debe existir en `known_classes`.

    Devuelve True si el tipo es válido; False si se registró un error.
    """
    base = t
    has_array = False
    while isinstance(base, ArrayType):
        has_array = True
        base = base.elem_type

    # void[] está prohibido
    if isinstance(base, VoidType) and has_array:
        err = SemanticError(
            f"Arreglo de 'void' no permitido usado en {where}.",
            line=ctx.start.line, column=ctx.start.column
        )
        if errors_list is not None:
            errors_list.append(err)
        log(f"ERROR: {err}", channel="semantic")
        return False

    # 'void' a secas es válido (p.ej. retorno)
    if isinstance(base, VoidType):
        return True

    # ClassType debe existir
    if isinstance(base, ClassType) and base.name not in known_classes:
        err = SemanticError(
            f"Tipo de clase no declarado: '{base.name}' usado en {where}.",
            line=ctx.start.line, column=ctx.start.column
        )
        if errors_list is not None:
            errors_list.append(err)
        log(f"ERROR: {err}", channel="semantic")
        return False

    return True
