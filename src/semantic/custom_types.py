from __future__ import annotations
from typing import Optional


class Type:
    """
    Clase base de todos los tipos del sistema.

    Convenciones:
      - La igualdad por defecto compara la CLASE del tipo (p.ej., IntegerType == IntegerType).
      - La representación en str elimina el sufijo "Type" y usa minúsculas
        (útil para mensajes y reportes).
    """

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)

    def __str__(self) -> str:
        return self.__class__.__name__.replace("Type", "").lower()


class IntegerType(Type):
    """
    Tipo entero.
    Considera 4 bytes por defecto (tamaño lo decide el backend de tamaños).
    """
    pass


class StringType(Type):
    """
    Tipo cadena (referencia/puntero en la mayoría de backends).
    Normalmente 8 bytes en plataformas de 64 bits.
    """
    pass


class BoolType(Type):
    """
    Tipo booleano (true/false).
    Suele representarse con 1 byte.
    """
    pass


class NullType(Type):
    """
    Tipo nulo: representa ausencia de valor/referencia.
    Compatible con tipos referencia a nivel semántico.
    """
    pass


class ErrorType(Type):
    """
    Tipo de error: sirve para propagar fallos de tipos sin abortar el análisis.
    Solo es igual a sí mismo.
    """

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ErrorType)


class VoidType(Type):
    """
    Tipo void: únicamente válido como tipo de retorno (no se instancia como valor).
    """
    pass


class ClassType(Type):
    """
    Representa una clase declarada en el lenguaje.

    Atributos:
        name: Nombre de la clase.
        parent: Clase base (si hay herencia) o None.
        members: Tabla de miembros propios de la clase (atributos/métodos expuestos
                 como tipos, si la capa semántica así lo decide).

    Notas:
        - La comparación (==) es por nombre de clase.
        - La búsqueda de miembros (hasMember/getMember) recorre la herencia.
    """

    def __init__(self, name: str, parent: Optional[ClassType] = None):
        self.name = name
        self.parent = parent
        self.members: dict[str, Type] = {}

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ClassType) and self.name == other.name

    def __str__(self) -> str:
        return f"class {self.name}"

    def hasMember(self, name: str) -> bool:
        """True si `name` existe en esta clase o en su cadena de herencia."""
        if name in self.members:
            return True
        if self.parent:
            return self.parent.hasMember(name)
        return False

    def getMember(self, name: str) -> Optional[Type]:
        """Devuelve el tipo del miembro `name` (buscando también en la base)."""
        if name in self.members:
            return self.members[name]
        if self.parent:
            return self.parent.getMember(name)
        return None


class StructType(Type):
    """
    Representa una estructura (como un 'record'): sin herencia ni métodos.

    Atributos:
        name: Nombre de la estructura.
        members: Mapa nombre -> Type de los campos.
    """

    def __init__(self, name: str):
        self.name = name
        self.members: dict[str, Type] = {}

    def __eq__(self, other: object) -> bool:
        return isinstance(other, StructType) and self.name == other.name

    def __str__(self) -> str:
        return f"struct {self.name}"

    def hasMember(self, name: str) -> bool:
        return name in self.members

    def getMember(self, name: str) -> Optional[Type]:
        return self.members.get(name)


class ArrayType(Type):
    """
    Arreglo homogéneo de un tipo base (p.ej., integer[]).

    Atributos:
        elem_type: Tipo de los elementos.
    """

    def __init__(self, elem_type: Type):
        self.elem_type = elem_type

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ArrayType) and self.elem_type == other.elem_type

    def __str__(self) -> str:
        return f"{self.elem_type}[]"


class FunctionType(Type):
    """
    Tipo función: lista de parámetros y tipo de retorno.

    Atributos:
        param_types: Lista de tipos de parámetros en orden.
        return_type: Tipo de retorno (puede ser None para denotar 'void' a nivel
                     de impresión; semánticamente se suele normalizar a VoidType()).

    Notas:
        - La igualdad compara aridad, tipos posicionales y retorno.
        - __str__ imprime "void" si return_type es None.
    """

    def __init__(self, param_types: Optional[list[Type]], return_type: Optional[Type]):
        self.param_types: list[Type] = param_types or []
        self.return_type: Optional[Type] = return_type

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, FunctionType)
            and len(self.param_types) == len(other.param_types)
            and all(a == b for a, b in zip(self.param_types, other.param_types))
            and self.return_type == other.return_type
        )

    def __str__(self) -> str:
        params = ", ".join(str(p) for p in self.param_types)
        ret = str(self.return_type) if self.return_type is not None else "void"
        return f"({params}) -> {ret}"
