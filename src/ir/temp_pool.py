from __future__ import annotations
from collections import defaultdict
from logs.logger import log

class TempPool:
    """
    Generador sencillo de nombres temporales por *función*.

    Decisiones:
      - No se reciclan identificadores: cada función arranca en t1 y
        se numeran en orden (t1, t2, ...). Es suficiente para el 3AC.
      - El parámetro `kind` existe porque el resto del pipeline lo pasa
        ("int", "bool", "ref", "*"), pero aquí solo sirve de anotación.
      - `free()` es intencionalmente un no-op. Se deja el gancho por si en
        el futuro quieres implementar reciclaje real.

    API estable (usada por el resto del backend):
      - newTemp(kind="*") -> str
      - free(name, kind="*") -> None
      - resetPerStatement() -> None
      - resetPerFunction()  -> None
    """

    def __init__(self) -> None:
        self.next_id = 0
        self._free = defaultdict(list)     # kind -> [tN, ...]
        self.kind_of: dict[str, str] = {} # tN -> kind
        self.leased_stmt: set[str] = set()

    def newTemp(self, kind: str = "*") -> str:
        """
        Devuelve un nuevo nombre temporal (tN). `kind` se ignora para el
        nombre pero se mantiene por compatibilidad con los llamadores.
        """
        k = kind or "*"
        if self._free[k]:
            name = self._free[k].pop()        
            log(f"[pool] reuse {name} ({k})", channel="tac")
                
        else:
            self.next_id += 1
            name = f"t{self.next_id}"
            self.kind_of[name] = k
            log(f"[pool] alloc {name} ({k})", channel="tac")
        self.leased_stmt.add(name)
        return name

    def free(self, name: str, kind: str = "*") -> None:
        """
        Gancho para liberar un temporal. No hace nada a propósito.
        Se conserva para no romper a los llamadores.
        """
        if not name:
            return
        k = self.kind_of.get(name, kind or "*")
        self._free[k].append(name)
        self.leased_stmt.discard(name)
        log(f"[pool] free  {name} ({k})", channel="tac")

    def resetPerStatement(self) -> None:
        """Marca el fin de una sentencia: limpiamos el set por-sentencia."""
        for name in list(self.leased_stmt):
            k = self.kind_of.get(name, "*")
            self._free[k].append(name)
            log(f"[pool] free  {name} ({k}) [resetPerStatement]", channel="tac")
        self.leased_stmt.clear()

    def resetPerFunction(self) -> None:
        """Marca el inicio de una nueva función: reinicia numeración y sets."""
        self.next_id = 0
        self._free.clear()
        self.leased_stmt.clear()
        self.kind_of.clear()