from semantic.custom_types import (
    IntegerType,
    FloatType,
    StringType,
    BoolType,
    NullType,
    ErrorType,
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

# ------------------------------
# Predicados de categorías
# ------------------------------
def isNumeric(t):
    return isinstance(t, (IntegerType, FloatType))

def isBoolean(t):
    return isinstance(t, BoolType)

def isReferenceType(t):
    """
    Referencia == admite null.
    Por ahora: string. Luego: ArrayType, ClassType, etc.
    """
    return isinstance(t, StringType)
    # Ejemplo futuro:
    # or isinstance(t, ArrayType) or isinstance(t, ClassType)


# --------------
# Asignabilidad 
# --------------
def isAssignable(target_type, value_type):
    """
    Regla de asignabilidad:
      - Mismo tipo => OK
      - value_type es NullType y target es referencia => OK
      - Caso contrario => NO
    """
    if isinstance(value_type, ErrorType):
        return True  # evitar efecto cascada
    if type(target_type) is type(value_type):
        return True
    if isinstance(value_type, NullType) and isReferenceType(target_type):
        return True
    return False

# ------------------------------
# Reglas de resultados por operación
# ------------------------------
def resultArithmetic(t1, t2, op):
    """
    Reglas aritméticas para +, -, *, / con un pequeño casteo implícito numérico:
      - integer (+-*/) float => float
      - integer (+-*/) integer => integer
      - float   (+-*/) float   => float

    Regla especial de concatenación:
      - '+' entre string y string => string

    NOTA: la concatenación solo aplica a '+'. Cualquier otro operador con strings es inválido.
    """
    # Propagación de errores: si alguno ya es ErrorType, no cascadiemos
    from semantic.custom_types import StringType, IntegerType, FloatType, ErrorType

    if isinstance(t1, ErrorType) or isinstance(t2, ErrorType):
        return ErrorType()

    # Concatenación de strings solo con '+'
    if op == '+' and isinstance(t1, StringType) and isinstance(t2, StringType):
        return StringType()

    # Aritmética numérica
    is_num1 = isinstance(t1, (IntegerType, FloatType))
    is_num2 = isinstance(t2, (IntegerType, FloatType))
    if is_num1 and is_num2:
        if isinstance(t1, FloatType) or isinstance(t2, FloatType):
            return FloatType()
        return IntegerType()

    # Cualquier otro caso => error
    return ErrorType()

def resultModulo(t1, t2):
    """
    Regla especial de %: solo integer % integer -> integer.
    """
    if isinstance(t1, ErrorType) or isinstance(t2, ErrorType):
        return ErrorType()
    if isinstance(t1, IntegerType) and isinstance(t2, IntegerType):
        return IntegerType()
    return ErrorType()

def resultRelational(t1, t2):
    """
    <, <=, >, >= : solo entre numéricos; resultado boolean.
    """
    if isinstance(t1, ErrorType) or isinstance(t2, ErrorType):
        return ErrorType()
    if isNumeric(t1) and isNumeric(t2):
        return BoolType()
    return ErrorType()

def resultEquality(t1, t2):
    """
    ==, != : permitido si:
      - mismos tipos
      - o referencia <-> null
    Resultado boolean.
    """
    if isinstance(t1, ErrorType) or isinstance(t2, ErrorType):
        return ErrorType()
    # mismos tipos
    if type(t1) is type(t2):
        return BoolType()
    # referencia <-> null
    if (isReferenceType(t1) and isinstance(t2, NullType)) or (isReferenceType(t2) and isinstance(t1, NullType)):
        return BoolType()
    return ErrorType()

def resultLogical(t1, t2):
    """
    &&, || : ambos boolean -> boolean
    """
    if isinstance(t1, ErrorType) or isinstance(t2, ErrorType):
        return ErrorType()
    if isBoolean(t1) and isBoolean(t2):
        return BoolType()
    return ErrorType()

def resultUnaryMinus(t):
    """
    -x : x numérico -> tipo de x (integer o float).
    """
    if isinstance(t, ErrorType):
        return ErrorType()
    if isNumeric(t):
        return t
    return ErrorType()

def resultUnaryNot(t):
    """
    !x : x boolean -> boolean.
    """
    if isinstance(t, ErrorType):
        return ErrorType()
    if isBoolean(t):
        return t
    return ErrorType()


# ------------------------------
# Resolución de anotación de tipos
# ------------------------------
def resolveAnnotatedType(typeAnnotationCtx):
    """
    Convierte la anotación de tipo del parser a una instancia de tipo semántico.

    Soporte actual: 'integer', 'boolean', 'string'
    'float' no está en la gramática baseType actual, pero se deja preparado.
    """
    t = typeAnnotationCtx.type_().getText() if typeAnnotationCtx else None
    if t is None:
        return None

    t = t.lower()

    if t == "integer":
        return IntegerType()
    if t == "boolean":
        return BoolType()
    if t == "string":
        return StringType()
    if t == "float":
        return FloatType()  # si luego lo agregas a la gramática

    # Futuro: arrays con '[]', identificadores de clase, etc.
    return None