from semantic.custom_types import ErrorType
from logs.logger_semantic import log_semantic

def validateIdentifier(name, symbolTable, errorList):
    log_semantic(f"Validating identifier: {name}")
    if name not in symbolTable:
        error_msg = f"Uso de variable no declarada: '{name}'"
        log_semantic(f"ERROR: {error_msg}")
        errorList.append(error_msg)
        return ErrorType()
