from logs.logger import log
from .log_reg import dump_addr_desc, dump_reg_desc
class RegisterDescriptor:
    def __init__(self, regs):
        # mapa de registros a los valores que contienen
        self.reg_contents = {reg: set() for reg in regs}
        log(f"[RegisterDescriptor.__init__] regs={regs}", channel="regalloc")

    def clear(self):
        # limpia todo el contenido registrado
        log("[RegisterDescriptor.clear] limpiando todo", channel="regalloc")
        for reg in self.reg_contents:
            self.reg_contents[reg].clear()

    def addContent(self, reg, name):
        # agrega un valor asociado a un registro
        self.reg_contents.setdefault(reg, set()).add(name)
        log(f"[RegisterDescriptor.addContent] {reg} += {name} -> {self.reg_contents[reg]}",
            channel="regalloc")

    def removeContent(self, reg, name):
        if reg in self.reg_contents:
            # elimina valor si está presente
            if name in self.reg_contents[reg]:
                self.reg_contents[reg].discard(name)
                log(f"[RegisterDescriptor.removeContent] {reg} -= {name} -> {self.reg_contents[reg]}",
                    channel="regalloc")

    def valueRegs(self, name):
        # devuelve los registros que contienen cierto valor
        result = []
        for reg, values in self.reg_contents.items():
            if name in values:
                result.append(reg)
        log(f"[RegisterDescriptor.valueRegs] name={name} -> regs={result}",
            channel="regalloc")
        return result


class AddressDescriptor:
    def __init__(self):
        # tabla que guarda info por variable
        self.locations = {}
        log("[AddressDescriptor.__init__]", channel="regalloc")

    def ensureEntry(self, name):
        # crea entrada si no existe
        if name not in self.locations:
            self.locations[name] = {
                "regs": set(),
                "stack_offset": None,
                "global_name": None,
            }
            log(f"[AddressDescriptor.ensureEntry] new entry for {name}", channel="regalloc")

    def setStackOffset(self, name, offset):
        # registra el offset de stack para la variable
        self.ensureEntry(name)
        self.locations[name]["stack_offset"] = offset
        log(f"[AddressDescriptor.setStackOffset] {name}.stack_offset = {offset}",
            channel="regalloc")

    def addReg(self, name, reg):
        # agrega referencia a registro
        self.ensureEntry(name)
        self.locations[name]["regs"].add(reg)
        log(f"[AddressDescriptor.addReg] {name}.regs += {reg} -> {self.locations[name]['regs']}",
            channel="regalloc")

    def removeReg(self, name, reg):
        # elimina referencia a registro
        self.ensureEntry(name)
        self.locations[name]["regs"].discard(reg)
        log(f"[AddressDescriptor.removeReg] {name}.regs -= {reg} -> {self.locations[name]['regs']}",
            channel="regalloc")

    def setGlobal(self, name, global_name):
        # marca nombre global asociado
        self.ensureEntry(name)
        self.locations[name]["global_name"] = global_name
        log(f"[AddressDescriptor.setGlobal] {name}.global = {global_name}",
            channel="regalloc")

    def getInfo(self, name):
        # devuelve info de la variable
        self.ensureEntry(name)
        info = self.locations[name]
        log(f"[AddressDescriptor.getInfo] {name} -> {info}", channel="regalloc")
        return info

class RegisterAllocator:
    def __init__(self, machine_desc, reg_desc, addr_desc):
        self.machine_desc = machine_desc
        self.reg_desc = reg_desc
        self.addr_desc = addr_desc
        log("[RegisterAllocator.__init__]", channel="regalloc")

    def getRegFor(self, name, current_frame, mips_emitter):
        # busca un registro libre
        regs = self.machine_desc.allRegs()
        log(f"[RegisterAllocator.getRegFor] pedir reg para name={name}, regs={regs}",
            channel="regalloc")
        dump_reg_desc(self.reg_desc)

        # busca un registro libre
        for reg in regs:
            if not self.reg_desc.reg_contents[reg]:
                # registro libre encontrado
                self.bindReg(reg, name)
                dump_reg_desc(self.reg_desc)
                dump_addr_desc(self.addr_desc)
                return reg

        # si no hay libres, elegimos víctima
        victim = regs[0]
        log(f"[RegisterAllocator.getRegFor] no libres, victim={victim} para {name}",
            channel="regalloc")
        self.spillReg(victim, current_frame, mips_emitter)
        self.bindReg(victim, name)
        dump_reg_desc(self.reg_desc)
        dump_addr_desc(self.addr_desc)
        return victim

    def bindReg(self, reg, name):
        log(f"[RegisterAllocator.bindReg] bind {name} -> {reg}", channel="regalloc")
        # desvincula contenido previo del registro
        for val in list(self.reg_desc.reg_contents[reg]):
            log(f"[RegisterAllocator.bindReg]  - limpiando {val} de {reg}", channel="regalloc")
            self.addr_desc.removeReg(val, reg)
            self.reg_desc.removeContent(reg, val)

        # asocia registro con nuevo valor
        self.reg_desc.addContent(reg, name)
        self.addr_desc.addReg(name, reg)
        dump_reg_desc(self.reg_desc)
        dump_addr_desc(self.addr_desc)

    def spillReg(self, reg, current_frame, mips_emitter):
        # vuelca el contenido del registro a memoria
        values = list(self.reg_desc.reg_contents[reg])
        log(f"[RegisterAllocator.spillReg] spill {reg} con valores={values}",
            channel="regalloc")

        for name in values:
            info = self.addr_desc.getInfo(name)
            regs_for_name = info["regs"]
            offset = info["stack_offset"]

            # si tenemos offset, sí guardamos a stack
            if offset is not None:
                mips_emitter.emitInstr("sw", reg, f"{offset}({self.machine_desc.fp})")
                log(
                    f"[RegisterAllocator.spillReg]   sw {reg},{offset}({self.machine_desc.fp}) para {name}",
                    channel="regalloc"
                )
            else:
                # de momento, mismo comportamiento que antes: solo se quita del reg
                log(
                    f"[RegisterAllocator.spillReg]   {name} sin stack_offset, solo se quita de {reg}",
                    channel="regalloc"
                )

            # en todos los casos, quitar el reg de la lista de ese nombre
            self.addr_desc.removeReg(name, reg)

        # limpiar el registro en el descriptor
        self.reg_desc.reg_contents[reg].clear()
        dump_reg_desc(self.reg_desc)
        dump_addr_desc(self.addr_desc)
