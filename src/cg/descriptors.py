# descriptores de registros y direcciones

class RegisterDescriptor:
    def __init__(self, regs):
        self.reg_contents = {reg: set() for reg in regs}

    def clear(self):
        for reg in self.reg_contents:
            self.reg_contents[reg].clear()

    def addContent(self, reg, name):
        self.reg_contents.setdefault(reg, set()).add(name)

    def removeContent(self, reg, name):
        if reg in self.reg_contents:
            self.reg_contents[reg].discard(name)

    def valueRegs(self, name):
        result = []
        for reg, values in self.reg_contents.items():
            if name in values:
                result.append(reg)
        return result


class AddressDescriptor:
    def __init__(self):
        self.locations = {}

    def ensureEntry(self, name):
        if name not in self.locations:
            self.locations[name] = {
                "regs": set(),
                "stack_offset": None,
                "global_name": None,
            }

    def setStackOffset(self, name, offset):
        self.ensureEntry(name)
        self.locations[name]["stack_offset"] = offset

    def addReg(self, name, reg):
        self.ensureEntry(name)
        self.locations[name]["regs"].add(reg)

    def removeReg(self, name, reg):
        self.ensureEntry(name)
        self.locations[name]["regs"].discard(reg)

    def setGlobal(self, name, global_name):
        self.ensureEntry(name)
        self.locations[name]["global_name"] = global_name

    def getInfo(self, name):
        self.ensureEntry(name)
        return self.locations[name]


class RegisterAllocator:
    def __init__(self, machine_desc, reg_desc, addr_desc):
        self.machine_desc = machine_desc
        self.reg_desc = reg_desc
        self.addr_desc = addr_desc

    def getRegFor(self, name, current_frame, mips_emitter):
        regs = self.machine_desc.allRegs()

        for reg in regs:
            if not self.reg_desc.reg_contents[reg]:
                self.bindReg(reg, name)
                return reg

        victim = regs[0]
        self.spillReg(victim, current_frame, mips_emitter)
        self.bindReg(victim, name)
        return victim

    def bindReg(self, reg, name):
        for val in list(self.reg_desc.reg_contents[reg]):
            self.addr_desc.removeReg(val, reg)
            self.reg_desc.removeContent(reg, val)

        self.reg_desc.addContent(reg, name)
        self.addr_desc.addReg(name, reg)

    def spillReg(self, reg, current_frame, mips_emitter):
        values = list(self.reg_desc.reg_contents[reg])
        for name in values:
            info = self.addr_desc.getInfo(name)
            offset = info["stack_offset"]
            if offset is None:
                # luego aquí podemos asignar un offset nuevo
                pass
            # aca iría el sw real: sw reg, offset($fp)
            self.addr_desc.removeReg(name, reg)
        self.reg_desc.reg_contents[reg].clear()
