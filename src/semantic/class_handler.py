from typing import Optional, Iterator
from semantic.custom_types import Type


class ClassInfo:
    """
    Contenedor mínimo de metadatos de una clase durante el análisis semántico.

    Atributos:
        name: Nombre de la clase.
        base: Nombre de la clase base (o None si no hereda).
        attributes: Mapa nombre_de_campo -> Type con los atributos declarados
                    directamente en esta clase (sin incluir los heredados).
    """
    def __init__(self, name: str, base: Optional[str] = None):
        self.name = name
        self.base = base
        self.attributes: dict[str, Type] = {}  # nombre -> Type


class ClassHandler:
    """
    Registro ligero de clases para la fase semántica.

    Qué hace:
      - Mantiene un índice nombre -> ClassInfo.
      - Permite registrar atributos y consultar su tipo subiendo por herencia.
      - Expone utilidades para calcular offsets de campos y tamaño total de objeto.

    Notas:
      - Este módulo no valida la existencia de tipos (eso corresponde a la
        resolución de tipos); solo almacena lo que se le indica.
      - La herencia se recorre de forma defensiva para evitar ciclos.
    """

    def __init__(self):
        self._classes: dict[str, ClassInfo] = {}

    # ---------------- Clases ----------------

    def ensureClass(self, name: str, base: Optional[str] = None) -> ClassInfo:
        """
        Crea (si no existe) o devuelve el ClassInfo de `name`.
        Si ya existía y se provee `base`, actualiza la clase base.
        """
        ci = self._classes.get(name)
        if ci is None:
            ci = ClassInfo(name, base)
            self._classes[name] = ci
        else:
            if base is not None:
                ci.base = base
        return ci

    def exists(self, name: str) -> bool:
        """True si la clase `name` ya fue registrada."""
        return name in self._classes

    def getBase(self, name: str) -> Optional[str]:
        """Devuelve el nombre de la clase base de `name` (o None si no hereda o no existe)."""
        ci = self._classes.get(name)
        return ci.base if ci else None

    def iterBases(self, name: str) -> Iterator[str]:
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

    # ---------------- Atributos ----------------

    def addAttribute(self, class_name: str, attr_name: str, attr_type: Type) -> None:
        """
        Registra (o actualiza) el atributo `attr_name: attr_type` en `class_name`.
        No afecta a clases base ni derivadas: solo escribe en la clase indicada.
        """
        ci = self.ensureClass(class_name)
        ci.attributes[attr_name] = attr_type

    def getAttributeType(self, class_name: str, attr_name: str) -> Optional[Type]:
        """
        Busca el tipo del atributo `attr_name` comenzando por `class_name`
        y subiendo por la cadena de herencia. Devuelve None si no se encuentra.
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

    # ---------------- Offsets / tamaño de objeto ----------------

    def getFieldOffsets(self, class_name: str) -> dict[str, int]:
        """
        Devuelve un dict nombre_de_campo -> offset (en bytes) para `class_name`.

        Regla de cómputo:
          1) Se acumulan primero los campos heredados en orden (base -> derivada).
          2) Luego se agregan los campos propios en orden de inserción.
          3) Los offsets se calculan sumando `getTypeWidth` de cada campo.

        Nota: si la clase base cambia, vuelve a llamarse para recalcular.
        """
        from semantic.type_system import getTypeWidth  # import local para evitar ciclos

        # 1) Offsets heredados
        offsets: dict[str, int] = {}
        size_so_far = 0
        base = self.getBase(class_name)
        if base:
            base_offsets = self.getFieldOffsets(base)
            offsets.update(base_offsets)
            # tamaño de la base = suma de anchos de sus campos
            base_size = 0
            for bname in base_offsets.keys():
                ci_base = self._classes.get(base)
                if ci_base and bname in ci_base.attributes:
                    base_size += getTypeWidth(ci_base.attributes[bname])
            size_so_far = base_size

        # 2) Añadir atributos propios
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
        Offset (en bytes) del campo `attr_name` dentro de `class_name`,
        o None si el campo no existe (ni en la jerarquía).
        """
        offs = self.getFieldOffsets(class_name)
        return offs.get(attr_name)

    def getObjectSize(self, class_name: str) -> int:
        """
        Tamaño total (en bytes) de una instancia de `class_name`:
        suma de anchos de todos los atributos visibles (base + propios).
        """
        from semantic.type_system import getTypeWidth  # import local para evitar ciclos
        total = 0

        # Recolectar jerarquía (base más alta al principio)
        seen = set()
        stack: list[str] = []
        curr = class_name
        while curr and curr not in seen:
            stack.append(curr)
            seen.add(curr)
            curr = self.getBase(curr)

        # Sumar de base->derivada
        for cname in reversed(stack):
            ci = self._classes.get(cname)
            if not ci:
                continue
            for _, atype in ci.attributes.items():
                total += getTypeWidth(atype)

        return total
