from semantic.custom_types import (
    IntegerType,
    FloatType,
    StringType,
    BoolType,
    NullType,
    ErrorType,
    ClassType,
    ArrayType,
)

# --------------------------------------
# Tamaños de tipos básicos (bytes)
# --------------------------------------
TYPE_SIZES = {
    IntegerType: 4,
    FloatType: 8,
    BoolType: 1,
    StringType: 8,   # tratado como puntero
    ClassType: 8,
    ArrayType: 8,
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
    Por ahora: string, class, array.
    """
    return isinstance(t, (StringType, ClassType, ArrayType))

# --------------
# Asignabilidad 
# --------------
def isAssignable(target_type, value_type):
    """
    Reglas:
      - Propagar ErrorType para no cascada.
      - null asignable a tipos de referencia (string, class, array).
      - ArrayType(T1) <- ArrayType(T2)  solo si T1 <- T2 (recursivo).
      - ClassType(A) <- ClassType(B)    solo si A == B (por ahora sin herencia).
      - Primitivos: mismo tipo exacto.
    """
    if isinstance(value_type, ErrorType):
        return True  # evitar cascada

    # null -> referencia
    if isinstance(value_type, NullType) and isReferenceType(target_type):
        return True

    # arrays: comparar elemento recursivamente
    if isinstance(target_type, ArrayType) and isinstance(value_type, ArrayType):
        return isAssignable(target_type.elem_type, value_type.elem_type)

    # clases: mismo nombre
    if isinstance(target_type, ClassType) and isinstance(value_type, ClassType):
        return target_type == value_type  # usa __eq__ por nombre

    # primitivos exactos
    return type(target_type) is type(value_type)

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

    Gramática:
      type: baseType ('[' ']')*
      baseType: 'boolean' | 'integer' | 'string' | Identifier

    Soporta arreglos anidados por conteo de '[]' en el texto,
    y clases por nombre (Identifier) como ClassType(name).
    """
    ttxt = typeAnnotationCtx.type_().getText() if typeAnnotationCtx else None
    if ttxt is None:
        return None

    # Conteo de sufijos [] (array nesting)
    dims = 0
    while ttxt.endswith("[]"):
        dims += 1
        ttxt = ttxt[:-2]

    base_txt = ttxt.strip()

    # builtins
    base = None
    if base_txt == "integer":
        base = IntegerType()
    elif base_txt == "boolean":
        base = BoolType()
    elif base_txt == "string":
        base = StringType()
    elif base_txt == "float":
        base = FloatType()
    else:
        # Si no es builtin, lo tratamos como nombre de clase (Identifier)
        # No validamos aquí existencia; eso lo hace el visitor (cuando vea usos).
        base = ClassType(base_txt)

    # Enrollar arreglos si hay dims > 0
    ty = base
    for _ in range(dims):
        ty = ArrayType(ty)
    return ty
