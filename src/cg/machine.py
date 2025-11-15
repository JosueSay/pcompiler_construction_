class MachineDesc:
    def __init__(self):
        # registros temporales, el compilador puede sobrescribirlos libremente
        self.temp_regs = ["$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6", "$t7", "$t8", "$t9"]

        # registros que deben preservarse entre llamadas
        self.saved_regs = ["$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7"]

        # registros donde llegan los argumentos de una función
        self.arg_regs = ["$a0", "$a1", "$a2", "$a3"]

        # registros donde se devuelve el resultado
        self.ret_regs = ["$v0", "$v1"]

        # punteros estándar usados en el ABI mips
        self.sp = "$sp"   # stack pointer
        self.fp = "$fp"   # frame pointer
        self.gp = "$gp"   # global pointer
        self.ra = "$ra"   # return address

        self.word_size = 4  # tamaño de palabra mips (32 bits)

    def isTemp(self, reg_name):
        # verifica si el registro es temporal
        return reg_name in self.temp_regs

    def isSaved(self, reg_name):
        # verifica si el registro debe preservarse
        return reg_name in self.saved_regs

    def allRegs(self):
        # lista combinada útil para validaciones o asignación de registros
        return self.temp_regs + self.saved_regs + self.ret_regs
