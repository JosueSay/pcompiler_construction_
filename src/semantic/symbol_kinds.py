class SymbolCategory:
    """
    Categorías de símbolos usadas por la tabla de símbolos en la fase semántica.

    Usamos strings simples (no Enum) para facilitar comparaciones y serialización:
    `sym.category == SymbolCategory.VARIABLE`.
    """
    VARIABLE = "variable"   # Variable mutable declarada por el usuario
    CONSTANT = "constant"   # Constante (inmutable tras inicialización)
    FUNCTION = "function"   # Función o método (introduce subámbito y firma)
    PARAMETER = "parameter" # Parámetro formal de función/método
