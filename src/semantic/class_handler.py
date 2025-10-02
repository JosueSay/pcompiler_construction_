from typing import Optional
from semantic.custom_types import Type

class ClassInfo:
    def __init__(self, name: str, base: Optional[str] = None):
        self.name = name
        self.base = base  # nombre de la clase base o None
        self.attributes: dict[str, Type] = {}  # nombre -> Type

class ClassHandler:
    """
    Registro ligero de clases para el análisis semántico:
      - nombre -> ClassInfo
      - atributos por clase
      - lookup con herencia (sube por base)

    Métodos públicos (camelCase):
      - ensureClass(name, base=None)
      - addAttribute(class_name, attr_name, attr_type)
      - getAttributeType(class_name, attr_name) -> Type|None
      - getBase(name) -> Optional[str]
      - iterBases(name) -> Iterator[str]
      - getFieldOffsets(class_name) -> dict[str, int]
      - getFieldOffset(class_name, attr_name) -> int|None
      - getObjectSize(class_name) -> int
    """

    def __init__(self):
        self._classes: dict[str, ClassInfo] = {}

    # --- clases ---
    def ensureClass(self, name: str, base: Optional[str] = None):
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

    def getBase(self, name: str) -> Optional[str]:
        ci = self._classes.get(name)
        return ci.base if ci else None

    def iterBases(self, name: str):
        """
        Itera hacia arriba por la cadena de herencia: base, base de la base, ...
        Se detiene si detecta ciclos defensivamente.
        """
        seen = set()
        curr = self.getBase(name)
        while curr and curr not in seen:
            yield curr
            seen.add(curr)
            curr = self.getBase(curr)

    # --- atributos ---
    def addAttribute(self, class_name: str, attr_name: str, attr_type: Type):
        ci = self.ensureClass(class_name)
        ci.attributes[attr_name] = attr_type

    def getAttributeType(self, class_name: str, attr_name: str) -> Optional[Type]:
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

    # --- utilidades para offsets/tamaño de objeto ---
    def getFieldOffsets(self, class_name: str) -> dict[str, int]:
        """
        Devuelve un dict nombre_de_campo -> offset (en bytes) para 'class_name',
        acumulando primero los campos heredados (en orden base->derivada) y
        luego los declarados en la clase (en orden de inserción).
        """
        from semantic.type_system import getTypeWidth  # import local para evitar ciclos

        # 1) empezar con offsets de la base
        offsets: dict[str, int] = {}
        size_so_far = 0
        base = self.getBase(class_name)
        if base:
            base_offsets = self.getFieldOffsets(base)
            offsets.update(base_offsets)
            # tamaño base = suma de sus anchos
            base_size = 0
            for bname in base_offsets.keys():
                ci_base = self._classes.get(base)
                if ci_base and bname in ci_base.attributes:
                    base_size += getTypeWidth(ci_base.attributes[bname])
            size_so_far = base_size

        # 2) añadir los atributos declarados en la clase actual
        ci = self._classes.get(class_name)
        if not ci:
            return offsets
        for aname, atype in ci.attributes.items():
            if aname not in offsets:
                offsets[aname] = size_so_far
                size_so_far += getTypeWidth(atype)
        return offsets

    def getFieldOffset(self, class_name: str, attr_name: str) -> int | None:
        """
        Offset (en bytes) del campo 'attr_name' dentro de 'class_name', o None si no existe.
        """
        offs = self.getFieldOffsets(class_name)
        return offs.get(attr_name)

    def getObjectSize(self, class_name: str) -> int:
        """
        Tamaño total (en bytes) de una instancia de 'class_name'
        = suma de anchos de todos los atributos visibles (base + propios).
        """
        from semantic.type_system import getTypeWidth  # import local para evitar ciclos
        total = 0

        seen = set()
        stack = []
        curr = class_name
        while curr and curr not in seen:
            stack.append(curr)
            seen.add(curr)
            curr = self.getBase(curr)

        for cname in reversed(stack):
            ci = self._classes.get(cname)
            if not ci:
                continue
            for _, atype in ci.attributes.items():
                total += getTypeWidth(atype)
        return total
