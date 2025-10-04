from __future__ import annotations

from typing import Any
from semantic.custom_types import IntegerType, StringType, BoolType, NullType, ErrorType
from semantic.errors import SemanticError
from logs.logger import log, logFunction


@logFunction
def validateLiteral(text: str, error_list: list[SemanticError], ctx: Any | None = None):
    """
    Determina el tipo semántico de un literal a partir de su texto.

    Reglas (simples y predecibles):
      - Dígitos puros (p.ej., "123") → IntegerType
      - Comillas dobles al inicio y fin → StringType
      - "true" o "false" → BoolType
      - "null" → NullType
      - Cualquier otro caso se considera inválido y genera un SemanticError.

    Notas:
      - Un negativo como "-3" suele tratarse como operador unario + literal "3"
        en el árbol; aquí, por convenio, no se acepta como literal numérico.
      - La validación de escapes o formatos avanzados de string no se hace aquí.

    Parámetros:
      - text: representación textual del literal en el código fuente.
      - error_list: lista acumulativa donde se agregan errores semánticos.
      - ctx: (opcional) nodo del parser para extraer línea/columna.

    Retorna:
      - Una instancia de tipo semántico (IntegerType, StringType, BoolType, NullType)
        o ErrorType si el literal no es válido.
    """
    log(f"Validating literal: {text}", channel="semantic")

    if text.isdigit():
        return IntegerType()
    if text.startswith('"') and text.endswith('"'):
        return StringType()
    if text in ("true", "false"):
        return BoolType()
    if text == "null":
        return NullType()

    line = getattr(getattr(ctx, "start", None), "line", None) if ctx else None
    column = getattr(getattr(ctx, "start", None), "column", None) if ctx else None
    error = SemanticError(
        message=f"Literal desconocido o inválido: {text}",
        line=line,
        column=column,
    )
    log(f"ERROR: {error}", channel="semantic")
    error_list.append(error)
    return ErrorType()
