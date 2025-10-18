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
        self.free_by_kind = defaultdict(list)  # kind -> [tN, ...]
        self.kind_of: dict[str, str] = {}      # tN -> kind
        self.leased_stmt: set[str] = set()
    
    def __repr__(self) -> str:
        try:
            kinds = sorted(self.free_by_kind.keys())
            free_desc = ", ".join(f"{k}:{list(self.free_by_kind[k])}" for k in kinds if self.free_by_kind[k])
            leased = sorted(self.leased_stmt)
            return f"<TempPool next={self.next_id} leased={leased} free={{ {free_desc} }}>"
        except Exception:
            return f"<TempPool next={self.next_id}>"

    def newTemp(self, kind: str = "*") -> str:
        """
        Devuelve un temporal del tipo `kind`, reutilizando si es posible.
        """
        k = kind or "*"
        if self.free_by_kind[k]:
            name = self.free_by_kind[k].pop()
            # Asegura que el mapeo exista (defensivo ante resetes parciales)
            self.kind_of.setdefault(name, k)
        else:
            name = f"t{self.next_id}"
            self.next_id += 1
            self.kind_of[name] = k
        self.leased_stmt.add(name)
        return name


    def free(self, name: str, kind: str = "*") -> None:
        """
        Libera un temporal solo si tiene forma 't<numero>'.
        Evita meter en la free list lugares como gp[8], fp[0], literales, etc.
        """
        if not name or not isinstance(name, str) or not name.startswith("t") or not name[1:].isdigit():
            return
        k = self.kind_of.get(name, kind or "*")
        # Evita double-free (mismo tN ya en la free-list)
        if name in self.free_by_kind[k]:
            return
        self.free_by_kind[k].append(name)
        self.leased_stmt.discard(name)
        log(f"\t\t[TempPool][pool] free  {name} ({k})", channel="tac")


    def resetPerStatement(self) -> None:
        """Marca el fin de una sentencia: devolver temporales a la free list."""
        for name in list(self.leased_stmt):
            # Solo reciclar verdaderos temporales t\d+
            if isinstance(name, str) and name.startswith("t") and name[1:].isdigit():
                k = self.kind_of.get(name, "*")
                self.free_by_kind[k].append(name)
                log(f"\t\t[TempPool][pool] free  {name} ({k}) [resetPerStatement]", channel="tac")
        self.leased_stmt.clear()

    def resetPerFunction(self) -> None:
        """Marca el inicio de una nueva función: reinicia numeración y estructuras."""
        self.next_id = 0
        self.free_by_kind.clear()
        self.leased_stmt.clear()
        self.kind_of.clear()