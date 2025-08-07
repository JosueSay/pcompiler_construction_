from semantic.custom_types import ErrorType

def validateIdentifier(name, symbolTable, errorList):
    # En el futuro, buscar en la tabla de símbolos
    errorList.append(f"Uso de variable no declarada: '{name}'")
    return ErrorType()
