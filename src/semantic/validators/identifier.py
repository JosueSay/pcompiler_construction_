from semantic.custom_types import ErrorType
from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic

def validateIdentifier(name, symbolTable, errorList, ctx=None):
    """
    Valida el uso de un identificador en una tabla plana (modo auxiliar).
    Nota: Para asignaciones y verificación completa usar ScopeManager en el Visitor.
    """
    log_semantic(f"Validating identifier: {name}")

    symbol = symbolTable.get(name)

    if not symbol:
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
