from __future__ import annotations

import os
from datetime import datetime

from .tac import Quad, Op
from .labels import LabelMaker
from .temp_pool import TempPool
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

    def emitNewList(self, dest_place: str, n_elems: int) -> None:
        self.emit(Op.NEWLIST, n_elems, None, dest_place)

    def emitLen(self, dest_place: str, arr_place: str):
        """
        Emite: dest_place = len arr_place
        (Pseudo-op de TAC, no expone 'len' al lenguaje)
        """
        from ir.tac import Op
        return self.emit(Op.LEN, arg1=arr_place, res=dest_place)

    def emitBoundsCheck(self, idx_place: str, arr_place: str):
        """
        Patrón estándar de bounds check para a[i] o t_arr[i].
        Emite:
           t_len = len arr_place
           if idx_place < 0 goto L_oob
           if idx_place >= t_len goto L_oob
           goto L_ok
           L_oob: call __bounds_error, 0
           L_ok:
        Retorna: (t_len, L_ok)
        """
        from ir.tac import Op
        t_len = self.temp_pool.newTemp("int")
        self.emitLen(t_len, arr_place)

        l_oob = self.newLabel("oob")
        l_ok  = self.newLabel("ok")

        self.emitIfGoto(f"{idx_place}<0", l_oob)
        self.emitIfGoto(f"{idx_place}>={t_len}", l_oob)
        self.emitGoto(l_ok)

        self.emitLabel(l_oob)
        self.emit(Op.CALL, arg1="__bounds_error", arg2="0")
        self.emitLabel(l_ok)

        return t_len, l_ok

    # ------------- RA helpers ----------------------
    
    def beginFunction(self, func_label: str, local_frame_size: int | None) -> None:
        """
        Abre un nuevo contexto de función:
        - resetea el pool de temporales por función
        - limpia cualquier barrera de flujo (por returns previos)
        - emite la etiqueta y el prólogo lógico 'enter'
        """
        # Aislar temporales por función
        self.temp_pool.resetPerFunction()
        # Asegurar que no hay barrera activada al entrar
        self.clearFlowTermination()
        # Etiqueta de entrada
        self.emitLabel(func_label)
        # Prológo lógico (usa 0 si aún no sabemos el frame real)
        size_text = str(local_frame_size if local_frame_size is not None else 0)
        self.emit(Op.ENTER, arg1=func_label, arg2=size_text)

    def endFunctionWithReturn(self, value_place: str | None = None) -> None:
        """
        Emite 'return' (con o sin valor) y activa barrera de emisión
        para suprimir cualquier 3AC posterior en el mismo bloque.
        """
        if value_place is not None and value_place != "":
            self.emit(Op.RETURN, arg1=value_place)
        else:
            self.emit(Op.RETURN)
        # Cerrar flujo del bloque actual
        self.markFlowTerminated()

    # ------------- Serialización -------------------

    def toText(self) -> str:
        lines: list[str] = list(self.header_lines)
        if lines and lines[-1] != "":
            lines.append("")
        for q in self.quads:
            lines.append(q.toText())
        return "\n".join(lines) + "\n"

    def writeTacText(self, out_dir: str, stem: str, *, simple_names: bool = False) -> str:
        """
        Si simple_names=True, escribe 'program.tac' dentro de out_dir.
        De lo contrario, usa '<stem>.tac' (compatibilidad).
        """
        os.makedirs(out_dir, exist_ok=True)
        filename = "program.tac" if simple_names else f"{stem}.tac"
        path = os.path.join(out_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.toText())
        return path

    def writeTacHtml(self, out_dir: str, stem: str, *, simple_names: bool = False) -> str:
        """
        Si simple_names=True, escribe 'program.tac.html' dentro de out_dir.
        De lo contrario, usa '<stem>.tac.html'.
        """
        os.makedirs(out_dir, exist_ok=True)
        filename = "program.tac.html" if simple_names else f"{stem}.tac.html"
        path = os.path.join(out_dir, filename)
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