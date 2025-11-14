# src/cg/instruction.py
import re
from logs.logger import log
from cg.stack_frame import StackFrame
from cg.mips_emitter import MipsEmitter

# patrones básicos
int_re = re.compile(r"-?\d+$")
temp_re = re.compile(r"\bt\d+\b")
fp_loc_re = re.compile(r"^fp\[(\d+)\]$")
gp_loc_re = re.compile(r"^gp\[(\d+)\]$")
this_loc_re = re.compile(r"^this\[(.+)\]$")


def isIntToken(text: str) -> bool:
    return int_re.fullmatch(text.strip()) is not None


def isTemp(text: str) -> bool:
    return temp_re.fullmatch(text.strip()) is not None


def isFpSlot(text: str) -> bool:
    return fp_loc_re.fullmatch(text.strip()) is not None


def isGpSlot(text: str) -> bool:
    return gp_loc_re.fullmatch(text.strip()) is not None


def isThisSlot(text: str) -> bool:
    return this_loc_re.fullmatch(text.strip()) is not None


def isRToken(text: str) -> bool:
    return text.strip() == "R"


def parseFpOffset(text: str) -> int | None:
    m = fp_loc_re.fullmatch(text.strip())
    if not m:
        return None
    return int(m.group(1))


def parseThisIndex(text: str) -> str | None:
    m = this_loc_re.fullmatch(text.strip())
    if not m:
        return None
    return m.group(1).strip()


def emitLoadValue(
    emitter: MipsEmitter, frame: StackFrame, operand: str, target_reg: str
) -> None:
    operand = operand.strip()

    if isTemp(operand):
        frame.loadTemp(emitter, operand, target_reg)
        return

    if isFpSlot(operand):
        offset = parseFpOffset(operand)
        emitter.emitText(f"    lw {target_reg}, {offset}($fp)")
        return

    if isIntToken(operand):
        emitter.emitText(f"    li {target_reg}, {operand}")
        return

    if isGpSlot(operand):
        emitter.emitText(f"    # gp slot no soportado aun: {operand}, usando 0")
        emitter.emitText(f"    li {target_reg}, 0")
        log(f"[cg] gp no soportado como operand: {operand}", channel="cg")
        return

    if isThisSlot(operand):
        # this[...] como rvalue directo (poco común en expr, pero lo manejamos)
        index_expr = parseThisIndex(operand)
        if index_expr is None:
            emitter.emitText(f"    # this[] invalido: {operand}, usando 0")
            emitter.emitText(f"    li {target_reg}, 0")
            log(f"[cg] this invalido: {operand}", channel="cg")
            return
        # index a $t3
        emitLoadValue(emitter, frame, index_expr, "$t3")
        emitter.emitText("    addu $t3, $s0, $t3")
        emitter.emitText(f"    lw {target_reg}, 0($t3)")
        return

    emitter.emitText(f"    # operand no soportado, usando 0: {operand}")
    emitter.emitText(f"    li {target_reg}, 0")
    log(f"[cg] operand no soportado: {operand}", channel="cg")


def emitStoreValue(
    emitter: MipsEmitter, frame: StackFrame, dest: str, source_reg: str
) -> None:
    dest = dest.strip()

    if isTemp(dest):
        frame.storeTemp(emitter, dest, source_reg)
        return

    if isFpSlot(dest):
        offset = parseFpOffset(dest)
        emitter.emitText(f"    sw {source_reg}, {offset}($fp)")
        return

    if isGpSlot(dest):
        emitter.emitText(f"    # gp slot no soportado para store: {dest}")
        log(f"[cg] gp no soportado como destino: {dest}", channel="cg")
        return

    if isThisSlot(dest):
        index_expr = parseThisIndex(dest)
        if index_expr is None:
            emitter.emitText(f"    # this[] invalido para store: {dest}")
            log(f"[cg] this invalido para store: {dest}", channel="cg")
            return
        # index a $t3
        emitLoadValue(emitter, frame, index_expr, "$t3")
        emitter.emitText("    addu $t3, $s0, $t3")
        emitter.emitText(f"    sw {source_reg}, 0($t3)")
        return

    emitter.emitText(f"    # destino no soportado para store: {dest}")
    log(f"[cg] destino no soportado: {dest}", channel="cg")


def translateAssign(
    emitter: MipsEmitter, frame: StackFrame, dest: str, expr: str
) -> None:
    expr = expr.strip()
    dest = dest.strip()

    # tX := R (resultado de llamada, viene en $v0)
    if isRToken(expr):
        emitter.emitText("    move $t0, $v0")
        emitStoreValue(emitter, frame, dest, "$t0")
        return

    # tX := this[tY]
    if isThisSlot(expr):
        index_expr = parseThisIndex(expr)
        if index_expr is None:
            emitter.emitText(f"    # this[] invalido en asignacion: {expr}")
            log(f"[cg] this invalido en asignacion: {expr}", channel="cg")
            return
        emitLoadValue(emitter, frame, index_expr, "$t3")
        emitter.emitText("    addu $t3, $s0, $t3")
        emitter.emitText("    lw $t0, 0($t3)")
        emitStoreValue(emitter, frame, dest, "$t0")
        return

    # casos simples: int, temp, fp slot
    if isIntToken(expr) or isTemp(expr) or isFpSlot(expr):
        emitLoadValue(emitter, frame, expr, "$t0")
        emitStoreValue(emitter, frame, dest, "$t0")
        return

    emitter.emitText(f"    # asignacion TAC no soportada aun: {dest} := {expr}")
    log(f"[cg] assign no soportado: {dest} := {expr}", channel="cg")


def translateBinOp(
    emitter: MipsEmitter,
    frame: StackFrame,
    dest: str,
    left: str,
    op: str,
    right: str,
) -> None:
    left = left.strip()
    right = right.strip()
    dest = dest.strip()

    emitLoadValue(emitter, frame, left, "$t0")
    emitLoadValue(emitter, frame, right, "$t1")

    if op == "+":
        emitter.emitText("    add $t2, $t0, $t1")
    elif op == "-":
        emitter.emitText("    sub $t2, $t0, $t1")
    elif op == "*":
        emitter.emitText("    mul $t2, $t0, $t1")
    elif op == "/":
        emitter.emitText("    div $t0, $t1")
        emitter.emitText("    mflo $t2")
    else:
        emitter.emitText(f"    # operador binario no soportado: {op}")
        emitter.emitText("    move $t2, $t0")
        log(f"[cg] operador no soportado: {op}", channel="cg")

    emitStoreValue(emitter, frame, dest, "$t2")


def translateReturn(
    emitter: MipsEmitter, frame: StackFrame, func_name: str, expr: str
) -> None:
    expr = expr.strip()

    if expr == "":
        emitter.emitText("    # return sin valor, v0 = 0")
        emitter.emitText("    li $v0, 0")
        emitter.emitText(f"    j {func_name}_end")
        return

    if isIntToken(expr) or isTemp(expr) or isFpSlot(expr):
        emitLoadValue(emitter, frame, expr, "$v0")
        emitter.emitText(f"    j {func_name}_end")
        return

    emitter.emitText("    # return expr no soportado, devolviendo 0")
    emitter.emitText("    li $v0, 0")
    emitter.emitText(f"    j {func_name}_end")
    log(f"[cg] return no soportado: {expr}", channel="cg")


# ---------- llamadas: PARAM / CALL ----------

def translateParam(
    emitter: MipsEmitter,
    frame: StackFrame,
    operand: str,
    arg_state: dict,
) -> None:
    # PARAM x: cargar x a $t0, hacer push en stack.
    emitLoadValue(emitter, frame, operand, "$t0")
    emitter.emitText("    addi $sp, $sp, -4")
    emitter.emitText("    sw $t0, 0($sp)")
    arg_state["pending"] = arg_state.get("pending", 0) + 1
    log(f"[cg] PARAM {operand}, pending={arg_state['pending']}", channel="cg")


def translateCall(
    emitter: MipsEmitter,
    frame: StackFrame,
    func_name: str,
    arg_count: int,
    arg_state: dict,
) -> None:
    pending = arg_state.get("pending", 0)
    if pending != arg_count:
        log(
            f"[cg] WARNING: CALL {func_name}, arg_count={arg_count}, "
            f"pending={pending}",
            channel="cg",
        )

    # primer argumento es this (si aplica): está más "arriba" en el stack
    if arg_count >= 1:
        offset = (arg_count - 1) * 4
        emitter.emitText(f"    lw $s0, {offset}($sp)")
        emitter.emitText("    # this cargado en $s0 (primer argumento)")

    emitter.emitText(f"    jal {func_name}")

    if arg_count > 0:
        emitter.emitText(f"    addi $sp, $sp, {arg_count * 4}")

    arg_state["pending"] = 0
    log(f"[cg] CALL {func_name} ({arg_count} args)", channel="cg")


# ---------- control de flujo: IF / GOTO ----------

_rel_re = re.compile(r"^\s*(.+?)\s*([><=!]=?|<=|>=)\s*(.+?)\s*$")


def translateGoto(emitter: MipsEmitter, label: str) -> None:
    emitter.emitText(f"    j {label}")


def translateIfGoto(
    emitter: MipsEmitter,
    frame: StackFrame,
    cond_expr: str,
    label: str,
) -> None:
    """
    Soportamos por ahora el patrón que ya usas:
       IF t4 > 0 GOTO L
    """
    m = _rel_re.match(cond_expr)
    if not m:
        emitter.emitText(f"    # IF no soportado: {cond_expr}")
        log(f"[cg] IF no soportado: {cond_expr}", channel="cg")
        return

    left, op, right = m.groups()
    left = left.strip()
    right = right.strip()

    emitLoadValue(emitter, frame, left, "$t0")
    emitLoadValue(emitter, frame, right, "$t1")

    # caso especial muy común:  x > 0  -> bgtz x,label
    if op == ">" and isIntToken(right) and int(right) == 0:
        emitter.emitText(f"    bgtz $t0, {label}")
        return

    # fallback básico: left - right > 0
    emitter.emitText("    sub $t2, $t0, $t1")
    if op == ">":
        emitter.emitText(f"    bgtz $t2, {label}")
    else:
        emitter.emitText(
            f"    # operador relacional no soportado aun: {op}, se ignora salto"
        )
        log(f"[cg] operador relacional no soportado: {op}", channel="cg")
