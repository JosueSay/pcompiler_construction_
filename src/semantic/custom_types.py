class Type:
    """
    Clase base para todos los tipos de datos.
    Provee comparación de tipos por clase e impresión legible del nombre del tipo.
    """

    def __eq__(self, other):
        """
        Permite comparar dos tipos para verificar si son del mismo tipo concreto.
        Por ejemplo: IntegerType() == IntegerType() → True
        """
        return isinstance(other, self.__class__)

    def __str__(self):
        """
        Retorna el nombre del tipo en minúsculas.
        Por ejemplo: IntegerType → 'integer'
        """
        return self.__class__.__name__.replace("Type", "").lower()


class IntegerType(Type):
    """Tipo de dato entero (4 bytes)."""
    pass


class FloatType(Type):
    """Tipo de dato de punto flotante (8 bytes)."""
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
        """
        Solo se considera igual a otro ErrorType.
        Esto evita errores cascada en validaciones.
        """
        return isinstance(other, ErrorType)

class VoidType(Type):
    """Tipo void: solo válido como tipo de retorno."""
    pass

class ClassType(Type):
    """
    Representa el tipo de una clase por nombre (referencia).
    """
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, ClassType) and self.name == other.name

    def __str__(self):
        return self.name  # imprime el nombre de la clase


class ArrayType(Type):
    """
    Arreglo homogéneo de un tipo base (referencia).
    """
    def __init__(self, elem_type: Type):
        self.elem_type = elem_type

    def __eq__(self, other):
        return isinstance(other, ArrayType) and self.elem_type == other.elem_type

    def __str__(self):
        return f"{self.elem_type}[]"