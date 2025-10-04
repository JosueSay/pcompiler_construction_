from __future__ import annotations

from typing import Optional

from semantic.custom_types import Type


class Symbol:
    """
    Entrada de la **tabla de símbolos** usada por la fase semántica y el backend TAC.

    Qué representa:
      - Variables, constantes, parámetros, funciones/métodos, campos y (si lo usas) clases.
      - Metadatos necesarios para layout (offset, width, storage) y generación TAC (label, frame size).

    Notas de diseño:
      - El atributo de tipo se llama **`type`** (no `type_`) por compatibilidad con el resto del código.
      - Las categorías son strings (ver `semantic/symbol_kinds.py`) para facilitar logs/serialización.
      - Los métodos auxiliares (`isVariable`, `isFunction`, etc.) devuelven un booleano directo.

    Atributos públicos principales:
      name: str
      type: Type
      category: str
      scope_id: int
      offset: int              # desplazamiento relativo dentro del storage
      width: int               # ancho en bytes (0 para funciones)
      initialized: bool
      init_value_type: Type|None
      init_note: str|None
      param_types: list[Type]  # solo para funciones/métodos
      return_type: Type|None   # solo para funciones/métodos
      fields: dict[str, Type]  # opcional: para tipos compuestos si lo usas
      label: str|None          # etiqueta para TAC/ensamblado
      storage: str             # 'global' | 'stack' | 'param'
      addr_class: str          # clase lógica de dirección (normalmente igual a storage)
      is_ref: bool             # true para referencias (string, class, array)
      local_frame_size: int|None  # tamaño de frame (solo funciones/métodos, lo fija ScopeManager)
    """

    def __init__(
        self,
        name: str,
        type_: Type,
        category: str,
        scope_id: int,
        offset: int = 0,
        width: int = 4,
        initialized: bool = False,
        init_value_type: Optional[Type] = None,
        init_note: Optional[str] = None,
        param_types: Optional[list[Type]] = None,
        return_type: Optional[Type] = None,
        fields: Optional[dict[str, Type]] = None,
        label: Optional[str] = None,
        storage: str = "stack",
        addr_class: Optional[str] = None,
        *,
        is_ref: bool = False,
        local_frame_size: Optional[int] = None,
    ) -> None:
        # Identidad y clasificación
        self.name = name
        self.type = type_
        self.category = category
        self.scope_id = scope_id

        # Layout / ubicación
        self.offset = offset
        self.width = width
        self.storage = storage
        self.addr_class = addr_class or storage  # por defecto coincide con storage

        # Estado de inicialización
        self.initialized = initialized
        self.init_value_type = init_value_type
        self.init_note = init_note

        # Firma (si aplica)
        self.param_types = param_types or []
        self.return_type = return_type

        # Miembros (opcional, si manejas compuestos aquí)
        self.fields = fields or {}

        # Emisión / backend
        self.label = label
        self.is_ref = is_ref
        self.local_frame_size = local_frame_size

    # ---------------- Helpers de consulta ----------------

    def isVariable(self) -> bool:
        """True si el símbolo es una variable."""
        return self.category == "variable"

    def isConstant(self) -> bool:
        """True si el símbolo es una constante."""
        return self.category == "constant"

    def isFunction(self) -> bool:
        """True si el símbolo es una función o método."""
        return self.category == "function"

    def isParameter(self) -> bool:
        """True si el símbolo es un parámetro formal."""
        return self.category == "parameter"

    def isClass(self) -> bool:
        """True si el símbolo representa una clase (si usas esa categoría)."""
        return self.category == "class"

    def isField(self) -> bool:
        """True si el símbolo es un campo/atributo (si usas esa categoría)."""
        return self.category == "field"

    def storageClass(self) -> str:
        """Devuelve la clase lógica de dirección (global/stack/param)."""
        return self.addr_class

    def hasLabel(self) -> bool:
        """True si el símbolo tiene una etiqueta asociada (para TAC/ASM)."""
        return bool(self.label)

    # ---------------- Representación ----------------

    def __repr__(self) -> str:
        return (
            "Symbol("
            f"name={self.name}, type={self.type}, category={self.category}, "
            f"scope={self.scope_id}, offset={self.offset}, width={self.width}, "
            f"initialized={self.initialized}, storage={self.storage}, addr_class={self.addr_class}, "
            f"is_ref={self.is_ref}, local_frame_size={self.local_frame_size}"
            ")"
        )
