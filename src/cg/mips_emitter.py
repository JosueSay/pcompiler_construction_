import os
from logs.logger import log


class MipsEmitter:
    def __init__(self, program_name: str):
        self.program_name = program_name
        self.data_lines: list[str] = []
        self.text_lines: list[str] = []
        self.has_text_header = False

    def emitData(self, line: str) -> None:
        self.data_lines.append(line)
        log(f"[data] {line}", channel="cg")

    def emitText(self, line: str) -> None:
        if not self.has_text_header:
            self.text_lines.append(".text")
            self.text_lines.append(".globl main")
            self.has_text_header = True
        self.text_lines.append(line)
        log(f"[text] {line}", channel="cg")

    def writeToFile(self, out_dir: str) -> str:
        asm_path = os.path.join(out_dir, f"{self.program_name}.asm")
        with open(asm_path, "w", encoding="utf-8") as f:
            if self.data_lines:
                f.write(".data\n")
                for line in self.data_lines:
                    f.write(line + "\n")
                f.write("\n")
            if self.text_lines:
                for line in self.text_lines:
                    f.write(line + "\n")
        log(f"[cg] asm escrito en {asm_path}", channel="cg", force=True)
        return asm_path
