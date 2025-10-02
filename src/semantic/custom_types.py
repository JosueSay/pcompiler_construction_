class Type:
    """
    Clase base para todos los tipos de datos.
    Provee comparación de tipos por clase e impresión legible del nombre del tipo.
    """

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __str__(self):
        return self.__class__.__name__.replace("Type", "").lower()


class IntegerType(Type):
    """Tipo de dato entero (4 bytes)."""
    pass


class StringType(Type):
    """Tipo de cadena de texto (8 bytes como referencia o puntero)."""
    pass


class BoolType(Type):
    """Tipo booleano (true/false, 1 byte)."""
    pass


class NullType(Type):
    """Tipo nulo. Representa una ausencia de valor o referencia nula."""
    pass


class ErrorType(Type):
    """
    Tipo de error. Utilizado para propagar errores semánticos y evitar interrupciones.
    No se compara como igual a ningún otro tipo, excepto a sí mismo.
    """
    def __eq__(self, other):
        return isinstance(other, ErrorType)


class VoidType(Type):
    """Tipo void: solo válido como tipo de retorno."""
    pass


class ClassType(Type):
    """
    Representa una clase definida en el lenguaje.
    Soporta herencia, atributos y métodos.
    """
    def __init__(self, name: str, parent=None):
        self.name = name
        self.parent = parent  # Otra instancia de ClassType o None
        self.members = {}     # { nombre: Type }

    def __eq__(self, other):
        return isinstance(other, ClassType) and self.name == other.name

    def __str__(self):
        return f"class {self.name}"

    def hasMember(self, name: str):
        """Verifica si un atributo o método existe en la clase o en su herencia."""
        if name in self.members:
            return True
        if self.parent:
            return self.parent.hasMember(name)
        return False

    def getMember(self, name: str):
        """Obtiene el tipo de un atributo o método."""
        if name in self.members:
            return self.members[name]
        if self.parent:
            return self.parent.getMember(name)
        return None


class StructType(Type):
    """
    Representa una estructura definida en el lenguaje.
    A diferencia de las clases, no soporta herencia ni métodos.
    """
    def __init__(self, name: str):
        self.name = name
        self.members = {}  # { nombre: Type }

    def __eq__(self, other):
        return isinstance(other, StructType) and self.name == other.name

    def __str__(self):
        return f"struct {self.name}"

    def hasMember(self, name: str):
        return name in self.members

    def getMember(self, name: str):
        return self.members.get(name)


class ArrayType(Type):
    """
    Arreglo homogéneo de un tipo base.
    """
    def __init__(self, elem_type: Type):
        self.elem_type = elem_type

    def __eq__(self, other):
        return isinstance(other, ArrayType) and self.elem_type == other.elem_type

    def __str__(self):
        return f"{self.elem_type}[]"


class FunctionType(Type):
    """
    Representa el tipo de una función: parámetros y retorno.
    """
    def __init__(self, param_types, return_type):
        self.param_types = param_types or []
        self.return_type = return_type

    def __eq__(self, other):
        return (
            isinstance(other, FunctionType) and
            len(self.param_types) == len(other.param_types) and
            all(a == b for a, b in zip(self.param_types, other.param_types)) and
            self.return_type == other.return_type
        )

    def __str__(self):
        params = ", ".join(str(p) for p in self.param_types)
        ret = str(self.return_type) if self.return_type else "void"
        return f"({params}) -> {ret}"
