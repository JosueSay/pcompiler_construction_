import os

class MipsEmitter:
    def __init__(self, program_name):
        # guarda el nombre del programa para usarlo en los metadatos del asm
        self.program_name = program_name
        self.data_lines = []
        self.text_lines = []
        self.current_label = None

    def emitData(self, line):
        # agrega una línea a la sección .data
        self.data_lines.append(line)

    def emitText(self, line):
        # agrega una línea directa a la sección .text
        self.text_lines.append(line)

    def emitInstr(self, op, *operands):
        # arma la instrucción mips: op dst, src1, src2...
        if operands:
            self.text_lines.append(f"{op} " + ", ".join(operands))
        else:
            self.text_lines.append(op)

    def emitLabel(self, label):
        # define una etiqueta en la sección .text
        self.text_lines.append(f"{label}:")
        self.current_label = label

    def emitComment(self, text):
        # inserta un comentario mips en la salida
        self.text_lines.append(f"# {text}")

    def emitJump(self, target):
        # salto incondicional mips
        self.text_lines.append(f"j {target}")

    def buildAsm(self):
        # construye el texto final del asm en orden: metadata, .data, .text
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
        # crea el dir si no existe y escribe el archivo .asm resultante
        os.makedirs(out_dir, exist_ok=True)
        filename = f"{stem}.asm"
        path = os.path.join(out_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.buildAsm())
        return path
