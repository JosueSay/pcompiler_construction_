from semantic.custom_types import IntegerType, StringType, BoolType, NullType, ErrorType
from logs.logger_semantic import log_semantic

def validateLiteral(text, errorList):
    """
    Determina el tipo semántico de un literal dado.

    Args:
        text (str): Representación textual del literal (ej. '42', '"hola"', 'true').
        errorList (list): Lista de errores semánticos donde se agrega si el literal no es válido.

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
        error = f"Unknown literal type: {text}"
        log_semantic(f"ERROR: {error}")
        errorList.append(error)
        return ErrorType()
