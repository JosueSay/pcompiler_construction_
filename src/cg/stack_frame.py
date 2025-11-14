from dataclasses import dataclass
from typing import Dict, Set
from logs.logger import log


@dataclass
class StackFrame:
    func_name: str
    temp_offsets: Dict[str, int]
    locals_size: int
    saved_fp_offset: int
    saved_ra_offset: int
    frame_size: int

    @classmethod
    def fromTemps(cls, func_name: str, temps: Set[str]) -> "StackFrame":
        sorted_temps = sorted(temps, key=lambda s: int(s[1:])) if temps else []
        temp_offsets: Dict[str, int] = {}
        for index, temp_name in enumerate(sorted_temps):
            temp_offsets[temp_name] = index * 4

        locals_size = len(temp_offsets) * 4
        saved_fp_offset = locals_size
        saved_ra_offset = locals_size + 4
        frame_size = locals_size + 8

        log(
            f"[frame] func={func_name} temps={sorted_temps} "
            f"locals_size={locals_size} frame_size={frame_size}",
            channel="cg",
        )
        return cls(
            func_name=func_name,
            temp_offsets=temp_offsets,
            locals_size=locals_size,
            saved_fp_offset=saved_fp_offset,
            saved_ra_offset=saved_ra_offset,
            frame_size=frame_size,
        )

    def emitPrologue(self, emitter) -> None:
        emitter.emitText(f"{self.func_name}:")
        emitter.emitText(f"    addi $sp, $sp, -{self.frame_size}")
        emitter.emitText(f"    sw $fp, {self.saved_fp_offset}($sp)")
        emitter.emitText(f"    sw $ra, {self.saved_ra_offset}($sp)")
        emitter.emitText("    move $fp, $sp")
        if self.func_name == "main":
            emitter.emitText("    # inicio de main")

    def emitEpilogue(self, emitter) -> None:
        end_label = f"{self.func_name}_end"
        emitter.emitText(f"{end_label}:")
        emitter.emitText(f"    lw $ra, {self.saved_ra_offset}($fp)")
        emitter.emitText(f"    lw $fp, {self.saved_fp_offset}($fp)")
        emitter.emitText(f"    addi $sp, $sp, {self.frame_size}")
        emitter.emitText("    jr $ra")

    def loadTemp(self, emitter, temp_name: str, reg: str) -> None:
        if temp_name not in self.temp_offsets:
            emitter.emitText(f"    # temp no encontrado: {temp_name}, usando 0")
            emitter.emitText(f"    li {reg}, 0")
            log(f"[frame] loadTemp missing {temp_name}", channel="cg")
            return
        offset = self.temp_offsets[temp_name]
        emitter.emitText(f"    lw {reg}, {offset}($fp)")

    def storeTemp(self, emitter, temp_name: str, reg: str) -> None:
        if temp_name not in self.temp_offsets:
            emitter.emitText(
                f"    # temp no encontrado para store: {temp_name}, se ignora"
            )
            log(f"[frame] storeTemp missing {temp_name}", channel="cg")
            return
        offset = self.temp_offsets[temp_name]
        emitter.emitText(f"    sw {reg}, {offset}($fp)")
