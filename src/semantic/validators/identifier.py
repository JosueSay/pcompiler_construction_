from semantic.custom_types import ErrorType
from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic

def validateIdentifier(name, symbolTable, errorList, ctx=None):
    """
    Valida el uso de un identificador (variable) en la tabla de símbolos actual.

    Args:
        name (str): Nombre del identificador a validar.
        symbolTable (dict): Tabla de símbolos del entorno actual.
        errorList (list): Lista donde se agregan errores semánticos detectados.
        ctx (ParserRuleContext, opcional): Contexto para extraer ubicación del error.

    Returns:
        Type: Tipo del símbolo si existe, o ErrorType si no está declarado.
    """
    log_semantic(f"Validating identifier: {name}")

    symbol = symbolTable.get(name)

    if not symbol:
        # Extraer línea y columna si se proporciona el contexto
        line = ctx.start.line if ctx else None
        column = ctx.start.column if ctx else None
        error = SemanticError(
            message=f"Uso de variable no declarada: '{name}'",
            line=line,
            column=column
        )
        log_semantic(f"ERROR: {error}")
        errorList.append(error)
        return ErrorType()

    log_semantic(f"Identifier '{name}' resolved with type: {symbol.type}")
    return symbol.type
