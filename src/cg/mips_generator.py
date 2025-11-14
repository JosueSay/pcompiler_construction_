import re
from typing import List

from logs.logger import log, addChannel
from cg.mips_emitter import MipsEmitter
from cg.stack_frame import StackFrame
from cg.instruction import (
    translateAssign,
    translateBinOp,
    translateReturn,
    translateParam,
    translateCall,
    translateIfGoto,
    translateGoto,
    temp_re,
)

func_re = re.compile(r"^\s*FUNCTION\s+([A-Za-z_][A-Za-z0-9_]*)\s*:")
end_func_re = re.compile(r"^\s*END\s+FUNCTION")
assign_re = re.compile(r"^\s*(.+?)\s*:=\s*(.+)$")
binop_re = re.compile(r"^\s*(.+?)\s*:=\s*(.+)\s*([+\-*/])\s*(.+)\s*$")
return_re = re.compile(r"^\s*RETURN\s+(.+)$")

label_re = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:$")
goto_re = re.compile(r"^GOTO\s+([A-Za-z_][A-Za-z0-9_]*)\s*$")
if_goto_re = re.compile(r"^IF\s+(.+)\s+GOTO\s+([A-Za-z_][A-Za-z0-9_]*)\s*$")
param_re = re.compile(r"^PARAM\s+(.+)$")
call_re = re.compile(r"^CALL\s+([A-Za-z_][A-Za-z0-9_]*),\s*(\d+)\s*$")


class FunctionTac:
    def __init__(self, name: str):
        self.name = name
        self.body_lines: List[str] = []
        self.temps: set[str] = set()

    def registerLine(self, line: str) -> None:
        self.body_lines.append(line)
        for t in temp_re.findall(line):
            self.temps.add(t)


def parseTacFunctions(tac_path: str) -> List[FunctionTac]:
    functions: List[FunctionTac] = []
    current_func: FunctionTac | None = None
    main_created = False

    with open(tac_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")

            # inicio de función explícita
            m_func = func_re.match(line)
            if m_func:
                func_name = m_func.group(1)
                current_func = FunctionTac(func_name)
                functions.append(current_func)
                log(f"[cg] FUNCTION {func_name}", channel="cg")
                continue

            # fin de función explícita
            if end_func_re.match(line):
                log("[cg] END FUNCTION", channel="cg")
                current_func = None
                continue

            # línea de comentario o vacía
            stripped = line.strip()
            if not stripped or stripped.startswith(";"):
                if current_func is not None:
                    current_func.registerLine(line)
                continue

            # si no estamos en función y aparece código, lo metemos en un main sintético
            if current_func is None and not main_created:
                current_func = FunctionTac("main")
                functions.append(current_func)
                main_created = True
                log("[cg] creando funcion sintetica main", channel="cg")

            if current_func is not None:
                current_func.registerLine(line)

    return functions


def translateFunction(emitter: MipsEmitter, func: FunctionTac) -> None:
    frame = StackFrame.fromTemps(func.name, func.temps)
    frame.emitPrologue(emitter)

    # estado de argumentos entre PARAM y CALL
    arg_state: dict = {"pending": 0}

    for line in func.body_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(";"):
            continue

        # LABEL:
        m_label = label_re.match(stripped)
        if m_label:
            label = m_label.group(1)
            emitter.emitText(f"{label}:")
            continue

        # RETURN ...
        m_ret = return_re.match(stripped)
        if m_ret:
            ret_expr = m_ret.group(1)
            translateReturn(emitter, frame, func.name, ret_expr)
            continue

        # IF ... GOTO ...
        m_if = if_goto_re.match(stripped)
        if m_if:
            cond_expr, label = m_if.groups()
            translateIfGoto(emitter, frame, cond_expr, label)
            continue

        # GOTO ...
        m_goto = goto_re.match(stripped)
        if m_goto:
            label = m_goto.group(1)
            translateGoto(emitter, label)
            continue

        # PARAM ...
        m_param = param_re.match(stripped)
        if m_param:
            operand = m_param.group(1)
            translateParam(emitter, frame, operand, arg_state)
            continue

        # CALL f, n
        m_call = call_re.match(stripped)
        if m_call:
            func_name_call = m_call.group(1)
            arg_count = int(m_call.group(2))
            translateCall(emitter, frame, func_name_call, arg_count, arg_state)
            continue

        # binario con + - * /
        m_bin = binop_re.match(stripped)
        if m_bin:
            dest, left, op, right = m_bin.groups()
            translateBinOp(emitter, frame, dest, left, op, right)
            continue

        # asignación genérica con :=
        m_assign = assign_re.match(stripped)
        if m_assign:
            dest, expr = m_assign.groups()
            translateAssign(emitter, frame, dest, expr)
            continue

        # todo lo demás, por ahora solo se comenta
        emitter.emitText(f"    # instruccion TAC no traducida aun: {stripped}")
        log(f"[cg] instruccion no traducida: {stripped}", channel="cg")

    frame.emitEpilogue(emitter)


def generateMipsFromTac(tac_path: str, out_dir: str, stem: str) -> str:
    addChannel("cg")
    log(f"[cg] generateMipsFromTac tac={tac_path}", channel="cg", force=True)

    functions = parseTacFunctions(tac_path)
    emitter = MipsEmitter(program_name=stem)

    if not functions:
        emitter.emitText("main:")
        emitter.emitText("    li $v0, 10")
        emitter.emitText("    syscall")
        return emitter.writeToFile(out_dir)

    for func in functions:
        translateFunction(emitter, func)
        emitter.emitText("")

    return emitter.writeToFile(out_dir)
