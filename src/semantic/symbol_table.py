class Symbol:
    """
    Representa una entrada en la tabla de símbolos.

    Atributos:
        name (str): Nombre del identificador.
        type_ (Type): Instancia de tipo semántico (IntegerType, StringType, etc.).
        category (str): Categoría del símbolo ('variable', 'function', etc.).
        scope_id (int): ID del ámbito donde fue declarado.
        offset (int): Posición relativa dentro del ámbito.
        width (int): Tamaño en bytes.
        param_types (List[Type]): Tipos de parámetros si el símbolo es función.
        return_type (Type): Tipo de retorno si es función.
        initialized (bool): Si fue inicializado (True) o no (False).
        init_value_type (Type|None): Tipo del valor usado para inicializar (p.ej. NullType()).
        init_note (str|None): Nota breve del origen de la inicialización (p.ej. 'explicit', 'default-null', 'missing-initializer').
    """

    def __init__(
        self,
        name,
        type_,
        category,
        scope_id,
        offset=0,
        width=4,
        param_types=None,
        return_type=None,
        initialized=False,
        init_value_type=None,
        init_note=None
    ):
        self.name = name
        self.type = type_
        self.category = category
        self.scope_id = scope_id
        self.offset = offset
        self.width = width
        self.param_types = param_types or []
        self.return_type = return_type

        # Nuevo: metadatos de inicialización
        self.initialized = initialized
        self.init_value_type = init_value_type
        self.init_note = init_note

    def __repr__(self):
        base = (
            f"Symbol(name={self.name}, type={self.type}, category={self.category}, "
            f"scope={self.scope_id}, offset={self.offset}, width={self.width}"
        )
        init_part = f", initialized={self.initialized}"
        if self.init_value_type is not None:
            init_part += f", init_value_type={self.init_value_type}"
        if self.init_note:
            init_part += f", init_note={self.init_note}"
        return base + init_part + ")"
