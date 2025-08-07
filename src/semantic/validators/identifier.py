from semantic.custom_types import ErrorType
from logs.logger_semantic import log_semantic

def validateIdentifier(name, symbolTable, errorList):
    """
    Valida el uso de un identificador (variable) en la tabla de símbolos actual.

    Args:
        name (str): Nombre del identificador a validar.
        symbolTable (dict): Tabla de símbolos del entorno actual.
        errorList (list): Lista donde se agregan errores semánticos detectados.

    Returns:
        Type: Tipo del símbolo si existe, o ErrorType si no está declarado.
    """
    log_semantic(f"Validating identifier: {name}")

    symbol = symbolTable.get(name)

    if not symbol:
        error_msg = f"Uso de variable no declarada: '{name}'"
        log_semantic(f"ERROR: {error_msg}")
        errorList.append(error_msg)
        return ErrorType()

    log_semantic(f"Identifier '{name}' resolved with type: {symbol.type}")
    return symbol.type
