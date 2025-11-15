# construcción de .data y .text y escritura del asm

import os


class MipsEmitter:
    def __init__(self, program_name):
        self.program_name = program_name
        self.data_lines = []
        self.text_lines = []
        self.current_label = None

    def emitData(self, line):
        self.data_lines.append(line)

    def emitText(self, line):
        self.text_lines.append(line)

    def emitInstr(self, op, *operands):
        # emite una instrucción mips genérica: op dst, src1, src2...
        if operands:
            self.text_lines.append(f"{op} " + ", ".join(operands))
        else:
            self.text_lines.append(op)

    def emitLabel(self, label):
        self.text_lines.append(f"{label}:")
        self.current_label = label

    def emitComment(self, text):
        self.text_lines.append(f"# {text}")

    def emitJump(self, target):
        # salto incondicional mips
        self.text_lines.append(f"j {target}")

    def buildAsm(self):
        lines = []
        lines.append("# mips generado por compiscript")
        lines.append(f"# program: {self.program_name}")
        lines.append("")

        if self.data_lines:
            lines.append(".data")
            lines.extend(self.data_lines)
            lines.append("")

        lines.append(".text")
        lines.append(".globl main")
        lines.extend(self.text_lines)
        lines.append("")
        return "\n".join(lines)

    def writeAsm(self, out_dir, stem):
        os.makedirs(out_dir, exist_ok=True)
        filename = f"{stem}.asm"
        path = os.path.join(out_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.buildAsm())
        return path
