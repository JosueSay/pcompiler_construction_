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
            reg = self.reg_alloc.getRegFor(src, self.current_frame, mips_emitter)
            mips_emitter.emitComment(
                f"getValueReg: src={src} (temp nuevo) -> {reg} (sin valor inicial)"
            )
            log(f"[getValueReg] TEMP NUEVO {src} -> reg={reg}", channel="regalloc")
            dump_reg_desc(self.reg_alloc.reg_desc)
            dump_addr_desc(self.reg_alloc.addr_desc)
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
        # leer left, op, right
        left, op, right = self.parseCondition(cond_txt)
        if left is None or op is None:
            mips_emitter.emitComment(f"condición '{cond_txt}' no soportada")
            return

        mips_emitter.emitComment(
            f"emitCondBranch: raw='{cond_txt}' -> left='{left}', op='{op}', right='{right}', "
            f"branch_on_true={branch_on_true}"
        )

        # --- CASO ESPECIAL: booleano tX > 0 ó tX != 0 ---
        # Nuestro TAC genera cosas como: IF t4 > 0 GOTO L,
        # donde t4 ya es 0/1 (resultado de una comparación previa).
        if self.isTemp(left) and right == "0" and op in (">", "!="):
            reg_left = self.getValueReg(left, left, mips_emitter)
            mips_emitter.emitComment(
                f"emitCondBranch (bool-opt): usando {left} como booleano 0/1 en {reg_left}"
            )

            if branch_on_true:
                # if t4 > 0  => branch si t4 != 0
                mips_emitter.emitInstr("bne", reg_left, "$zero", target_label)
            else:
                # ifFalse t4 > 0 => branch si t4 == 0
                mips_emitter.emitInstr("beq", reg_left, "$zero", target_label)
            return
        # --- FIN CASO ESPECIAL ---

        # invertir operador cuando es ifFalse (caso genérico)
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

        # cargar operandos en registros (camino genérico)
        reg_left = self.getValueReg(left, left if self.isTemp(left) else None, mips_emitter)
        reg_right = self.getValueReg(right, right if self.isTemp(right) else None, mips_emitter)

        mips_emitter.emitComment(
            f"emitCondBranch: regs -> left={left} en {reg_left}, right={right} en {reg_right}"
        )

        if reg_left is None or reg_right is None:
            mips_emitter.emitComment(f"branch sobre '{cond_txt}' no soportado (operandos)")
            return

        # mapear operador a instrucción MIPS
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
        
        # inicializar 'this' desde el primer parámetro en fp[16]
        this_reg = getattr(self.machine_desc, "this_reg", None)
        if this_reg is not None:
            mips_emitter.emitInstr("lw", this_reg, "16($fp)")
            mips_emitter.emitComment(
                f"init this_reg={this_reg} desde fp[16] (convención actual de 'this')"
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

        # =========================
        # 1) OBTENER REGISTROS
        #    → primero RIGHT, luego LEFT
        # =========================
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

        if reg_left is None or reg_right is None:
            mips_emitter.emitComment(
                f"binary {dst_name} := {left} {op} {right} (no soportado: operandos)"
            )
            return

        # Pequeño comentario para debug
        mips_emitter.emitComment(
            f"lowerBinary: left={left}({reg_left}), right={right}({reg_right}), op={op}"
        )

        # --------- CASO STRINGS (concat "fake" todavía) ---------
        if (
            isinstance(left, str) and left.startswith('"') and left.endswith('"')
        ) or (
            isinstance(right, str) and right.startswith('"') and right.endswith('"')
        ):
            dst_reg = reg_left

            if dst_name is None:
                mips_emitter.emitComment(
                    f"binary string {left} {op} {right} -> resultado en {dst_reg} (sin concat real)"
                )
                return

            addr_dst = self.parseAddress(dst_name)
            if addr_dst is not None:
                dst_base, dst_off = addr_dst
                mips_emitter.emitInstr("sw", dst_reg, f"{dst_off}({dst_base})")
                mips_emitter.emitComment(
                    f"binary string (store) {left} {op} {right} -> {dst_name} via {dst_reg}"
                )
                return

            if self.isTemp(dst_name):
                self.reg_alloc.bindReg(dst_reg, dst_name)
                mips_emitter.emitComment(
                    f"binary string (temp) {left} {op} {right} -> {dst_name} en {dst_reg}"
                )
                return

            mips_emitter.emitComment(
                f"binary string destino {dst_name} no soportado, valor en {dst_reg}"
            )
            return

        # --------- CASO NUMÉRICO / COMPARACIONES ---------

        # Evitar que left y right usen el MISMO registro físico
        # salvo que sea el mismo temporal (t0 + t0 es válido).
        if (
            reg_right == reg_left
            and not (self.isTemp(left) and self.isTemp(right) and left == right)
        ):
            # Usamos un registro de hardware que el allocator NO usa ($at)
            scratch = "$at"
            mips_emitter.emitComment(
                f"binary: left/right comparten {reg_left}, forzando right en {scratch}"
            )

            if self.isImmediate(right):
                # right es un inmediato: recargar en $at
                reg_right = scratch
                mips_emitter.emitInstr("li", reg_right, str(right))

            else:
                addr_right = self.parseAddress(right)
                if addr_right is not None:
                    # right es algo tipo fp[...] / gp[...] : recargar desde memoria en $at
                    base_reg, offset = addr_right
                    reg_right = scratch
                    mips_emitter.emitInstr("lw", reg_right, f"{offset}({base_reg})")

                elif self.isTemp(right):
                    # right es un temp distinto a left pero quedó en el mismo reg.
                    # (si el allocator lo hace, al menos separamos en scratch)
                    reg_right = scratch
                    mips_emitter.emitInstr("move", reg_right, reg_left)

                else:
                    # Caso raro: símbolo no soportado; dejamos comentario.
                    mips_emitter.emitComment(
                        f"binary: right={right} con reg compartido {reg_left}, caso no soportado"
                    )

        # reutilizamos reg_left como destino físico
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

        if op in arith_ops:
            mips_op = arith_ops[op]
            mips_emitter.emitInstr(mips_op, dst_reg, reg_left, reg_right)

        elif op in cmp_ops:
            mips_op = cmp_ops[op]
            mips_emitter.emitInstr(mips_op, dst_reg, reg_left, reg_right)

        else:
            # operador aún no soportado
            mips_emitter.emitComment(f"operador binario '{op}' no soportado aún")
            return

        if dst_name is None:
            return

        # escribir el resultado
        addr_dst = self.parseAddress(dst_name)

        if addr_dst is not None:
            base_reg, offset = addr_dst
            mips_emitter.emitInstr("sw", dst_reg, f"{offset}({base_reg})")
            return

        if self.isTemp(dst_name):
            # asociar registro al destino temporal
            self.reg_alloc.bindReg(dst_reg, dst_name)
            return

        # destino no soportado
        mips_emitter.emitComment(
            f"binary destino {dst_name} no soportado, valor en {dst_reg}"
        )




    def lowerReturn(self, quad, mips_emitter):
        """
        RETURN x:
          - Calcula el valor de x en algún registro.
          - Lo mueve (si hace falta) a $v0.
          - El epílogo/jr $ra lo hace lowerLeave.
        """
        if quad.arg1 is None:
            mips_emitter.emitComment("return (sin valor)")
            return

        val = quad.arg1

        # obtener registro con el valor a retornar
        val_reg = self.getValueReg(
            val,
            val if self.isTemp(val) else None,
            mips_emitter
        )

        if val_reg is None:
            # típicamente pasará con strings (aún no soportados)
            mips_emitter.emitComment(f"return {val} (no soportado aún, $v0 sin cambiar)")
            return

        ret_reg = self.machine_desc.ret_regs[0]  # normalmente '$v0'

        if val_reg != ret_reg:
            mips_emitter.emitInstr("move", ret_reg, val_reg)

        mips_emitter.emitComment(f"return {val} -> {ret_reg}")


    # ---------- llamadas ----------

    def lowerParam(self, quad, mips_emitter):
        """
        PARAM x:
          - Solo acumulamos el valor de x en una lista.
          - El push real a stack se hace en CALL.
        """
        arg = quad.arg1
        self.pending_params.append(arg)
        mips_emitter.emitComment(f"param {arg}")


    def lowerCall(self, quad, mips_emitter):
        """
        CALL f, n:
          - Empuja los parámetros acumulados en pending_params al stack,
            en el orden en que llegaron los PARAM.
          - Llama a la función con jal.
          - Limpia el stack (caller limpia argumentos).
          - El valor de retorno queda en $v0 (pseudo 'R').
        """
        func_label = quad.arg1
        n_args = int(quad.arg2) if quad.arg2 is not None else 0

        # sanity: si hay mismatch, solo lo dejamos en comentario
        if n_args != len(self.pending_params):
            mips_emitter.emitComment(
                f"call {func_label} n_args={n_args} "
                f"(warning: pending_params={len(self.pending_params)})"
            )
        else:
            mips_emitter.emitComment(f"call {func_label} n_args={n_args}")

        # 1) Empujar parámetros al stack en el orden de los PARAM
        #    (param1 primero, paramN último)
        for arg in self.pending_params:
            # obtener registro con el valor del argumento
            reg = self.getValueReg(
                arg,
                arg if self.isTemp(arg) else None,
                mips_emitter
            )

            if reg is None:
                mips_emitter.emitComment(f"param {arg} no soportado (no se empuja)")
                continue

            # hacer espacio en el stack y guardar el valor
            mips_emitter.emitInstr("addiu", "$sp", "$sp", "-4")
            mips_emitter.emitInstr("sw", reg, "0($sp)")

        # 2) Llamar a la función
        mips_emitter.emitInstr("jal", func_label)

        # 3) Limpiar los argumentos del stack (caller-cleanup)
        if n_args > 0:
            total_bytes = 4 * n_args
            mips_emitter.emitInstr("addiu", "$sp", "$sp", str(total_bytes))

        # 4) Limpiar la lista de parámetros pendientes
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

        # ----------- Caso general: base[idx] -----------

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
        idx_reg = self.getValueReg(idx, None, mips_emitter)
        if idx_reg is None:
            mips_emitter.emitComment(f"index_load {dst} := {base}[{idx}] (idx no soportado)")
            return

        # En nuestro TAC actual, idx YA es un offset en bytes (0, 8, 12, 20, 16, 24...),
        # así que no lo escalamos por word_size, solo lo usamos directo.
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

        # Caso especial: sin índice -> equivale a store simple
        if idx is None:
            addr = self.parseAddress(base)
            if addr is None:
                mips_emitter.emitComment(f"index_store {base} := {src} (sin idx, base no soportada)")
                return

            base_reg, offset = addr
            src_reg = self.getValueReg(
                src,
                src if self.isTemp(src) else None,
                mips_emitter
            )
            if src_reg is None:
                mips_emitter.emitComment(f"index_store {base} := {src} (src no soportado)")
                return

            mips_emitter.emitInstr("sw", src_reg, f"{offset}({base_reg})")
            return

        # ----------- Caso general: base[idx] := src -----------

        # 1) registro base
        if isinstance(base, str) and base == "this":
            base_reg = getattr(self.machine_desc, "this_reg", None)
            if base_reg is None:
                mips_emitter.emitComment("index_store con 'this' pero machine_desc.this_reg no definido")
                return
        else:
            base_reg = self.getValueReg(base, base if self.isTemp(base) else None, mips_emitter)

        if base_reg is None:
            mips_emitter.emitComment(f"index_store {base}[{idx}] := {src} (base no soportada)")
            return

        # 2) registro índice
        idx_reg = self.getValueReg(idx, None, mips_emitter)
        if idx_reg is None:
            mips_emitter.emitComment(f"index_store {base}[{idx}] := {src} (idx no soportado)")
            return

        # En nuestro TAC actual, idx es offset en bytes, no índice.
        offset_reg = self.reg_alloc.getRegFor(f"{src}_idx_off", self.current_frame, mips_emitter)
        mips_emitter.emitInstr("move", offset_reg, idx_reg)

        # addr = base + offset
        addr_reg = self.reg_alloc.getRegFor(f"{src}_addr", self.current_frame, mips_emitter)
        mips_emitter.emitInstr("add", addr_reg, base_reg, offset_reg)

        # 5) valor a guardar
        src_reg = self.getValueReg(
            src,
            src if self.isTemp(src) else None,
            mips_emitter
        )
        if src_reg is None:
            mips_emitter.emitComment(f"index_store {base}[{idx}] := {src} (src no soportado)")
            return

        mips_emitter.emitInstr("sw", src_reg, f"0({addr_reg})")


    def lowerNewObj(self, quad, mips_emitter):
        """
        NEWOBJ dst = newobj ClassName, size:
          - Por ahora delegamos la reserva real a una rutina de runtime __newobj(size).
          - __newobj debe:
              * recibir 'size' (bytes) en stack como único parámetro,
              * devolver en $v0 un puntero al bloque reservado.
          - Aquí solo:
              * preparamos el parámetro (size),
              * llamamos a __newobj,
              * dejamos el puntero en 'dst' (temp o gp[...]).
        """
        dst = quad.res
        class_name = quad.arg1
        size = quad.arg2 if quad.arg2 is not None else 0

        mips_emitter.emitComment(
            f"newobj {dst} = newobj {class_name}, size={size}"
        )

        # 1) size en un registro
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

        # 2) push del parámetro size
        mips_emitter.emitInstr("addiu", "$sp", "$sp", "-4")
        mips_emitter.emitInstr("sw", size_reg, "0($sp)")

        # 3) llamada al runtime allocator
        mips_emitter.emitInstr("jal", "__newobj")

        # 4) limpiar el parámetro del stack (caller-cleanup)
        mips_emitter.emitInstr("addiu", "$sp", "$sp", "4")

        # 5) resultado está en $v0
        ret_reg = self.machine_desc.ret_regs[0]

        if dst is None:
            # Nada que hacer, puntero queda en $v0
            mips_emitter.emitComment("newobj sin destino explícito, puntero en $v0")
            return

        addr_dst = self.parseAddress(dst)

        if addr_dst is not None:
            # gp[16] := puntero
            base_reg, offset = addr_dst
            mips_emitter.emitInstr("sw", ret_reg, f"{offset}({base_reg})")
            return

        if self.isTemp(dst):
            # asociar el registro de retorno al temporal dst
            self.reg_alloc.bindReg(ret_reg, dst)
            mips_emitter.emitComment(
                f"newobj: puntero resultado -> temp {dst} en {ret_reg}"
            )
            return

        # cualquier otro destino aún no soportado
        mips_emitter.emitComment(
            f"newobj destino {dst} no soportado, puntero queda en {ret_reg}"
        )
