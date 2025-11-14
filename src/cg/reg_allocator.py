from logs.logger import log


class RegAllocator:
    def __init__(self) -> None:
        self.temp_regs: list[str] = [
            "$t0",
            "$t1",
            "$t2",
            "$t3",
            "$t4",
            "$t5",
            "$t6",
            "$t7",
            "$t8",
            "$t9",
        ]
        self.free: set[str] = set(self.temp_regs)
        self.in_use: set[str] = set()

    def getTempReg(self) -> str:
        if not self.free:
            # por ahora no hacemos spill, solo log
            log("[reg] sin registros libres, usando $t0", channel="cg")
            return "$t0"
        reg = sorted(self.free)[0]
        self.free.remove(reg)
        self.in_use.add(reg)
        log(f"[reg] get {reg}", channel="cg")
        return reg

    def release(self, reg: str) -> None:
        if reg in self.in_use:
            self.in_use.remove(reg)
            self.free.add(reg)
            log(f"[reg] release {reg}", channel="cg")
