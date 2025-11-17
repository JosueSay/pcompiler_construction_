from ir.tac import Op
from logs.logger import log
from .log_reg import dump_addr_desc, dump_reg_desc

class InstructionSelector:
    
    def __init__(self, machine_desc, reg_alloc, addr_desc, frame_builder):
        self.machine_desc = machine_desc
        self.reg_alloc = reg_alloc
        self.addr_desc = addr_desc
        self.frame_builder = frame_builder
        self.current_frame = None
        self.pending_params = []

    def isImmediate(self, value):
        if value is None:
            return False
        s = str(value)
        if s.startswith("-"):
            return s[1:].isdigit()
        return s.isdigit()

    def isTemp(self, name):
        if not isinstance(name, str):
            return False
        if not name.startswith("t"):
            return False
        return name[1:].isdigit()

    def parseAddress(self, name):
        if not isinstance(name, str):
            return None
        if name.startswith("fp[") and name.endswith("]"):
            offset = int(name[3:-1])
            return (self.machine_desc.fp, offset)
        if name.startswith("gp[") and name.endswith("]"):
            offset = int(name[3:-1])
            return (self.machine_desc.gp, offset)
        return None

    def isStringLiteral(self, value):
        return (
            isinstance(value, str)
            and len(value) >= 2
            and value[0] == '"'
            and value[-1] == '"'
        )

    def isProtectedFrameSlot(self, base_reg, offset):
        """
        Evita escribir en los slots donde se guardan old $fp y $ra.
        """
        if self.current_frame is None:
            return False

        if base_reg != self.machine_desc.fp:
            return False

        return offset in (
            self.current_frame.saved_fp_offset,
            self.current_frame.saved_ra_offset,
        )

    def getValueReg(self, src, dst_hint, mips_emitter):
        log(f"[getValueReg] IN src={src}, dst_hint={dst_hint}", channel="regalloc")

        # src == 'R' significa retorno de función
        if src == "R":
            reg = self.machine_desc.ret_regs[0]
            mips_emitter.emitComment(f"getValueReg: src=R -> {reg}")
            log(f"[getValueReg] src=R -> reg={reg}", channel="regalloc")
            return reg

        # 'this' como puntero al objeto actual
        if isinstance(src, str) and src == "this":
            this_reg = getattr(self.machine_desc, "this_reg", None)
            if this_reg is None:
                mips_emitter.emitComment("getValueReg: 'this' pero machine_desc.this_reg no definido")
                log("[getValueReg] this_reg no definido", channel="regalloc")
                return None
            mips_emitter.emitComment(f"getValueReg: src=this -> {this_reg}")
            log(f"[getValueReg] src=this -> reg={this_reg}", channel="regalloc")
            return this_reg

        # gp como puntero global base
        if isinstance(src, str) and src == "gp":
            gp_reg = getattr(self.machine_desc, "gp", None)
            if gp_reg is None:
                mips_emitter.emitComment("getValueReg: 'gp' pero machine_desc.gp no definido")
                log("[getValueReg] gp no definido en machine_desc", channel="regalloc")
                return None
            mips_emitter.emitComment(f"getValueReg: src=gp -> {gp_reg}")
            log(f"[getValueReg] src=gp -> reg={gp_reg}", channel="regalloc")
            return gp_reg

        # literales string: "hola", "texto\n", etc.
        if isinstance(src, str) and len(src) >= 2 and src[0] == '"' and src[-1] == '"':
            text = src[1:-1]
            label = mips_emitter.internString(text)
            name = dst_hint if dst_hint is not None else label
            reg = self.reg_alloc.getRegFor(name, self.current_frame, mips_emitter)
            mips_emitter.emitInstr("la", reg, label)
            mips_emitter.emitComment(
                f"getValueReg: src={src} (string) -> {reg} (label={label}, name={name})"
            )
            log(f"[getValueReg] STRING src={src} name={name} -> reg={reg}, label={label}",
                channel="regalloc")
            dump_reg_desc(self.reg_alloc.reg_desc)
            return reg

        # cargar inmediato
        if self.isImmediate(src):
            name = dst_hint if dst_hint is not None else str(src)
            reg = self.reg_alloc.getRegFor(name, self.current_frame, mips_emitter)
            mips_emitter.emitInstr("li", reg, str(src))
            mips_emitter.emitComment(f"getValueReg: src={src} (imm) -> {reg} (name={name})")
            log(f"[getValueReg] IMM src={src} name={name} -> reg={reg}", channel="regalloc")
            dump_reg_desc(self.reg_alloc.reg_desc)
            return reg

        # cargar desde memoria fp[...] o gp[...]
        addr = self.parseAddress(src)
        if addr is not None:
            base_reg, offset = addr
            name = dst_hint if dst_hint is not None else f"{src}_tmp"
            reg = self.reg_alloc.getRegFor(name, self.current_frame, mips_emitter)
            mips_emitter.emitInstr("lw", reg, f"{offset}({base_reg})")
            mips_emitter.emitComment(
                f"getValueReg: src={src} (mem {base_reg}+{offset}) -> {reg} (name={name})"
            )
            log(f"[getValueReg] MEM src={src} base={base_reg} off={offset} name={name} -> reg={reg}",
                channel="regalloc")
            dump_reg_desc(self.reg_alloc.reg_desc)
            dump_addr_desc(self.reg_alloc.addr_desc)
            return reg

        # temporales tN
        if self.isTemp(src):
            regs = self.reg_alloc.reg_desc.valueRegs(src)
            if regs:
                reg = regs[0]
                mips_emitter.emitComment(f"getValueReg: src={src} (temp en reg existente) -> {reg}")
                log(f"[getValueReg] TEMP {src} ya en reg={reg}", channel="regalloc")
                dump_reg_desc(self.reg_alloc.reg_desc)
                return reg

            # ⚠ TEMP SIN VALOR INICIAL → warning, lo inicializamos a 0 para evitar ERROR
            msg = f"WARN: temp {src} usado sin valor inicial - se inicializa a 0"
            mips_emitter.emitComment(msg)
            log(f"[getValueReg] {msg}", channel="regalloc")

            # obtenemos un registro para ese temp y lo llenamos con 0
            reg = self.reg_alloc.getRegFor(src, self.current_frame, mips_emitter)
            mips_emitter.emitInstr("li", reg, "0")
            self.reg_alloc.bindReg(reg, src)
            dump_reg_desc(self.reg_alloc.reg_desc)
            return reg

        # caso no soportado (otros símbolos, etc.)
        mips_emitter.emitComment(f"getValueReg: origen {src} no soportado")
        log(f"[getValueReg] origen NO SOPORTADO src={src}", channel="regalloc")
        return None

 
    def parseCondition(self, cond_str):
        # parsear formato tipo 't4>0' o 't4<=5'
        if cond_str is None:
            return None, None, None

        s = str(cond_str).replace(" ", "")
        ops = ["<=", ">=", "==", "!=", "<", ">"]

        for op in ops:
            idx = s.find(op)
            if idx != -1:
                left = s[:idx]
                right = s[idx + len(op):]
                return left, op, right

        # fallback: 't4' => t4 != 0
        return s, "!=", "0"

    def emitCondBranch(self, cond_txt, target_label, branch_on_true, mips_emitter):
        # parsear left, op, right desde la condición bruta
        left, op, right = self.parseCondition(cond_txt)
        if left is None or op is None:
            mips_emitter.emitComment(f"condición '{cond_txt}' no soportada")
            return

        mips_emitter.emitComment(
            f"emitCondBranch: raw='{cond_txt}' -> left='{left}', op='{op}', right='{right}', "
            f"branch_on_true={branch_on_true}"
        )

        # caso especial: temp usado como booleano (0/1) en comparaciones tipo tX > 0 o tX != 0
        if self.isTemp(left) and right == "0" and op in (">", "!="):
            reg_left = self.getValueReg(left, left, mips_emitter)
            mips_emitter.emitComment(
                f"emitCondBranch (bool-opt): usando {left} como booleano 0/1 en {reg_left}"
            )

            if branch_on_true:
                # salto si tX != 0
                mips_emitter.emitInstr("bne", reg_left, "$zero", target_label)
            else:
                # salto si tX == 0
                mips_emitter.emitInstr("beq", reg_left, "$zero", target_label)
            return

        # si es ifFalse, invertir el operador para reutilizar un único flujo
        if not branch_on_true:
            negate = {
                "==": "!=",
                "!=": "==",
                "<":  ">=",
                "<=": ">",
                ">":  "<=",
                ">=": "<",
            }
            old_op = op
            op = negate.get(op, op)
            mips_emitter.emitComment(f"emitCondBranch: negando operador {old_op} -> {op}")

        # cargar operandos: caso con inmediato en right y left no inmediato
        if self.isImmediate(right) and not self.isImmediate(left):
            # cargar left en registro (con hint si es temp)
            reg_left = self.getValueReg(
                left,
                left if self.isTemp(left) else None,
                mips_emitter
            )

            # right inmediato → usar $at para no clobber
            reg_right = "$at"
            mips_emitter.emitComment(
                f"emitCondBranch: right inmediato {right} -> {reg_right} (no pisa left)"
            )
            mips_emitter.emitInstr("li", reg_right, str(right))

        else:
            # camino genérico: cargar ambos operandos
            reg_left = self.getValueReg(
                left,
                left if self.isTemp(left) else None,
                mips_emitter
            )
            reg_right = self.getValueReg(
                right,
                right if self.isTemp(right) else None,
                mips_emitter
            )

        mips_emitter.emitComment(
            f"emitCondBranch: regs -> left={left} en {reg_left}, right={right} en {reg_right}"
        )

        if reg_left is None or reg_right is None:
            mips_emitter.emitComment(f"branch sobre '{cond_txt}' no soportado (operandos)")
            return

        # mapear operador lógico al branch mips correspondiente
        branch_map = {
            "==": "beq",
            "!=": "bne",
            "<":  "blt",
            "<=": "ble",
            ">":  "bgt",
            ">=": "bge",
        }
        br_op = branch_map.get(op)
        if br_op is None:
            mips_emitter.emitComment(f"operador de condición '{op}' no soportado en branch")
            return

        mips_emitter.emitComment(
            f"emitCondBranch: emitiendo {br_op} {reg_left}, {reg_right}, {target_label}"
        )
        mips_emitter.emitInstr(br_op, reg_left, reg_right, target_label)

    def lowerQuad(self, quad, mips_emitter):
        # log interno para depuración del lowering
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
        # arg1 contiene el nombre/label de la función
        func_label = quad.arg1

        # construir el frame layout para esta función
        frame_layout = self.frame_builder.buildForFunction(func_label)
        self.current_frame = frame_layout

        frame_size = int(frame_layout.frame_size or 0)
        if frame_size < 8:
            frame_size = 8  # espacio mínimo para fp y ra

        mips_emitter.emitLabel(func_label)
        mips_emitter.emitComment(f"prologo frame_size={frame_size}")

        # reservar espacio del frame en stack
        mips_emitter.emitInstr("addiu", "$sp", "$sp", f"-{frame_size}")

        # guardar ra y fp en ubicaciones precomputadas del frame
        mips_emitter.emitInstr("sw", "$ra", f"{frame_layout.saved_ra_offset}($sp)")
        mips_emitter.emitInstr("sw", "$fp", f"{frame_layout.saved_fp_offset}($sp)")

        # actualizar fp
        mips_emitter.emitInstr("move", "$fp", "$sp")

        # inicializar 'this' SOLO si el frame_layout expone un offset válido
        this_reg = getattr(self.machine_desc, "this_reg", None)
        this_offset = getattr(frame_layout, "this_param_offset", None)

        if this_reg is not None and this_offset is not None:
            # solo si el offset cae dentro del frame actual
            if 0 <= int(this_offset) < frame_size:
                mips_emitter.emitInstr("lw", this_reg, f"{this_offset}($fp)")
                mips_emitter.emitComment(
                    f"init this_reg={this_reg} desde fp[{this_offset}] (this_param_offset)"
                )
            else:
                mips_emitter.emitComment(
                    f"se omite init de this_reg={this_reg}: this_param_offset={this_offset} "
                    f"fuera de frame_size={frame_size}"
                )
        elif this_reg is not None:
            # sin this_param_offset asumimos que el caller carga 'this'
            mips_emitter.emitComment(
                f"this_reg={this_reg} definido pero sin this_param_offset en frame; "
                f"se asume que el caller inicializa 'this'"
            )

    def lowerLeave(self, quad, mips_emitter):
        if self.current_frame is None:
            # no hay frame activo, no-op
            mips_emitter.emitComment("epilogo sin frame (noop)")
            return

        frame_size = int(self.current_frame.frame_size or 0)
        if frame_size < 8:
            frame_size = 8

        mips_emitter.emitComment("epilogo")

        # restaurar sp al inicio del frame
        mips_emitter.emitInstr("move", "$sp", "$fp")

        # restaurar ra y fp
        mips_emitter.emitInstr("lw", "$ra", f"{self.current_frame.saved_ra_offset}($sp)")
        mips_emitter.emitInstr("lw", "$fp", f"{self.current_frame.saved_fp_offset}($sp)")

        # liberar todo el frame
        mips_emitter.emitInstr("addiu", "$sp", "$sp", f"{frame_size}")

        # salto al caller
        mips_emitter.emitInstr("jr", "$ra")

        self.current_frame = None

    # ---------- control de flujo ----------

    def lowerLabel(self, quad, mips_emitter):
        mips_emitter.emitLabel(quad.res)

    def lowerGoto(self, quad, mips_emitter):
        # salto incondicional usando helper del emitter
        target = quad.arg1
        mips_emitter.emitJump(target)

    def lowerIfGoto(self, quad, mips_emitter):
        # if cond goto label
        cond_txt = quad.arg1
        target = quad.arg2
        self.emitCondBranch(cond_txt, target, True, mips_emitter)

    def lowerIfFalseGoto(self, quad, mips_emitter):
        # ifFalse cond goto label
        cond_txt = quad.arg1
        target = quad.arg2
        self.emitCondBranch(cond_txt, target, False, mips_emitter)

    # ---------- expresiones / datos ----------

    def lowerAssign(self, quad, mips_emitter):
        dst_name = quad.res
        src = quad.arg1

        # obtener un registro con el valor de src
        src_reg = None

        if src == "R":
            # resultado de una llamada está en $v0
            src_reg = self.machine_desc.ret_regs[0]

        elif self.isImmediate(src):
            target_name = dst_name if dst_name is not None else str(src)
            src_reg = self.reg_alloc.getRegFor(target_name, self.current_frame, mips_emitter)
            mips_emitter.emitInstr("li", src_reg, str(src))

        else:
            # literal string en asignación: gp[0] := "texto"
            if isinstance(src, str) and len(src) >= 2 and src[0] == '"' and src[-1] == '"':
                text = src[1:-1]
                label = mips_emitter.internString(text)
                target_name = dst_name if dst_name is not None else label
                src_reg = self.reg_alloc.getRegFor(target_name, self.current_frame, mips_emitter)
                mips_emitter.emitInstr("la", src_reg, label)
                mips_emitter.emitComment(
                    f"assign literal string {src} -> {src_reg} (label={label})"
                )
            else:
                addr_src = self.parseAddress(src)
                if addr_src is not None:
                    base_reg, offset = addr_src
                    # si el destino es temp usamos su nombre para el registro
                    reg_name = dst_name if self.isTemp(dst_name) else f"{src}_tmp"
                    src_reg = self.reg_alloc.getRegFor(reg_name, self.current_frame, mips_emitter)
                    mips_emitter.emitInstr("lw", src_reg, f"{offset}({base_reg})")

                elif self.isTemp(src):
                    cand_regs = self.reg_alloc.reg_desc.valueRegs(src)
                    if cand_regs:
                        src_reg = cand_regs[0]
                    else:
                        # temp sin registro asignado
                        src_reg = self.reg_alloc.getRegFor(src, self.current_frame, mips_emitter)
                        mips_emitter.emitComment(f"valor de {src} no inicializado en registros")

                else:
                    # caso no soportado (otros símbolos)
                    mips_emitter.emitComment(f"assign {dst_name} := {src} (no soportado aún)")
                    return

        if dst_name is None:
            return

        # escribir el valor en el destino
        addr_dst = self.parseAddress(dst_name)

        if addr_dst is not None:
            base_reg, offset = addr_dst

            # protección: no pisar old $fp ni $ra
            if self.isProtectedFrameSlot(base_reg, offset):
                mips_emitter.emitComment(
                    f"assign a slot protegido fp[{offset}] (old fp/ra), se ignora"
                )
                return

            mips_emitter.emitInstr("sw", src_reg, f"{offset}({base_reg})")
            return

        if self.isTemp(dst_name):
            # asociar registro al temporal
            self.reg_alloc.bindReg(src_reg, dst_name)
            return

        # destino no soportado
        mips_emitter.emitComment(f"assign destino {dst_name} no soportado, valor en {src_reg}")


    def lowerBinary(self, quad, mips_emitter):
        dst_name = quad.res
        op = quad.label
        left = quad.arg1
        right = quad.arg2

        # --- inicializar set de temporales "tipo string" si no existe ---
        if not hasattr(self, "string_temps"):
            self.string_temps = set()

        # helper para saber si un temp tiene un registro vivo
        def temp_has_live_reg(name):
            if not (isinstance(name, str) and self.isTemp(name)):
                return False
            regs = self.reg_alloc.reg_desc.valueRegs(name)
            return bool(regs)

        # --- ¿es una operación de strings? (solo soportamos +) ---
        is_string_bin = (
            op == "+"
            and (
                self.isStringLiteral(left)
                or self.isStringLiteral(right)
                or (self.isTemp(left) and left in self.string_temps)
                or (self.isTemp(right) and right in self.string_temps)
            )
        )

        # --- CASO ESPECIAL: operaciones con strings ---
        if is_string_bin:
            # Elegimos una fuente razonable para inicializar dst:
            # 1) Operando no literal que además tenga registro vivo
            # 2) Operando no literal (aunque no tenga registro vivo)
            # 3) Si todo falla, el left (puede ser literal)
            candidates = [left, right]
            src_for_dst = None

            # 1) no literal + reg vivo
            for c in candidates:
                if not self.isStringLiteral(c) and temp_has_live_reg(c):
                    src_for_dst = c
                    break

            # 2) cualquier no literal
            if src_for_dst is None:
                for c in candidates:
                    if not self.isStringLiteral(c):
                        src_for_dst = c
                        break

            # 3) fallback: left
            if src_for_dst is None:
                src_for_dst = left

            if dst_name is not None and src_for_dst is not None:
                reg = self.getValueReg(
                    src_for_dst,
                    dst_name if self.isTemp(dst_name) else None,
                    mips_emitter
                )
                if reg is not None and self.isTemp(dst_name):
                    self.reg_alloc.bindReg(reg, dst_name)
                    # marcar destino como temp string
                    self.string_temps.add(dst_name)

            mips_emitter.emitComment(
                f"binary {dst_name} := {left} {op} {right} con strings "
                f"(concat simplificada: dst copia de {src_for_dst})"
            )
            return

        # ---------- CASO NORMAL (sin strings) ----------

        # obtener registros evitando que un inmediato en right pise left
        if self.isImmediate(right) and not self.isImmediate(left):
            reg_left = self.getValueReg(
                left,
                left if self.isTemp(left) else dst_name,
                mips_emitter
            )

            # right inmediato va a $at
            reg_right = "$at"
            mips_emitter.emitInstr("li", reg_right, str(right))
        else:
            # camino genérico para ambos operandos
            reg_right = self.getValueReg(
                right,
                right if self.isTemp(right) else None,
                mips_emitter
            )

            reg_left = self.getValueReg(
                left,
                left if self.isTemp(left) else dst_name,
                mips_emitter
            )

        # si no hay registros se aborta
        if reg_left is None or reg_right is None:
            mips_emitter.emitComment(f"binary {dst_name} := {left} {op} {right} (no soportado)")
            return

        # evitar que left y right queden en el mismo registro físico salvo que sea el mismo temp
        if (
            reg_right == reg_left
            and not (self.isTemp(left) and self.isTemp(right) and left == right)
        ):
            scratch = "$at"

            if self.isImmediate(right):
                reg_right = scratch
                mips_emitter.emitInstr("li", reg_right, str(right))

            else:
                addr_right = self.parseAddress(right)
                if addr_right is not None:
                    base_reg, offset = addr_right
                    reg_right = scratch
                    mips_emitter.emitInstr("lw", reg_right, f"{offset}({base_reg})")

                elif self.isTemp(right):
                    reg_right = scratch
                    mips_emitter.emitInstr("move", reg_right, reg_left)

                else:
                    mips_emitter.emitComment(f"binary: right={right} caso no soportado")

        # usar reg_left como destino
        dst_reg = reg_left

        arith_ops = {
            "+": "add",
            "-": "sub",
            "*": "mul",
            "/": "div",
            "%": "rem",
        }

        cmp_ops = {
            "==": "seq",
            "!=": "sne",
            "<":  "slt",
            "<=": "sle",
            ">":  "sgt",
            ">=": "sge",
        }

        # operación aritmética o comparación
        if op in arith_ops:
            mips_op = arith_ops[op]
            mips_emitter.emitInstr(mips_op, dst_reg, reg_left, reg_right)

        elif op in cmp_ops:
            mips_op = cmp_ops[op]
            mips_emitter.emitInstr(mips_op, dst_reg, reg_left, reg_right)

        else:
            mips_emitter.emitComment(f"operador binario '{op}' no soportado")
            return

        if dst_name is None:
            return

        # escribir el resultado
        addr_dst = self.parseAddress(dst_name)

        if addr_dst is not None:
            base_reg, offset = addr_dst

            if self.isProtectedFrameSlot(base_reg, offset):
                mips_emitter.emitComment(
                    f"binary: intento de escribir en slot protegido fp[{offset}] (old fp/ra), se ignora"
                )
                return

            mips_emitter.emitInstr("sw", dst_reg, f"{offset}({base_reg})")
            return

        if self.isTemp(dst_name):
            self.reg_alloc.bindReg(dst_reg, dst_name)
            return

        mips_emitter.emitComment(f"binary destino {dst_name} no soportado, valor en {dst_reg}")




    def lowerReturn(self, quad, mips_emitter):

        if quad.arg1 is None:
            # return sin valor
            mips_emitter.emitComment("return (sin valor)")
            return

        val = quad.arg1

        # obtener registro donde está el valor a retornar
        val_reg = self.getValueReg(
            val,
            val if self.isTemp(val) else None,
            mips_emitter
        )

        if val_reg is None:
            # valor no soportado todavía (ej: strings), no se toca $v0
            mips_emitter.emitComment(f"return {val} (no soportado aún, $v0 sin cambiar)")
            return

        ret_reg = self.machine_desc.ret_regs[0]  # normalmente $v0

        if val_reg != ret_reg:
            # mover el valor al registro de retorno si hace falta
            mips_emitter.emitInstr("move", ret_reg, val_reg)

        # log de return final
        mips_emitter.emitComment(f"return {val} -> {ret_reg}")

    # ---------- llamadas ----------

    def lowerParam(self, quad, mips_emitter):
        arg = quad.arg1

        # acumulamos el valor del parámetro hasta que se ejecute el call
        self.pending_params.append(arg)

        # comentar el param para trazabilidad en el código mips generado
        mips_emitter.emitComment(f"param {arg}")

    def lowerCall(self, quad, mips_emitter):
        # call: prepara args, hace jal y limpia stack
        func_label = quad.arg1
        n_args = int(quad.arg2) if quad.arg2 is not None else 0

        # aviso rápido si hay mismatch de parámetros
        if n_args != len(self.pending_params):
            mips_emitter.emitComment(
                f"call {func_label} n_args={n_args} (warning: pending_params={len(self.pending_params)})"
            )
        else:
            mips_emitter.emitComment(f"call {func_label} n_args={n_args}")

        # empujar params al stack en el orden recibido
        for arg in self.pending_params:
            reg = self.getValueReg(
                arg,
                arg if self.isTemp(arg) else None,
                mips_emitter
            )

            if reg is None:
                mips_emitter.emitComment(f"param {arg} no soportado (no se empuja)")
                continue

            # reservar espacio y guardar valor
            mips_emitter.emitInstr("addiu", "$sp", "$sp", "-4")
            mips_emitter.emitInstr("sw", reg, "0($sp)")

        # llamar a la función
        mips_emitter.emitInstr("jal", func_label)

        # limpiar args del stack (caller cleanup)
        if n_args > 0:
            total_bytes = 4 * n_args
            mips_emitter.emitInstr("addiu", "$sp", "$sp", str(total_bytes))

        # reset de lista de params
        self.pending_params = []

    # ---------- arreglos / objetos ----------

    def lowerIndexLoad(self, quad, mips_emitter):
        dst = quad.res
        base = quad.arg1
        idx = quad.arg2

        # Caso especial: sin índice -> equivale a un load simple
        if idx is None:
            addr = self.parseAddress(base)
            if addr is None:
                mips_emitter.emitComment(f"index_load {dst} := {base} (sin idx, base no soportada)")
                return

            base_reg, offset = addr

            # destino en registro o en memoria
            addr_dst = self.parseAddress(dst)
            if addr_dst is not None:
                # mem <- mem (necesita reg intermedio)
                tmp_reg = self.reg_alloc.getRegFor(f"{dst}_tmp", self.current_frame, mips_emitter)
                mips_emitter.emitInstr("lw", tmp_reg, f"{offset}({base_reg})")
                dst_base, dst_off = addr_dst
                mips_emitter.emitInstr("sw", tmp_reg, f"{dst_off}({dst_base})")
                return

            if self.isTemp(dst):
                dst_reg = self.reg_alloc.getRegFor(dst, self.current_frame, mips_emitter)
                mips_emitter.emitInstr("lw", dst_reg, f"{offset}({base_reg})")
                self.reg_alloc.bindReg(dst_reg, dst)
                return

            mips_emitter.emitComment(f"index_load destino {dst} no soportado")
            return

        # caso general: base[idx]

        # 1) registro base
        if isinstance(base, str) and base == "this":
            # asumimos que el descriptor de máquina tiene this_reg
            base_reg = getattr(self.machine_desc, "this_reg", None)
            if base_reg is None:
                mips_emitter.emitComment("index_load con 'this' pero machine_desc.this_reg no definido")
                return
        else:
            base_reg = self.getValueReg(base, base if self.isTemp(base) else None, mips_emitter)

        if base_reg is None:
            mips_emitter.emitComment(f"index_load {dst} := {base}[{idx}] (base no soportada)")
            return

        # 2) registro índice
        if self.isImmediate(idx):
            # índice literal: lo cargamos directo sin pasar por getValueReg
            idx_reg = self.reg_alloc.getRegFor(
                f"{dst}_idx_imm", self.current_frame, mips_emitter
            )
            mips_emitter.emitInstr("li", idx_reg, str(idx))
            mips_emitter.emitComment(
                f"index_load: idx inmediato {idx} -> {idx_reg}"
            )
        else:
            idx_reg = self.getValueReg(
                idx,
                idx if self.isTemp(idx) else None,
                mips_emitter,
            )

        if idx_reg is None:
            mips_emitter.emitComment(f"index_load {dst} := {base}[{idx}] (idx sin valor)")
            return

        offset_reg = self.reg_alloc.getRegFor(f"{dst}_idx_off", self.current_frame, mips_emitter)
        mips_emitter.emitInstr("move", offset_reg, idx_reg)

        # addr = base + offset
        addr_reg = self.reg_alloc.getRegFor(f"{dst}_addr", self.current_frame, mips_emitter)
        mips_emitter.emitInstr("add", addr_reg, base_reg, offset_reg)

        # 5) cargar en destino
        addr_dst = self.parseAddress(dst)
        if addr_dst is not None:
            # mem <- *(base+idx*4) usando reg temporal
            tmp_reg = self.reg_alloc.getRegFor(f"{dst}_tmp", self.current_frame, mips_emitter)
            mips_emitter.emitInstr("lw", tmp_reg, f"0({addr_reg})")
            dst_base, dst_off = addr_dst
            mips_emitter.emitInstr("sw", tmp_reg, f"{dst_off}({dst_base})")
            return

        if self.isTemp(dst):
            dst_reg = self.reg_alloc.getRegFor(dst, self.current_frame, mips_emitter)
            mips_emitter.emitInstr("lw", dst_reg, f"0({addr_reg})")
            self.reg_alloc.bindReg(dst_reg, dst)
            return

        mips_emitter.emitComment(f"index_load destino {dst} no soportado, valor queda en memoria")

    def lowerIndexStore(self, quad, mips_emitter):
        base = quad.arg1
        idx = quad.arg2 if quad.arg2 is not None else quad.label
        src = quad.res

        # Caso especial: sin índice -> store simple base[offset] := src
        if idx is None:
            addr = self.parseAddress(base)
            if addr is None:
                mips_emitter.emitComment(
                    f"index_store {base} := {src} (sin idx, base no soportada)"
                )
                return

            base_reg, offset = addr
            src_reg = self.getValueReg(
                src,
                src if self.isTemp(src) else None,
                mips_emitter
            )
            if src_reg is None:
                mips_emitter.emitComment(
                    f"index_store {base} := {src} (src no soportado)"
                )
                return

            if self.isProtectedFrameSlot(base_reg, offset):
                mips_emitter.emitComment(
                    f"index_store {base} := {src} intenta escribir en slot protegido "
                    f"fp[{offset}], se ignora"
                )
                return

            mips_emitter.emitInstr("sw", src_reg, f"{offset}({base_reg})")
            return

        # ---------- caso general: base[idx] := src ----------

        # 1) registro base
        if isinstance(base, str) and base == "this":
            base_reg = getattr(self.machine_desc, "this_reg", None)
            if base_reg is None:
                mips_emitter.emitComment(
                    "index_store con 'this' pero machine_desc.this_reg no definido"
                )
                return
        else:
            base_reg = self.getValueReg(
                base,
                base if self.isTemp(base) else None,
                mips_emitter
            )

        if base_reg is None:
            mips_emitter.emitComment(
                f"index_store {base}[{idx}] := {src} (base no soportada)"
            )
            return

        # 2) registro índice
        if self.isImmediate(idx):
            idx_reg = self.reg_alloc.getRegFor(
                f"{src}_idx_imm", self.current_frame, mips_emitter
            )
            mips_emitter.emitInstr("li", idx_reg, str(idx))
            mips_emitter.emitComment(
                f"index_store: idx inmediato {idx} -> {idx_reg}"
            )
        else:
            idx_reg = self.getValueReg(
                idx,
                idx if self.isTemp(idx) else None,
                mips_emitter,
            )

        if idx_reg is None:
            mips_emitter.emitComment(
                f"index_store {base}[{idx}] := {src} (idx sin valor)"
            )
            return

        # 3) offset = idx (según TAC actual, sin escalar)
        offset_reg = self.reg_alloc.getRegFor(
            f"{src}_idx_off", self.current_frame, mips_emitter
        )
        mips_emitter.emitInstr("move", offset_reg, idx_reg)

        # 4) addr = base + offset
        addr_reg = self.reg_alloc.getRegFor(
            f"{src}_addr", self.current_frame, mips_emitter
        )
        mips_emitter.emitInstr("add", addr_reg, base_reg, offset_reg)

        # 5) valor a guardar
        src_reg = self.getValueReg(
            src,
            src if self.isTemp(src) else None,
            mips_emitter
        )
        if src_reg is None:
            mips_emitter.emitComment(
                f"index_store {base}[{idx}] := {src} (src no soportado)"
            )
            return

        # ⚠️ FIX REAL: evitar sw $reg, 0($reg) usando scratch físico $t9
        if src_reg == addr_reg:
            scratch = "$t9"   # registro físico reservado como scratch
            mips_emitter.emitInstr("move", scratch, src_reg)
            mips_emitter.emitComment(
                f"index_store: src_reg == addr_reg ({src_reg}), usando scratch={scratch} "
                f"para evitar sw {src_reg}, 0({src_reg})"
            )
            src_reg = scratch

        mips_emitter.emitInstr("sw", src_reg, f"0({addr_reg})")

    def lowerNewObj(self, quad, mips_emitter):
        # preparar datos básicos
        dst = quad.res
        class_name = quad.arg1
        size = quad.arg2 if quad.arg2 is not None else 0

        mips_emitter.emitComment(
            f"newobj {dst} = newobj {class_name}, size={size}"
        )

        # cargar size en un registro
        size_reg = None
        if self.isImmediate(size):
            size_reg = self.reg_alloc.getRegFor(
                f"{dst}_size" if dst is not None else "newobj_size",
                self.current_frame,
                mips_emitter,
            )
            mips_emitter.emitInstr("li", size_reg, str(size))
        else:
            size_reg = self.getValueReg(size, None, mips_emitter)

        if size_reg is None:
            mips_emitter.emitComment(
                f"newobj {dst}: size={size} no soportado (no se llama a __newobj)"
            )
            return

        # push del parámetro size
        mips_emitter.emitInstr("addiu", "$sp", "$sp", "-4")
        mips_emitter.emitInstr("sw", size_reg, "0($sp)")

        # llamar al runtime allocator
        mips_emitter.emitInstr("jal", "__newobj")

        # limpiar parámetro
        mips_emitter.emitInstr("addiu", "$sp", "$sp", "4")

        # $v0 contiene el puntero
        ret_reg = self.machine_desc.ret_regs[0]

        if dst is None:
            mips_emitter.emitComment("newobj sin destino, puntero en $v0")
            return

        addr_dst = self.parseAddress(dst)

        if addr_dst is not None:
            # almacenar en memoria
            base_reg, offset = addr_dst
            mips_emitter.emitInstr("sw", ret_reg, f"{offset}({base_reg})")
            return

        if self.isTemp(dst):
            # asociar retorno al temporal
            self.reg_alloc.bindReg(ret_reg, dst)
            mips_emitter.emitComment(
                f"newobj: puntero -> temp {dst} en {ret_reg}"
            )
            return

        # destino no soportado
        mips_emitter.emitComment(
            f"newobj destino {dst} no soportado, puntero queda en {ret_reg}"
        )
