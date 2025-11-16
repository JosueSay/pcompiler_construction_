from logs.logger import log, currentOutDir
from .machine import MachineDesc
from .activation_records import ActivationRecordBuilder
from .descriptors import RegisterDescriptor, AddressDescriptor, RegisterAllocator
from .instr_selector import InstructionSelector
from .mips_emitter import MipsEmitter

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

        # transformar cada quad a instrucciones mips
        for q in quads:
            self.instr_selector.lowerQuad(q, self.mips_emitter)

        # escribir archivo de salida
        out_dir = currentOutDir()
        stem = stem or self.program_name
        asm_path = self.mips_emitter.writeAsm(out_dir, stem)

        # log final con ruta generada
        log(f"[CG] fin generateFromQuads -> {asm_path}", channel="cg")
        return asm_path
