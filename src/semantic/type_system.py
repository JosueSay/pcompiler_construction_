from semantic.custom_types import (
    IntegerType,
    StringType,
    BoolType,
    NullType,
    ErrorType,
    ClassType,
    ArrayType,
    VoidType,
)

# Tamaños de tipos básicos (bytes)
TYPE_SIZES = {
    IntegerType: 4,
    BoolType: 1,
    StringType: 8,   # tratado como puntero
    ClassType: 8,
    ArrayType: 8,
    NullType: 0,     # sin espacio propio
    VoidType: 0,
}

def getTypeWidth(typeInstance):
    """Retorna el tamaño en bytes de una instancia de tipo semántico."""
    for cls, size in TYPE_SIZES.items():
        if isinstance(typeInstance, cls):
            return size
    return 0

# Predicados de categorías
def isNumeric(t): 
    # sin float: numérico == integer
    return isinstance(t, IntegerType)

def isBoolean(t): 
    return isinstance(t, BoolType)

def isReferenceType(t):
    """Referencia == admite null. Por ahora: string, class, array."""
    return isinstance(t, (StringType, ClassType, ArrayType))

# Asignabilidad
def isAssignable(target_type, value_type):
    if isinstance(value_type, ErrorType):
        return True  # evitar cascada

    if isinstance(value_type, NullType) and isReferenceType(target_type):
        return True

    if isinstance(target_type, ArrayType) and isinstance(value_type, ArrayType):
        return isAssignable(target_type.elem_type, value_type.elem_type)

    if isinstance(target_type, ClassType) and isinstance(value_type, ClassType):
        return target_type == value_type  # usa __eq__ por nombre

    return type(target_type) is type(value_type)

# Reglas de resultados por operación (solo integer/string)
def resultArithmetic(t1, t2, op):
    if isinstance(t1, ErrorType) or isinstance(t2, ErrorType):
        return ErrorType()

    # concatenación de strings con '+'
    if op == '+' and isinstance(t1, StringType) and isinstance(t2, StringType):
        return StringType()

    # aritmética entera
    if isinstance(t1, IntegerType) and isinstance(t2, IntegerType):
        return IntegerType()

    return ErrorType()

def resultModulo(t1, t2):
    if isinstance(t1, ErrorType) or isinstance(t2, ErrorType):
        return ErrorType()
    if isinstance(t1, IntegerType) and isinstance(t2, IntegerType):
        return IntegerType()
    return ErrorType()

def resultRelational(t1, t2):
    if isinstance(t1, ErrorType) or isinstance(t2, ErrorType):
        return ErrorType()
    if isNumeric(t1) and isNumeric(t2):
        return BoolType()
    return ErrorType()

def resultEquality(t1, t2):
    if isinstance(t1, ErrorType) or isinstance(t2, ErrorType):
        return ErrorType()
    if type(t1) is type(t2):
        return BoolType()
    if (isReferenceType(t1) and isinstance(t2, NullType)) or (isReferenceType(t2) and isinstance(t1, NullType)):
        return BoolType()
    return ErrorType()

def resultLogical(t1, t2):
    if isinstance(t1, ErrorType) or isinstance(t2, ErrorType):
        return ErrorType()
    if isBoolean(t1) and isBoolean(t2):
        return BoolType()
    return ErrorType()

def resultUnaryMinus(t):
    if isinstance(t, ErrorType):
        return ErrorType()
    if isNumeric(t):   # ahora solo integer
        return t
    return ErrorType()

def resultUnaryNot(t):
    if isinstance(t, ErrorType):
        return ErrorType()
    if isBoolean(t):
        return t
    return ErrorType()

# Resolución de anotación de tipos
def resolveAnnotatedType(typeAnnotationCtx):
    """
    Convierte la anotación de tipo del parser a una instancia de tipo semántico.
    """
    ttxt = typeAnnotationCtx.type_().getText() if typeAnnotationCtx else None
    if ttxt is None:
        return None

    dims = 0
    while ttxt.endswith("[]"):
        dims += 1
        ttxt = ttxt[:-2]

    base_txt = ttxt.strip()

    if base_txt == "integer":
        base = IntegerType()
    elif base_txt == "boolean":
        base = BoolType()
    elif base_txt == "string":
        base = StringType()
    elif base_txt == "void":
        base = VoidType()
    else:
        # 'float' ya NO se reconoce como primitivo; caerá como ClassType
        base = ClassType(base_txt)

    ty = base
    for _ in range(dims):
        ty = ArrayType(ty)
    return ty
