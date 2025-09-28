from semantic.symbol_table import Symbol
from semantic.type_system import getTypeWidth, isReferenceType
from semantic.symbol_kinds import SymbolCategory

class ScopeManager:
    """
    Administra los distintos entornos (scopes) de un programa utilizando una pila de diccionarios.
    Cada entorno contiene símbolos declarados localmente, con su respectivo offset de memoria.
    """

    def __init__(self):
        self.scopes = [{}]      # Pila de entornos (cada uno es un diccionario de símbolos)
        self.offsets = [0]      # Pila paralela para manejar el offset actual en cada entorno
        self.scopeId = 0        # ID incremental para identificar cada entorno

    def enterScope(self):
        """
        Entra a un nuevo entorno (por ejemplo, al entrar a una función o bloque).
        Crea un nuevo diccionario vacío y un nuevo offset inicial.
        """
        self.scopes.append({})
        self.offsets.append(0)
        self.scopeId += 1
        return self.scopeId
    
    def currentStorage(self):
        return "global" if self.scopeId == 0 else "stack"

    def frameSize(self):
        """Bytes usados en el scope actual (útil para generación de código)."""
        return self.offsets[-1]    

    def exitScope(self):
        """
        Retorna el frame size del scope que se cierra (útil para logs / CG),
        luego hace pop.
        """
        size = self.offsets[-1]
        self.scopes.pop()
        self.offsets.pop()
        self.scopeId -= 1
        return size

    def addSymbol(
        self,
        name,
        type_,
        category=SymbolCategory.VARIABLE,
        *,
        initialized=False,
        init_value_type=None,
        init_note=None
    ):
        """
        Agrega un nuevo símbolo al entorno actual.
        
        Parámetros:
            - name (str): nombre del símbolo.
            - type_ (Type): tipo del símbolo (IntegerType, StringType, etc.).
            - category (SymbolCategory): categoría (variable, función, parámetro, etc.).

        Retorna:
            - Symbol: el símbolo recién creado y registrado.
        
        Lanza:
            - Exception si el símbolo ya existe en el entorno actual.
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
            scope_id=self.scopeId,
            offset=offset,
            width=width,
            initialized=initialized,
            init_value_type=init_value_type,
            init_note=init_note,
            storage=storage,
            is_ref=is_ref,
            addr_class=addr_class
        )

        self.scopes[-1][name] = symbol
        self.offsets[-1] += width
        return symbol

    def lookup(self, name):
        """
        Busca un símbolo en todos los entornos activos, desde el más reciente al global.
        
        Parámetro:
            - name (str): nombre del símbolo a buscar.

        Retorna:
            - Symbol si se encuentra, o None si no está declarado.
        """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def allSymbols(self):
        """
        Devuelve una lista con todos los símbolos de todos los entornos actuales.
        Ideal para debug o reporte final.

        Retorna:
            - List[Symbol]: lista de todos los símbolos acumulados.
        """
        all_syms = []
        for scope in self.scopes:
            all_syms.extend(scope.values())
        return all_syms
    
    def closeFunctionScope(self, func_symbol: Symbol) -> int:
        """
        Cierra el scope actual y actualiza func_symbol.local_frame_size
        con los bytes usados por locales/temps del scope.
        """
        size = self.exitScope()
        func_symbol.local_frame_size = size
        return size
