from semantic.custom_types import IntegerType, StringType, BoolType, NullType, ErrorType
from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic

def validateLiteral(text, errorList, ctx=None):
    """
    Determina el tipo semántico de un literal dado.

    Args:
        text (str): Representación textual del literal (ej. '42', '"hola"', 'true').
        errorList (list): Lista de errores semánticos donde se agrega si el literal no es válido.
        ctx (ParserRuleContext, opcional): Contexto para capturar línea y columna.

    Returns:
        Type: Instancia del tipo correspondiente (IntegerType, StringType, BoolType, etc.),
              o ErrorType si no se reconoce el literal.
    """
    log_semantic(f"Validating literal: {text}")

    if text.isdigit():
        return IntegerType()
    elif text.startswith('"') and text.endswith('"'):
        return StringType()
    elif text in ("true", "false"):
        return BoolType()
    elif text == "null":
        return NullType()
    else:
        line = ctx.start.line if ctx else None
        column = ctx.start.column if ctx else None
        error = SemanticError(
            message=f"Literal desconocido o inválido: {text}",
            line=line,
            column=column
        )
        log_semantic(f"ERROR: {error}")
        errorList.append(error)
        return ErrorType()
