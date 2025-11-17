from logs.logger import log, currentOutDir
from .machine import MachineDesc
from .activation_records import ActivationRecordBuilder
from .descriptors import RegisterDescriptor, AddressDescriptor, RegisterAllocator
from .instr_selector import InstructionSelector
from .mips_emitter import MipsEmitter
from ir.tac import Op


class CodeGeneratorMips:
    def __init__(self, program_name, scope_manager, method_registry, class_layout=None):
        # init componentes principales para el generador
        self.program_name = program_name
        self.scope_manager = scope_manager
        self.method_registry = method_registry
        self.class_layout = class_layout or {}

        # setup de descripcion de maquina y estructuras auxiliares
        self.machine_desc = MachineDesc()
        self.reg_desc = RegisterDescriptor(self.machine_desc.allRegs())
        self.addr_desc = AddressDescriptor()
        self.reg_alloc = RegisterAllocator(self.machine_desc, self.reg_desc, self.addr_desc)
        self.frame_builder = ActivationRecordBuilder(self.machine_desc, self.scope_manager)

        # instancias para seleccion de instrucciones y emision mips
        self.mips_emitter = MipsEmitter(program_name)
        self.instr_selector = InstructionSelector(
            self.machine_desc,
            self.reg_alloc,
            self.addr_desc,
            self.frame_builder,
        )

    def generateFromQuads(self, quads, stem=None):
        # log inicial para rastrear generacion
        log("[CG] inicio generateFromQuads", channel="cg")

        # limpiar descriptores por si se reusa el generador
        self.reg_desc.clear()
        self.addr_desc.locations.clear()

        # manejo de toplevel como main sintético
        in_func = False        # estamos dentro de alguna función (entre ENTER/LEAVE)
        main_emitted = False   # ya emitimos la etiqueta main:

        for q in quads:
            op = q.op

            # --- controlar ENTER / LEAVE para saber si estamos en una función ---
            if op is Op.ENTER:
                in_func = True
                self.instr_selector.lowerQuad(q, self.mips_emitter)
                continue

            if op is Op.LEAVE:
                self.instr_selector.lowerQuad(q, self.mips_emitter)
                in_func = False
                continue

            # --- quads toplevel: aún no estamos en función ---
            if (not in_func) and (not main_emitted):
                # primer quad fuera de función => empezar main sintético
                self.mips_emitter.emitLabel("main")
                main_emitted = True

            # transformar cada quad a instrucciones mips
            self.instr_selector.lowerQuad(q, self.mips_emitter)

        # si hubo código toplevel, agregar cierre de programa
        if main_emitted:
            self.mips_emitter.emitComment("fin de main (toplevel)")
            # salida limpia en MARS/SPIM
            self.mips_emitter.emitInstr("li", "$v0", "10")
            self.mips_emitter.emitInstr("syscall")

        # escribir archivo de salida
        out_dir = currentOutDir()
        stem = stem or self.program_name
        asm_path = self.mips_emitter.writeAsm(out_dir, stem)

        # log final con ruta generada
        log(f"[CG] fin generateFromQuads -> {asm_path}", channel="cg")
        return asm_path
