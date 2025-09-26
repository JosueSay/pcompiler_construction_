from __future__ import annotations

import os
from datetime import datetime

from .tac import Quad, Op
from .labels import LabelMaker
from .tem_pool import TempPool
from .ra import ActivationRecordTools


class Emitter:
    """
    Acumula cuádruplos y genera 3AC textual/HTML.
    Pensado para inyectarse en el Visitor semántico.
    """

    def __init__(self, program_name: str = "main") -> None:
        self.program_name: str = program_name
        self.quads: list[Quad] = []
        self.label_maker = LabelMaker()
        self.temp_pool = TempPool()
        self.header_lines: list[str] = []
        self.flow_terminated: bool = False  # barrera de emisión (p.ej., tras return)

        self.addHeaderLine(f"; Compiscript TAC")
        self.addHeaderLine(f"; program: {self.program_name}")
        self.addHeaderLine(f"; generated: {datetime.now().isoformat(timespec='seconds')}")

    # ------------- Cabecera / control --------------

    def addHeaderLine(self, text: str) -> None:
        self.header_lines.append(text)

    def markFlowTerminated(self) -> None:
        self.flow_terminated = True

    def clearFlowTermination(self) -> None:
        self.flow_terminated = False

    # ------------- Emisión básica ------------------

    def emit(self, op: Op, arg1: str | None = None, arg2: str | None = None,
             res: str | None = None, label: str | None = None) -> Quad | None:
        if self.flow_terminated and op not in (Op.LABEL,):
            # Suprimimos emisión en regiones muertas, pero permitimos etiquetas ya reservadas.
            return None
        q = Quad(op=op, arg1=arg1, arg2=arg2, res=res, label=label)
        self.quads.append(q)
        return q

    def emitLabel(self, name: str) -> Quad:
        return self.emit(Op.LABEL, res=name)  # type: ignore

    def newLabel(self, prefix: str = "L") -> str:
        return self.label_maker.newLabel(prefix)

    # ------------- Atajos frecuentes ---------------

    def emitGoto(self, label_name: str) -> None:
        self.emit(Op.GOTO, arg1=label_name)

    def emitIfGoto(self, cond_text: str, label_name: str) -> None:
        self.emit(Op.IF_GOTO, arg1=cond_text, arg2=label_name)

    def emitIfFalseGoto(self, cond_text: str, label_name: str) -> None:
        self.emit(Op.IF_FALSE_GOTO, arg1=cond_text, arg2=label_name)

    def emitAssign(self, dst: str, src: str) -> None:
        self.emit(Op.ASSIGN, arg1=src, res=dst)

    def emitBinary(self, dst: str, left: str, op_text: str, right: str) -> None:
        self.emit(Op.BINARY, arg1=left, arg2=right, res=dst, label=op_text)

    def emitUnary(self, dst: str, op_text: str, value: str) -> None:
        self.emit(Op.UNARY, arg1=value, res=dst, label=op_text)

    # ------------- RA helpers ----------------------

    def beginFunction(self, func_label: str, local_frame_size: int) -> None:
        self.temp_pool.resetPerFunction()
        self.emitLabel(func_label)
        self.quads.append(ActivationRecordTools.emitEnter(func_label, local_frame_size))

    def endFunctionWithReturn(self, value: str | None = None) -> None:
        self.quads.append(ActivationRecordTools.emitReturn(value))
        self.markFlowTerminated()

    # ------------- Serialización -------------------

    def toText(self) -> str:
        lines: list[str] = list(self.header_lines)
        if lines and lines[-1] != "":
            lines.append("")
        for q in self.quads:
            lines.append(q.toText())
        return "\n".join(lines) + "\n"

    def writeTacText(self, out_dir: str, stem: str) -> str:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"{stem}.tac")
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.toText())
        return path

    def writeTacHtml(self, out_dir: str, stem: str) -> str:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"{stem}.tac.html")
        body = self.toText().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html = (
            "<!doctype html><meta charset='utf-8'>"
            "<title>Compiscript TAC</title>"
            "<style>body{font-family:ui-monospace,monospace}pre{line-height:1.3}</style>"
            f"<h3>Compiscript TAC — {self.program_name}</h3>"
            f"<pre>{body}</pre>"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return path
