from __future__ import annotations

import os
from datetime import datetime

from .tac import Quad, Op
from .labels import LabelMaker
from .temp_pool import TempPool


class Emitter:
    """
    Constructor de 3AC (TAC).

    - Acumula quads y puede serializarlos a texto/HTML.
    - Administra etiquetas y temporales.
    - Implementa una barrera de flujo (post-`return`) para suprimir emisión
      de quads en regiones inalcanzables, permitiendo únicamente `LABEL`
      (necesario para cerrar/controlar CFG).
    """

    def __init__(self, program_name: str = "main") -> None:
        self.program_name: str = program_name
        self.quads: list[Quad] = []
        self.label_maker = LabelMaker()
        self.temp_pool = TempPool()
        self.header_lines: list[str] = []
        self.flow_terminated: bool = False
        self.current_function: str | None = None


        self.addHeaderLine("; Compiscript TAC")
        self.addHeaderLine(f"; program: {self.program_name}")
        self.addHeaderLine(f"; generated: {datetime.now().isoformat(timespec='seconds')}")


    # ---------- cabecera / control ----------

    def addHeaderLine(self, text: str) -> None:
        self.header_lines.append(text)

    def markFlowTerminated(self) -> None:
        """Activa la barrera de flujo: suprime quads futuros (excepto `LABEL`)."""
        self.flow_terminated = True

    def clearFlowTermination(self) -> None:
        """Desactiva la barrera de flujo (p.ej., al entrar a una función)."""
        self.flow_terminated = False


    # ---------- emisión básica ----------

    def emit(
        self,
        op: Op,
        arg1: str | None = None,
        arg2: str | None = None,
        res: str | None = None,
        label: str | None = None,
    ) -> Quad | None:
        """
        Inserta un quad si no hay barrera activa. Si la hay, solo acepta `LABEL`.
        Devuelve el quad emitido o None si se suprimió.
        """
        if self.flow_terminated and op not in (Op.LABEL,):
            return None
        q = Quad(op=op, arg1=arg1, arg2=arg2, res=res, label=label)
        self.quads.append(q)
        return q

    def emitLabel(self, name: str) -> Quad | None:
        return self.emit(Op.LABEL, res=name)  # type: ignore

    def newLabel(self, prefix: str = "L") -> str:
        return self.label_maker.newLabel(prefix)


    # ---------- atajos frecuentes ----------

    def emitGoto(self, target: str) -> None:
        self.emit(Op.GOTO, arg1=target)

    def emitIfGoto(self, cond_text: str, target: str) -> None:
        self.emit(Op.IF_GOTO, arg1=cond_text, arg2=target)

    def emitIfFalseGoto(self, cond_text: str, target: str) -> None:
        self.emit(Op.IF_FALSE_GOTO, arg1=cond_text, arg2=target)

    def emitAssign(self, dst: str, src: str) -> None:
        self.emit(Op.ASSIGN, arg1=src, res=dst)

    def emitBinary(self, dst: str, left: str, op_text: str, right: str) -> None:
        self.emit(Op.BINARY, arg1=left, arg2=right, res=dst, label=op_text)

    def emitUnary(self, dst: str, op_text: str, value: str) -> None:
        self.emit(Op.UNARY, arg1=value, res=dst, label=op_text)

    def emitNewList(self, dest_place: str, n_elems: int) -> None:
        self.emit(Op.NEWLIST, arg1=n_elems, res=dest_place)

    def emitLen(self, dest_place: str, arr_place: str) -> Quad | None:
        return self.emit(Op.LEN, arg1=arr_place, res=dest_place)


    # ---------- patrón de bounds-check ----------

    def emitBoundsCheck(self, idx_place: str, arr_place: str) -> tuple[str, str]:
        """
        Verificación de límites para `arr[idx]`.

        Emite la secuencia:
            t_len = len arr
            if idx < 0       goto L_oob
            if idx >= t_len  goto L_oob
            goto L_ok
          L_oob:
            call __bounds_error, 0
          L_ok:

        Devuelve:
            (t_len, L_ok)
        """
        t_len = self.temp_pool.newTemp("int")
        self.emitLen(t_len, arr_place)

        l_oob = self.newLabel("oob")
        l_ok = self.newLabel("ok")

        self.emitIfGoto(f"{idx_place}<0", l_oob)
        self.emitIfGoto(f"{idx_place}>={t_len}", l_oob)
        self.emitGoto(l_ok)

        self.emitLabel(l_oob)
        self.emit(Op.CALL, arg1="__bounds_error", arg2="0")
        self.emitLabel(l_ok)

        return t_len, l_ok


    # ---------- helpers de función ----------

    def beginFunction(self, func_label: str, local_frame_size: int | None) -> None:
        """
        Prólogo lógico de función:
        - reinicia el pool de temporales (aislamiento por función)
        - limpia barrera de flujo
        - emite etiqueta y `enter`
        """
        self.current_function = func_label
        self.temp_pool.resetPerFunction()
        self.clearFlowTermination()
        size_text = str(local_frame_size if local_frame_size is not None else 0)
        self.emit(Op.ENTER, arg1=func_label, arg2=size_text)

    def endFunctionWithReturn(self, value_place: str | None = None) -> None:
        """
        Retorno y cierre lógico de función:
        - `return` (con o sin valor)
        - activa la barrera de flujo para suprimir emisión posterior
        """
        if value_place is not None and value_place != "":
            self.emit(Op.RETURN, arg1=value_place)
        else:
            self.emit(Op.RETURN)
            
        self.emit(Op.LEAVE, arg1=self.current_function)
        self.markFlowTerminated()

    def endFunction(self) -> None:
        """
        Cierre explícito sin `return`. Útil para prólogos/epílogos sintéticos.
        Normalmente no se usa si `endFunctionWithReturn` ya cerró el flujo.
        """
        self.emit(Op.LEAVE, arg1=self.current_function)
        self.markFlowTerminated()


    # ---------- serialización ----------

    def toText(self) -> str:
        lines: list[str] = list(self.header_lines)
        if lines and lines[-1] != "":
            lines.append("")

        for q in self.quads:
            txt = q.toText()
            # Saltar quads sin representación textual (p.ej., PARAM oculto)
            if not txt:
                continue
            parts = txt.splitlines()
            # No indentar: LABEL, ENTER (FUNCTION), LEAVE (END FUNCTION)
            if q.op in (Op.LABEL, Op.ENTER, Op.LEAVE):
                lines.extend(parts)
            else:
                lines.extend(["\t" + p for p in parts])

        return "\n".join(lines) + "\n"




    def writeTacText(self, out_dir: str, stem: str, *, simple_names: bool = False) -> str:
        """
        Escribe TAC plano. Con `simple_names=True` el archivo se llama `program.tac`,
        de lo contrario `<stem>.tac`.
        """
        os.makedirs(out_dir, exist_ok=True)
        filename = "program.tac" if simple_names else f"{stem}.tac"
        path = os.path.join(out_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.toText())
        return path

    def writeTacHtml(self, out_dir: str, stem: str, *, simple_names: bool = False) -> str:
        """
        Escribe una vista HTML simple del TAC. Con `simple_names=True` se llama
        `program.tac.html`, de lo contrario `<stem>.tac.html`.
        """
        os.makedirs(out_dir, exist_ok=True)
        filename = "program.tac.html" if simple_names else f"{stem}.tac.html"
        path = os.path.join(out_dir, filename)
        body = (
            self.toText()
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
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
