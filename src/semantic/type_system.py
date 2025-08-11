from semantic.custom_types import (
    IntegerType,
    FloatType,
    StringType,
    BoolType,
    NullType,
)

# --------------------------------------
# Tamaños de tipos básicos (bytes)
# --------------------------------------
TYPE_SIZES = {
    IntegerType: 4,
    FloatType: 8,
    BoolType: 1,
    StringType: 8,   # tratado como puntero
    NullType: 0,     # sin espacio propio
}


def getTypeWidth(typeInstance):
    """
    Retorna el tamaño en bytes de una instancia de tipo semántico.
    """
    for cls, size in TYPE_SIZES.items():
        if isinstance(typeInstance, cls):
            return size
    return 0


def isReferenceType(t):
    """
    Referencia == admite null.
    Por ahora: string. Luego: ArrayType, ClassType, etc.
    """
    return isinstance(t, StringType)
    # Ejemplo futuro:
    # or isinstance(t, ArrayType) or isinstance(t, ClassType)


def isAssignable(target_type, value_type):
    """
    Regla de asignabilidad:
      - Mismo tipo => OK
      - value_type es NullType y target es referencia => OK
      - Caso contrario => NO
    """
    if type(target_type) is type(value_type):
        return True
    if isinstance(value_type, NullType) and isReferenceType(target_type):
        return True
    return False


def resolveAnnotatedType(typeAnnotationCtx):
    """
    Convierte la anotación de tipo del parser a una instancia de tipo semántico.

    Soporte actual:
      - 'integer', 'boolean', 'string'
      - 'float' no aparece en la gramática baseType, pero se deja preparado por si se agrega
    """
    t = typeAnnotationCtx.type_().getText() if typeAnnotationCtx else None
    if t is None:
        return None

    # Normalizamos a minúsculas
    t = t.lower()

    if t == "integer":
        return IntegerType()
    if t == "boolean":
        return BoolType()
    if t == "string":
        return StringType()
    if t == "float":
        return FloatType()  # por si se habilita en la gramática

    # Futuro: arrays con '[]', identificadores de clase, etc.
    # Por ahora, no soportado:
    return None
