# selección de instrucciones mips a partir de quads

from ir.tac import Op
from logs.logger import log


class InstructionSelector:
    def __init__(self, machine_desc, reg_alloc, addr_desc, frame_builder):
        self.machine_desc = machine_desc
        self.reg_alloc = reg_alloc
        self.addr_desc = addr_desc
        self.frame_builder = frame_builder  # se usará más adelante para prólogos reales

    def lowerQuad(self, quad, mips_emitter):
        log(f"[CG] lowering quad: {quad}", channel="cg")
        op = quad.op

        if op is Op.ENTER:
            self.lowerEnter(quad, mips_emitter)
        elif op is Op.LEAVE:
            self.lowerLeave(quad, mips_emitter)
        elif op is Op.LABEL:
            self.lowerLabel(quad, mips_emitter)
        elif op is Op.GOTO:
            self.lowerGoto(quad, mips_emitter)
        elif op is Op.IF_GOTO:
            self.lowerIfGoto(quad, mips_emitter)
        elif op is Op.IF_FALSE_GOTO:
            self.lowerIfFalseGoto(quad, mips_emitter)
        elif op is Op.ASSIGN:
            self.lowerAssign(quad, mips_emitter)
        elif op is Op.BINARY:
            self.lowerBinary(quad, mips_emitter)
        elif op is Op.INDEX_LOAD:
            self.lowerIndexLoad(quad, mips_emitter)
        elif op is Op.INDEX_STORE:
            self.lowerIndexStore(quad, mips_emitter)
        elif op is Op.NEWOBJ:
            self.lowerNewObj(quad, mips_emitter)
        elif op is Op.RETURN:
            self.lowerReturn(quad, mips_emitter)
        elif op is Op.PARAM:
            self.lowerParam(quad, mips_emitter)
        elif op is Op.CALL:
            self.lowerCall(quad, mips_emitter)
        else:
            mips_emitter.emitComment(f"quad no manejado: {quad.op.value}")


    # ---------- funciones / activación ----------

    def lowerEnter(self, quad, mips_emitter):
        # quad.arg1 = label de la función (nombre)
        func_label = quad.arg1

        # pedimos el layout del frame a ActivationRecordBuilder
        frame_layout = self.frame_builder.buildForFunction(func_label)
        self.current_frame = frame_layout

        frame_size = int(frame_layout.frame_size or 0)
        if frame_size < 8:
            frame_size = 8  # espacio mínimo para $fp y $ra

        # etiqueta de función
        mips_emitter.emitLabel(func_label)
        mips_emitter.emitComment(f"prologo frame_size={frame_size}")

        # reservar espacio en stack
        mips_emitter.emitInstr("addiu", "$sp", "$sp", f"-{frame_size}")

        # guardar $ra y $fp en el frame
        mips_emitter.emitInstr("sw", "$ra", f"{frame_layout.saved_ra_offset}($sp)")
        mips_emitter.emitInstr("sw", "$fp", f"{frame_layout.saved_fp_offset}($sp)")

        # actualizar $fp
        mips_emitter.emitInstr("move", "$fp", "$sp")



    def lowerLeave(self, quad, mips_emitter):
        if self.current_frame is None:
            mips_emitter.emitComment("epilogo sin frame (noop)")
            return

        frame_size = int(self.current_frame.frame_size or 0)
        if frame_size < 8:
            frame_size = 8

        mips_emitter.emitComment("epilogo")

        # restaurar $sp al inicio del frame
        mips_emitter.emitInstr("move", "$sp", "$fp")

        # restaurar $ra y $fp
        mips_emitter.emitInstr("lw", "$ra", f"{self.current_frame.saved_ra_offset}($sp)")
        mips_emitter.emitInstr("lw", "$fp", f"{self.current_frame.saved_fp_offset}($sp)")

        # liberar el frame
        mips_emitter.emitInstr("addiu", "$sp", "$sp", f"{frame_size}")

        # volver al caller
        mips_emitter.emitInstr("jr", "$ra")

        self.current_frame = None


    # ---------- control de flujo ----------

    def lowerLabel(self, quad, mips_emitter):
        mips_emitter.emitLabel(quad.res)

    def lowerGoto(self, quad, mips_emitter):
        target = quad.arg1
        mips_emitter.emitInstr("j", target)



    def lowerIfGoto(self, quad, mips_emitter):
        # pendiente: generar rama condicional real
        mips_emitter.emitComment(f"if {quad.arg1} goto {quad.arg2}")

    def lowerIfFalseGoto(self, quad, mips_emitter):
        # pendiente: generar rama condicional real
        mips_emitter.emitComment(f"ifFalse {quad.arg1} goto {quad.arg2}")

    # ---------- expresiones / datos ----------

    def lowerAssign(self, quad, mips_emitter):
        mips_emitter.emitComment(f"assign {quad.res} := {quad.arg1}")

    def lowerBinary(self, quad, mips_emitter):
        mips_emitter.emitComment(
            f"binary {quad.res} := {quad.arg1} {quad.label} {quad.arg2}"
        )

    def lowerReturn(self, quad, mips_emitter):
        if quad.arg1 is not None:
            # más adelante se hará el move real a $v0
            mips_emitter.emitComment(f"return {quad.arg1} -> $v0")
        else:
            mips_emitter.emitComment("return")

    # ---------- llamadas ----------

    def lowerParam(self, quad, mips_emitter):
        # más adelante se hará el push real en la pila / paso en registros
        mips_emitter.emitComment(f"param {quad.arg1}")

    def lowerCall(self, quad, mips_emitter):
        # aquí luego se generará jal <label> y el ajuste de pila
        mips_emitter.emitComment(f"call {quad.arg1} n_args={quad.arg2}")

    # ---------- arreglos / objetos ----------

    def lowerIndexLoad(self, quad, mips_emitter):
        dst = quad.res
        base = quad.arg1
        idx = quad.arg2
        # de momento solo dejamos trazabilidad en el asm
        # más adelante aquí se hace el lw con cálculo de dirección
        mips_emitter.emitComment(f"index_load {dst} := {base}[{idx}]")

    def lowerIndexStore(self, quad, mips_emitter):
        base = quad.arg1
        idx = quad.arg2 if quad.arg2 is not None else quad.label
        src = quad.res
        # igual, ahora solo comentamos; luego se baja a sw real
        mips_emitter.emitComment(f"index_store {base}[{idx}] := {src}")

    def lowerNewObj(self, quad, mips_emitter):
        dst = quad.res
        class_name = quad.arg1
        size = quad.arg2
        # punto de inicio para manejar el heap / layout de objetos
        mips_emitter.emitComment(
            f"newobj {dst} = newobj {class_name}, size={size}"
        )
