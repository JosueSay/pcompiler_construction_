class MachineDesc:
    def __init__(self):
        # registro reservado para 'this' (no lo usamos en allRegs)
        self.this_reg = "$s0"

        # registros temporales, el compilador puede sobrescribirlos libremente
        self.temp_regs = ["$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6", "$t7", "$t8", "$t9"]

        # registros que deben preservarse entre llamadas
        # OJO: empezamos en $s1 porque $s0 lo reservamos para 'this'
        self.saved_regs = ["$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7"]

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
        """
        Registros que el allocator puede usar.
        No incluimos $sp, $fp, $gp, $ra ni this_reg ($s0).
        """
        return self.temp_regs + self.saved_regs + self.ret_regs
