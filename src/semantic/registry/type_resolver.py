from semantic.custom_types import IntegerType, StringType, BoolType, VoidType, ClassType, ArrayType
from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic

def resolveTypeCtx(type_ctx):
    if type_ctx is None:
        return None

    base_txt = type_ctx.baseType().getText()

    if base_txt == "integer":
        t = IntegerType()
    elif base_txt == "string":
        t = StringType()
    elif base_txt == "boolean":
        t = BoolType()
    elif base_txt == "void":
        t = VoidType()
    else:
        t = ClassType(base_txt)

    dims = (type_ctx.getChildCount() - 1) // 2
    for _ in range(dims):
        t = ArrayType(t)
    return t

def validateKnownTypes(t, known_classes, ctx, where: str, errors_list=None):
    base = t
    has_array = False
    while isinstance(base, ArrayType):
        has_array = True
        base = base.elem_type

    if isinstance(base, VoidType) and has_array:
        err = SemanticError(f"Arreglo de 'void' no permitido usado en {where}.",
                            line=ctx.start.line, column=ctx.start.column)
        (errors_list or []).append(err)
        log_semantic(f"ERROR: {err}")
        return False

    if isinstance(base, VoidType):
        return True

    if isinstance(base, ClassType) and base.name not in known_classes:
        err = SemanticError(f"Tipo de clase no declarado: '{base.name}' usado en {where}.",
                            line=ctx.start.line, column=ctx.start.column)
        (errors_list or []).append(err)
        log_semantic(f"ERROR: {err}")
        return False

    return True
