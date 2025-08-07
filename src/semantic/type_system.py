from semantic.custom_types import IntegerType, FloatType, StringType, BoolType, NullType

# Diccionario de tamaños por tipo básico.
# El valor representa cuántos bytes ocupa cada tipo.
# - String se trata como puntero (8 bytes).
# - NullType no ocupa espacio (0 bytes).
TYPE_SIZES = {
    IntegerType: 4,
    FloatType: 8,
    BoolType: 1,
    StringType: 8,
    NullType: 0
}

def getTypeWidth(typeInstance):
    """
    Retorna el tamaño en bytes de una instancia de tipo semántico.

    Args:
        typeInstance (Type): Instancia de tipo (ej. IntegerType(), StringType(), etc.)

    Returns:
        int: Tamaño en bytes del tipo, o 0 si no se reconoce.
    """
    for typeClass, size in TYPE_SIZES.items():
        if isinstance(typeInstance, typeClass):
            return size
    return 0  # Tipo desconocido o no mapeado
