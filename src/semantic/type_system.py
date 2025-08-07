from semantic.custom_types import IntegerType, FloatType, StringType, BoolType, NullType

# Diccionario de tipos y sus tamaños
TYPE_SIZES = {
    IntegerType: 4,
    FloatType: 8,
    BoolType: 1,
    StringType: 8,  # Supongamos que es un puntero
    NullType: 0     # No ocupa espacio directamente
}

def getTypeWidth(typeInstance):
    for typeClass, size in TYPE_SIZES.items():
        if isinstance(typeInstance, typeClass):
            return size
    return 0  # Desconocido
