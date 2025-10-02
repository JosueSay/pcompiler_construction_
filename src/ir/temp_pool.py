from __future__ import annotations


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
        self.next: int = 1              # contador por función
        self.per_stmt: set[str] = set() # temporales creados en la sentencia actual
        self.per_func: set[str] = set() # temporales creados en la función actual

    def newTemp(self, kind: str = "*") -> str:
        """
        Devuelve un nuevo nombre temporal (tN). `kind` se ignora para el
        nombre pero se mantiene por compatibilidad con los llamadores.
        """
        name = f"t{self.next}"
        self.next += 1
        self.per_stmt.add(name)
        self.per_func.add(name)
        return name

    def free(self, name: str, kind: str = "*") -> None:
        """
        Gancho para liberar un temporal. No hace nada a propósito.
        Se conserva para no romper a los llamadores.
        """
        return

    def resetPerStatement(self) -> None:
        """Marca el fin de una sentencia: limpiamos el set por-sentencia."""
        self.per_stmt.clear()

    def resetPerFunction(self) -> None:
        """Marca el inicio de una nueva función: reinicia numeración y sets."""
        self.per_func.clear()
        self.per_stmt.clear()
        self.next = 1
