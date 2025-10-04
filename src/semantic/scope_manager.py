from __future__ import annotations

from typing import Optional

from semantic.symbol_table import Symbol
from semantic.symbol_kinds import SymbolCategory
from semantic.type_system import getTypeWidth, isReferenceType


class ScopeManager:
    """
    Administrador de ámbitos para el análisis semántico.

    Qué lleva dentro:
      - Una pila de diccionarios de símbolos (`self.scopes`), uno por ámbito.
      - Un acumulador de offset por ámbito (`self.offsets`) para calcular
        desplazamientos dentro del frame.
      - Un identificador entero para cada scope (`self.scope_stack`), con
        `0` reservado para el global.
      - Un contador monotónico para asignar nuevos IDs (`self.next_scope_id`).

    Convenciones:
      - El ámbito global es el primero (ID = 0).
      - Los símbolos FUNCTION no consumen ancho (width=0), no desplazan offset.
      - `addr_class` será "param" para parámetros y el `storage` para el resto.

    Métodos públicos (camelCase):
      - currentScopeId() -> int
      - enterScope() -> int
      - exitScope() -> int
      - currentStorage() -> str
      - frameSize() -> int
      - addSymbol(...): crea símbolo en el scope actual
      - addSymbolGlobal(...): crea símbolo en el scope global
      - lookup(name) -> Symbol|None
      - allSymbols() -> list[Symbol]
      - closeFunctionScope(func_symbol) -> int  (anota local_frame_size)
    """

    def __init__(self) -> None:
        # Pila de scopes (cada uno: dict nombre -> Symbol).
        self.scopes: list[dict[str, Symbol]] = [{}]
        # Pila de offsets (acumulado por ámbito).
        self.offsets: list[int] = [0]
        # IDs de ámbito anidados; 0 es global.
        self.scope_stack: list[int] = [0]
        # Generador de IDs crecientes (el próximo que asigne enterScope()).
        self.next_scope_id: int = 0

    # ----------------- Estado/IDs -----------------

    def currentScopeId(self) -> int:
        """ID del ámbito actual (punta de la pila)."""
        return self.scope_stack[-1]

    def enterScope(self) -> int:
        """
        Abre un nuevo ámbito (p. ej. al entrar en un bloque o función).
        Devuelve el ID asignado.
        """
        self.next_scope_id += 1
        new_id = self.next_scope_id
        self.scopes.append({})
        self.offsets.append(0)
        self.scope_stack.append(new_id)
        return new_id

    def exitScope(self) -> int:
        """
        Cierra el ámbito actual y devuelve el tamaño total (bytes) consumido
        por los símbolos no-FUNCTION declarados en él.
        """
        size = self.offsets[-1]
        self.scopes.pop()
        self.offsets.pop()
        self.scope_stack.pop()
        return size

    # ----------------- Info del frame -----------------

    def currentStorage(self) -> str:
        """
        Tipo de almacenamiento para el scope actual:
          - "global" si estamos en el scope raíz
          - "stack"  para scopes anidados
        """
        return "global" if len(self.scope_stack) == 1 else "stack"

    def frameSize(self) -> int:
        """
        Tamaño actual (bytes) del frame del scope activo.
        Útil para anotar `local_frame_size` al cerrar una función.
        """
        return self.offsets[-1]

    # ----------------- Altas de símbolos -----------------

    def addSymbol(
        self,
        name: str,
        type_,
        category: SymbolCategory = SymbolCategory.VARIABLE,
        *,
        initialized: bool = False,
        init_value_type=None,
        init_note: Optional[str] = None,
    ) -> Symbol:
        """
        Registra un símbolo en el scope actual.

        Reglas:
          - No permite colisiones dentro del mismo scope.
          - Para FUNCTION, el ancho es 0 (no mueve offset).
          - `addr_class` es "param" si es parámetro; de lo contrario = storage.

        Devuelve el `Symbol` creado.
        """
        if name in self.scopes[-1]:
            raise Exception(f"Símbolo '{name}' ya declarado en este ámbito.")

        width = 0 if category == SymbolCategory.FUNCTION else getTypeWidth(type_)
        offset = self.offsets[-1]
        storage = self.currentStorage()
        is_ref = isReferenceType(type_)
        addr_class = "param" if category == SymbolCategory.PARAMETER else storage

        symbol = Symbol(
            name=name,
            type_=type_,
            category=category,
            scope_id=self.currentScopeId(),
            offset=offset,
            width=width,
            initialized=initialized,
            init_value_type=init_value_type,
            init_note=init_note,
            storage=storage,
            addr_class=addr_class,
            is_ref=is_ref,
        )
        self.scopes[-1][name] = symbol
        self.offsets[-1] += width
        return symbol

    def addSymbolGlobal(
        self,
        name: str,
        type_,
        category: SymbolCategory = SymbolCategory.VARIABLE,
        *,
        initialized: bool = False,
        init_value_type=None,
        init_note: Optional[str] = None,
    ) -> Symbol:
        """
        Registra un símbolo *directamente* en el ámbito global (ID=0), sin importar
        el scope actual. Útil para declaraciones toplevel.
        """
        if name in self.scopes[0]:
            raise Exception(f"Símbolo '{name}' ya declarado en el ámbito global.")

        width = 0 if category == SymbolCategory.FUNCTION else getTypeWidth(type_)
        offset = self.offsets[0]
        storage = "global"
        is_ref = isReferenceType(type_)
        addr_class = "param" if category == SymbolCategory.PARAMETER else storage

        symbol = Symbol(
            name=name,
            type_=type_,
            category=category,
            scope_id=0,
            offset=offset,
            width=width,
            initialized=initialized,
            init_value_type=init_value_type,
            init_note=init_note,
            storage=storage,
            addr_class=addr_class,
            is_ref=is_ref,
        )
        self.scopes[0][name] = symbol
        # Nota: para FUNCTION, width=0 → no mueve offset.
        self.offsets[0] += width
        return symbol

    # ----------------- Búsquedas y utilidades -----------------

    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Busca un símbolo por nombre desde el scope actual hacia arriba.
        Devuelve el `Symbol` si lo encuentra, o None si no existe.
        """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def allSymbols(self) -> list[Symbol]:
        """Lista plana con todos los símbolos visibles (todos los scopes)."""
        return [sym for scope in self.scopes for sym in scope.values()]

    def closeFunctionScope(self, func_symbol: Symbol) -> int:
        """
        Cierra el scope de una función, calcula su `local_frame_size` a partir
        del tamaño del frame del ámbito que se cierra, y lo devuelve.
        """
        size = self.exitScope()
        func_symbol.local_frame_size = size
        return size
