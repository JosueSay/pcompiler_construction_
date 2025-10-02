class Symbol:
    """
    Entrada de la tabla de símbolos.

    Atributos:
        name (str)
        type (Type)                      # Nota: se usa 'type' (no 'type_') para compatibilidad actual
        category (str)                   # 'variable', 'function', 'parameter', 'class', 'field', ...
        scope_id (int)
        offset (int)                     # posición relativa en memoria
        width (int)
        initialized (bool)
        init_value_type (Type | None)    # NUEVO: tipo del valor del inicializador si aplica
        init_note (str | None)           # NUEVO: nota textual del inicializador si aplica
        param_types (List[Type])
        return_type (Type | None)
        fields (Dict[str, Type])
        label (str | None)
        storage (str)                    # 'global' | 'stack' | 'param'
        addr_class (str)                 # 'global' | 'stack' | 'param' (lógico para TAC)
        is_ref (bool)                    # NUEVO: si es referencia (string, class, array)
        local_frame_size (int | None)
    """

    def __init__(
        self,
        name,
        type_,
        category,
        scope_id,
        offset=0,
        width=4,
        initialized=False,
        init_value_type=None,
        init_note=None,
        param_types=None,
        return_type=None,
        fields=None,
        label=None,
        storage="stack",
        addr_class=None,
        *,
        is_ref: bool = False,
        local_frame_size: int | None = None,
    ):
        self.name = name
        self.type = type_
        self.category = category
        self.scope_id = scope_id
        self.offset = offset
        self.width = width

        self.initialized = initialized
        self.init_value_type = init_value_type
        self.init_note = init_note

        self.param_types = param_types or []
        self.return_type = return_type
        self.fields = fields or {}
        self.label = label

        self.storage = storage
        self.addr_class = addr_class or storage

        self.is_ref = is_ref
        self.local_frame_size = local_frame_size

    # Helpers...
    def isVariable(self) -> bool: return self.category == "variable"
    def isConstant(self) -> bool: return self.category == "constant"
    def isFunction(self) -> bool: return self.category == "function"
    def isParameter(self) -> bool: return self.category == "parameter"
    def isClass(self) -> bool:     return self.category == "class"
    def isField(self) -> bool:     return self.category == "field"

    def storageClass(self) -> str:
        return self.addr_class

    def hasLabel(self) -> bool:
        return bool(self.label)

    def __repr__(self):
        return (
            f"Symbol(name={self.name}, type={self.type}, category={self.category}, "
            f"scope={self.scope_id}, offset={self.offset}, width={self.width}, "
            f"initialized={self.initialized}, storage={self.storage}, addr_class={self.addr_class}, "
            f"is_ref={self.is_ref}, local_frame_size={self.local_frame_size})"
        )
