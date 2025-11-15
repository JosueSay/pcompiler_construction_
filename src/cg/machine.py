# describe la máquina mips y la convención de llamadas

class MachineDesc:
    def __init__(self):
        self.temp_regs = ["$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6", "$t7", "$t8", "$t9"]
        self.saved_regs = ["$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7"]
        self.arg_regs = ["$a0", "$a1", "$a2", "$a3"]
        self.ret_regs = ["$v0", "$v1"]

        self.sp = "$sp"
        self.fp = "$fp"
        self.gp = "$gp"
        self.ra = "$ra"

        self.word_size = 4

    def isTemp(self, reg_name):
        return reg_name in self.temp_regs

    def isSaved(self, reg_name):
        return reg_name in self.saved_regs

    def allRegs(self):
        return self.temp_regs + self.saved_regs
