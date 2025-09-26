from __future__ import annotations


class TempPool:
    """
    Pool de temporales por función, con reciclaje por tipo.
    - newTemp(type_name) => "tN"
    - free(name, type_name)
    - resetPerStatement()
    - resetPerFunction()
    """
    def __init__(self) -> None:
        self.next_id: int = 0
        self.free_pools: dict[str, list[str]] = {}
        self.live_since_stmt: list[str] = []

    def newTemp(self, type_name: str) -> str:
        pool = self.free_pools.get(type_name)
        if pool and len(pool) > 0:
            name = pool.pop()
        else:
            self.next_id += 1
            name = f"t{self.next_id}"
        self.live_since_stmt.append(name)
        return name

    def free(self, name: str, type_name: str) -> None:
        pool = self.free_pools.setdefault(type_name, [])
        pool.append(name)

    def resetPerStatement(self, type_resolver: callable | None = None) -> None:
        """
        Libera los temporales usados en la sentencia actual hacia sus pools.
        Si se aporta type_resolver(name) -> type_name, se clasifica por tipo.
        """
        if not self.live_since_stmt:
            return
        if type_resolver is None:
            # Si no hay resolution de tipo, devolverlos a un pool genérico.
            for name in self.live_since_stmt:
                pool = self.free_pools.setdefault("*", [])
                pool.append(name)
        else:
            for name in self.live_since_stmt:
                type_name = type_resolver(name)
                pool = self.free_pools.setdefault(type_name, [])
                pool.append(name)
        self.live_since_stmt.clear()

    def resetPerFunction(self) -> None:
        """
        Reinicia el espacio de nombres de temporales para la función.
        """
        self.next_id = 0
        self.free_pools.clear()
        self.live_since_stmt.clear()
