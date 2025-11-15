class RegisterDescriptor:
    def __init__(self, regs):
        # mapa de registros a los valores que contienen
        self.reg_contents = {reg: set() for reg in regs}

    def clear(self):
        # limpia todo el contenido registrado
        for reg in self.reg_contents:
            self.reg_contents[reg].clear()

    def addContent(self, reg, name):
        # agrega un valor asociado a un registro
        self.reg_contents.setdefault(reg, set()).add(name)

    def removeContent(self, reg, name):
        if reg in self.reg_contents:
            # elimina valor si está presente
            self.reg_contents[reg].discard(name)

    def valueRegs(self, name):
        # devuelve los registros que contienen cierto valor
        result = []
        for reg, values in self.reg_contents.items():
            if name in values:
                result.append(reg)
        return result


class AddressDescriptor:
    def __init__(self):
        # tabla que guarda info por variable
        self.locations = {}

    def ensureEntry(self, name):
        # crea entrada si no existe
        if name not in self.locations:
            self.locations[name] = {
                "regs": set(),
                "stack_offset": None,
                "global_name": None,
            }

    def setStackOffset(self, name, offset):
        # registra el offset de stack para la variable
        self.ensureEntry(name)
        self.locations[name]["stack_offset"] = offset

    def addReg(self, name, reg):
        # agrega referencia a registro
        self.ensureEntry(name)
        self.locations[name]["regs"].add(reg)

    def removeReg(self, name, reg):
        # elimina referencia a registro
        self.ensureEntry(name)
        self.locations[name]["regs"].discard(reg)

    def setGlobal(self, name, global_name):
        # marca nombre global asociado
        self.ensureEntry(name)
        self.locations[name]["global_name"] = global_name

    def getInfo(self, name):
        # devuelve info de la variable
        self.ensureEntry(name)
        return self.locations[name]


class RegisterAllocator:
    def __init__(self, machine_desc, reg_desc, addr_desc):
        self.machine_desc = machine_desc
        self.reg_desc = reg_desc
        self.addr_desc = addr_desc

    def getRegFor(self, name, current_frame, mips_emitter):
        # busca un registro libre
        regs = self.machine_desc.allRegs()

        for reg in regs:
            if not self.reg_desc.reg_contents[reg]:
                # registro libre encontrado
                self.bindReg(reg, name)
                return reg

        # si no hay libres, elegimos víctima
        victim = regs[0]
        self.spillReg(victim, current_frame, mips_emitter)
        self.bindReg(victim, name)
        return victim

    def bindReg(self, reg, name):
        # desvincula contenido previo del registro
        for val in list(self.reg_desc.reg_contents[reg]):
            self.addr_desc.removeReg(val, reg)
            self.reg_desc.removeContent(reg, val)

        # asocia registro con nuevo valor
        self.reg_desc.addContent(reg, name)
        self.addr_desc.addReg(name, reg)

    def spillReg(self, reg, current_frame, mips_emitter):
        # vuelca el contenido del registro a memoria
        values = list(self.reg_desc.reg_contents[reg])
        for name in values:
            info = self.addr_desc.getInfo(name)
            offset = info["stack_offset"]
            if offset is None:
                # falta asignar offset si no existe
                pass
            # aquí iría la instrucción real sw reg, offset($fp)
            self.addr_desc.removeReg(name, reg)
        self.reg_desc.reg_contents[reg].clear()
