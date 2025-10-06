from __future__ import annotations
from antlr_gen.CompiscriptLexer import CompiscriptLexer
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

    tok = getattr(ctx, "start", None)

    # 1) Si hay token, usarlo
    if tok is not None:
        ttype = tok.type

        # Caso 1a: emite 'Literal'
        if ttype == CompiscriptLexer.Literal:
            # Distinguir por el contenido del token (seguro: es un único token)
            ttxt = tok.text or text or ""
            if ttxt.isdigit():
                return IntegerType()
            if len(ttxt) >= 2 and ttxt[0] == '"' and ttxt[-1] == '"':
                return StringType()

        if hasattr(CompiscriptLexer, "IntegerLiteral") and ttype == CompiscriptLexer.IntegerLiteral:
            return IntegerType()
        if hasattr(CompiscriptLexer, "StringLiteral") and ttype == CompiscriptLexer.StringLiteral:
            return StringType()

    # 2) Palabras clave (el parser ya las reconoce como literales)
    if text == "null":
        return NullType()
    if text == "true" or text == "false":
        return BoolType()

    # 3) Fallback por texto (cuando no hubo token útil)
    if text.isdigit():
        return IntegerType()
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        return StringType()

    # 4) Error
    line = getattr(getattr(ctx, "start", None), "line", None) if ctx else None
    column = getattr(getattr(ctx, "start", None), "column", None) if ctx else None
    error_list.append(SemanticError(
        message=f"Literal desconocido o inválido: {text}",
        line=line,
        column=column,
    ))
    return ErrorType()