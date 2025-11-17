import os

class MipsEmitter:
    def __init__(self, program_name):
        # guarda el nombre del programa para usarlo en los metadatos del asm
        self.program_name = program_name
        self.data_lines = ["__gp_base: .space 256"]
        self.text_lines = []
        self.current_label = None

        # pool de strings
        self.string_pool = {}     # text -> label
        self.data_strings = []    # lista de (label, text)
        self.string_counter = 0

    def emitData(self):
        """
        Genera la sección .data:
        - Literales de string internados.
        - Área de globals para gp[...] (ej. gp[0], gp[8], etc.).
        """
        lines = []
        lines.append(".data")

        # --- strings ---
        for label, text in self.string_pool.items():
            lines.append(f"{label}: .asciiz {text}")

        # --- área para 'gp' (global frame) ---
        # 256 bytes = 64 enteros de 4 bytes; te sobra para gp[0..252].
        lines.append("__gp_base: .space 256")

        return "\n".join(lines)

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

    # ---------- soporte para literales de string ----------

    def internString(self, text: str) -> str:
        """
        Devuelve una etiqueta para el literal de texto.
        Si ya existe, la reutiliza.
        """
        if text in self.string_pool:
            return self.string_pool[text]

        label = f"__str_{self.string_counter}"
        self.string_counter += 1
        self.string_pool[text] = label
        self.data_strings.append((label, text))
        return label

    # ---------- construcción y escritura del ASM ----------

    def buildAsm(self):
        # construye el texto final del asm en orden: metadata, .data, .text
        lines = []
        lines.append("# mips generado por compiscript")
        lines.append(f"# program: {self.program_name}")
        lines.append("")

        if self.data_lines or self.data_strings:
            lines.append(".data")
            # primero cualquier línea .data explícita
            lines.extend(self.data_lines)
            # luego los literales de string
            for label, text in self.data_strings:
                esc = (
                    text.replace("\\", "\\\\")
                        .replace("\"", "\\\"")
                        .replace("\n", "\\n")
                )
                lines.append(f"{label}: .asciiz \"{esc}\"")
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
