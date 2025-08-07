from semantic.custom_types import ErrorType
from logs.logger_semantic import log_semantic

def validateIdentifier(name, symbolTable, errorList):
    log_semantic(f"Validating identifier: {name}")
    symbol = symbolTable.get(name)
    if not symbol:
        error_msg = f"Uso de variable no declarada: '{name}'"
        log_semantic(f"ERROR: {error_msg}")
        errorList.append(error_msg)
        return ErrorType()
    log_semantic(f"Identifier '{name}' resolved with type: {symbol.type}")
    return symbol.type
