from typing import Dict, Optional
from semantic.custom_types import Type

class ClassInfo:
    def __init__(self, name: str, base: Optional[str] = None):
        self.name = name
        self.base = base  # nombre de la clase base o None
        self.attributes: Dict[str, Type] = {}  # nombre -> Type

class ClassHandler:
    """
    Registro ligero de clases para el análisis semántico:
      - nombre -> ClassInfo
      - atributos por clase
      - lookup con herencia (sube por base)
    Métodos públicos:
      - ensure_class(name, base=None)
      - add_attribute(class_name, attr_name, attr_type)
      - get_attribute_type(class_name, attr_name) -> Type|None
      - get_base(name) -> Optional[str]
      - iter_bases(name) -> Iterator[str]
    """
    def __init__(self):
        self._classes: Dict[str, ClassInfo] = {}

    # ---- clases ----
    def ensure_class(self, name: str, base: Optional[str] = None):
        ci = self._classes.get(name)
        if ci is None:
            ci = ClassInfo(name, base)
            self._classes[name] = ci
        else:
            if base is not None:
                ci.base = base
        return ci

    def exists(self, name: str) -> bool:
        return name in self._classes

    def get_base(self, name: str) -> Optional[str]:
        ci = self._classes.get(name)
        return ci.base if ci else None

    def iter_bases(self, name: str):
        """
        Itera hacia arriba por la cadena de herencia: base, base de la base, ...
        Se detiene si detecta ciclos defensivamente.
        """
        seen = set()
        curr = self.get_base(name)
        while curr and curr not in seen:
            yield curr
            seen.add(curr)
            curr = self.get_base(curr)

    # ---- atributos ----
    def add_attribute(self, class_name: str, attr_name: str, attr_type: Type):
        ci = self.ensure_class(class_name)
        ci.attributes[attr_name] = attr_type

    def get_attribute_type(self, class_name: str, attr_name: str) -> Optional[Type]:
        """
        Busca el atributo en la clase y si no está, camina por la cadena de herencia.
        """
        seen = set()
        curr = class_name
        while curr and curr not in seen:
            seen.add(curr)
            ci = self._classes.get(curr)
            if ci is None:
                return None
            if attr_name in ci.attributes:
                return ci.attributes[attr_name]
            curr = ci.base
        return None
