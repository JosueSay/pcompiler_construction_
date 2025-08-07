class Symbol:
    """
    Representa una entrada en la tabla de símbolos del compilador/interprete.

    Atributos:
        name (str): Nombre del identificador.
        type_ (Type): Instancia de tipo semántico (IntegerType, BoolType, etc.).
        category (str): Categoría del símbolo ('variable', 'function', etc.).
        scope_id (int): ID del ámbito o entorno donde fue declarado.
        offset (int): Posición relativa en memoria dentro del ámbito.
        width (int): Cantidad de bytes que ocupa el símbolo.
        param_types (List[Type]): Tipos de parámetros si el símbolo es una función.
        return_type (Type): Tipo de retorno si el símbolo es una función.
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
        return_type=None
    ):
        self.name = name
        self.type = type_                       # Tipo de dato (IntegerType, etc.)
        self.category = category                # variable, function, constant, parameter
        self.scope_id = scope_id                # ID del entorno donde fue declarado
        self.offset = offset                    # Posición en memoria relativa al scope
        self.width = width                      # Tamaño en bytes
        self.param_types = param_types or []    # Solo si es función
        self.return_type = return_type          # Solo si es función

    def __repr__(self):
        return (
            f"Symbol(name={self.name}, type={self.type}, "
            f"category={self.category}, scope={self.scope_id}, "
            f"offset={self.offset}, width={self.width})"
        )
