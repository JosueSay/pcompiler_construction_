from semantic.type_system import getTypeWidth

# oldFP (4) + retAddr (4) => 8 bytes
PARAM_BASE = 8

def place_of_symbol(sym, *, fp_syntax: bool = True) -> str:
    """
    Devuelve el 'place' textual para un símbolo ya anotado por semántica.
    sym.addr_class: 'param' | 'local' | 'global'
    sym.offset:     desplazamiento *desde el inicio de su zona*
    sym.width:      tamaño del símbolo (para locals)
    """
    cls = getattr(sym, "addr_class", getattr(sym, "storage", "stack"))

    if cls == "param":
        if fp_syntax:
            # params viven por encima de FP
            return f"fp[{PARAM_BASE + sym.offset}]"
        return f"param[{sym.offset}]"

    if cls == "local":
        # locals viven por debajo de FP
        # OJO: tu FrameAllocator da offset = inicio del bloque del local;
        # la dirección efectiva = FP - (offset + width)
        disp = sym.offset + sym.width
        if fp_syntax:
            return f"fp[-{disp}]"
        return f"local[{sym.offset}]"

    # global
    if fp_syntax:
        return f"gp[{sym.offset}]"
    return f"global[{sym.offset}]"


def elem_width_of(type_):
    """ ancho del dato (útil para INDEX_LOAD/STORE, FIELD_*) """
    return getTypeWidth(type_)


def elem_width_of_array(type_):
    from semantic.custom_types import ArrayType
    if isinstance(type_, ArrayType):
        return getTypeWidth(type_.elem_type)
    return getTypeWidth(type_)
