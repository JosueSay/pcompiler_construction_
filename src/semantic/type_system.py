from __future__ import annotations

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


# ---------------- Anchos (bytes) ----------------

# Tamaños de tipos básicos (en bytes). Las referencias (string/class/array) se tratan como punteros.
TYPE_SIZES: dict[type, int] = {
    IntegerType: 4,
    BoolType: 1,
    StringType: 8,   # referencia/puntero
    ClassType: 8,    # referencia/puntero
    ArrayType: 8,    # referencia/puntero
    NullType: 0,     # sin espacio propio
    VoidType: 0,     # solo válido como retorno
}


def getTypeWidth(type_instance) -> int:
    """
    Devuelve el tamaño en bytes de una **instancia** de tipo semántico.

    Notas:
    - Para referencias (string, class, array) se devuelve el tamaño del puntero.
    - `NullType` y `VoidType` ocupan 0 bytes.
    """
    for cls, size in TYPE_SIZES.items():
        if isinstance(type_instance, cls):
            return size
    return 0


# ---------------- Predicados de categoría ----------------

def isNumeric(t) -> bool:
    """Numérico (por ahora) ≡ `integer`."""
    return isinstance(t, IntegerType)


def isBoolean(t) -> bool:
    """Booleano (`true`/`false`)."""
    return isinstance(t, BoolType)


def isReferenceType(t) -> bool:
    """
    True si el tipo es de **referencia** (admite `null`):
    string, class o array.
    """
    return isinstance(t, (StringType, ClassType, ArrayType))


# ---------------- Asignabilidad ----------------

def isAssignable(target_type, value_type) -> bool:
    """
    Reglas de asignación `target_type <- value_type`.

    - Corta la cascada si `value_type` es `ErrorType` (devuelve True).
    - `null` es asignable a cualquier tipo de referencia.
    - Arrays: requieren asignabilidad recursiva de sus elementos.
    - Clases: debe coincidir el nombre (no hay subtipado estructural aquí).
    - Resto: deben ser exactamente el mismo tipo.
    """
    if isinstance(value_type, ErrorType):
        return True  # evita cascada de errores

    if isinstance(value_type, NullType) and isReferenceType(target_type):
        return True

    if isinstance(target_type, ArrayType) and isinstance(value_type, ArrayType):
        return isAssignable(target_type.elem_type, value_type.elem_type)

    if isinstance(target_type, ClassType) and isinstance(value_type, ClassType):
        # Usa __eq__ de ClassType (nombre)
        return target_type == value_type

    # Tipos básicos: igualdad estricta de clase
    return type(target_type) is type(value_type)


# ---------------- Resultados de operaciones ----------------

def resultArithmetic(t1, t2, op: str):
    """
    Resultado de operaciones aritméticas/suma.

    Reglas:
    - `string + string` → `string` (concatenación).
    - `integer (+,-,*,/) integer` → `integer`.
    - Cualquier otro caso → `ErrorType`.
    """
    if isinstance(t1, ErrorType) or isinstance(t2, ErrorType):
        return ErrorType()

    if op == '+' and isinstance(t1, StringType) and isinstance(t2, StringType):
        return StringType()

    if isinstance(t1, IntegerType) and isinstance(t2, IntegerType):
        return IntegerType()

    return ErrorType()


def resultModulo(t1, t2):
    """Resultado de `t1 % t2`: solo definido para `integer % integer`."""
    if isinstance(t1, ErrorType) or isinstance(t2, ErrorType):
        return ErrorType()
    if isinstance(t1, IntegerType) and isinstance(t2, IntegerType):
        return IntegerType()
    return ErrorType()


def resultRelational(t1, t2):
    """
    Resultado de relacionales (`<`, `>`, `<=`, `>=`):
    requiere numéricos a ambos lados → `boolean`.
    """
    if isinstance(t1, ErrorType) or isinstance(t2, ErrorType):
        return ErrorType()
    if isNumeric(t1) and isNumeric(t2):
        return BoolType()
    return ErrorType()


def resultEquality(t1, t2):
    """
    Resultado de igualdad/desigualdad (`==`, `!=`):
    - Mismo tipo → `boolean`.
    - `ref == null` o `null == ref` → `boolean`.
    - Otro caso → `ErrorType`.
    """
    if isinstance(t1, ErrorType) or isinstance(t2, ErrorType):
        return ErrorType()
    if type(t1) is type(t2):
        return BoolType()
    if (isReferenceType(t1) and isinstance(t2, NullType)) or (isReferenceType(t2) and isinstance(t1, NullType)):
        return BoolType()
    return ErrorType()


def resultLogical(t1, t2):
    """Resultado de `&&` / `||`: requiere booleanos → `boolean`."""
    if isinstance(t1, ErrorType) or isinstance(t2, ErrorType):
        return ErrorType()
    if isBoolean(t1) and isBoolean(t2):
        return BoolType()
    return ErrorType()


def resultUnaryMinus(t):
    """Resultado de `-x`: solo para numéricos (integer)."""
    if isinstance(t, ErrorType):
        return ErrorType()
    if isNumeric(t):
        return t
    return ErrorType()


def resultUnaryNot(t):
    """Resultado de `!x`: solo para `boolean`."""
    if isinstance(t, ErrorType):
        return ErrorType()
    if isBoolean(t):
        return t
    return ErrorType()


# ---------------- Resolución de anotaciones ----------------

def resolveAnnotatedType(type_annotation_ctx):
    """
    Convierte una anotación de tipo del parser a una **instancia** de tipo semántico.

    Soporta sufijos `[]` (arrays) sobre:
      - `integer`, `boolean`, `string`, `void`
      - identificadores de clase (se crean como `ClassType(name)`)

    Ejemplos:
      "integer"      -> IntegerType()
      "string[]"     -> ArrayType(StringType())
      "Foo[][]"      -> ArrayType(ArrayType(ClassType("Foo")))
      "void"         -> VoidType()
    """
    ttxt = type_annotation_ctx.type_().getText() if type_annotation_ctx else None
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
        # No hay float aquí: identificadores desconocidos se tratan como clases
        base = ClassType(base_txt)

    ty = base
    for _ in range(dims):
        ty = ArrayType(ty)
    return ty
