class SymbolCategory:
    """
    Enum simulada para categorizar los símbolos utilizados en la tabla de símbolos.

    Usado para diferenciar entre tipos de símbolos como variables, constantes,
    funciones y parámetros. Esto permite aplicar reglas semánticas específicas
    dependiendo del tipo.
    """

    VARIABLE = "variable"    # Declaración de variable común
    CONSTANT = "constant"    # Valor constante, no modificable
    FUNCTION = "function"    # Declaración de función
    PARAMETER = "parameter"  # Parámetro formal dentro de funciones
