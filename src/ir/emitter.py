from __future__ import annotations

import os
from datetime import datetime

from .tac import Quad, Op
from .labels import LabelMaker
from .temp_pool import TempPool
from logs.logger import log 


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
        
    def parseAddress(self, place: str) -> tuple[str, str] | None:
        """
        Intenta descomponer un place 'base[idx]' en ('base', 'idx').
        Devuelve None si no coincide.
        """
        if not isinstance(place, str):
            return None
        place = place.strip()
        if not place.endswith("]"):
            return None
        try:
            lbr = place.index("[")
            base = place[:lbr]
            idx = place[lbr + 1 : -1]  # contenido entre [ ... ]
            base = base.strip()
            idx = idx.strip()
            if base and idx:
                return base, idx
        except Exception:
            return None
        return None

    def canLowerField(self, owner_place: str | None, field_label: str | int | None) -> bool:
        """
        Bajamos si:
        - field_label es un entero (offset numérico)
        - y el owner es de la forma base[idx] **o** un place simple (p. ej. t2, fp[...], gp[...])
        """
        if owner_place is None or field_label is None:
            return False
        try:
            int(field_label)  # debe ser offset numérico
        except Exception:
            return False
        # Permitimos tanto base[idx] como un place simple
        return True

    def lowerFieldLoad(self, owner_place: str | None, dst_place: str | None, field_label: str | int | None) -> Quad | None:
        """
        Convierte:
            FIELD_LOAD  res=dst, arg1=owner_place(base[idx0]), label=off
        en:
            t_off := 0 + off
            t_sum := idx0 + t_off
            dst   := base[t_sum]
        Si no aplica, devuelve None (caller emitirá FIELD_LOAD normal).
        """
        if not self.canLowerField(owner_place, field_label) or not dst_place:
            return None
        
        parsed = self.parseAddress(owner_place)
        if parsed:
            base, idx0 = parsed
        else:
            # owner simple (ej. t2): tratamos como base + 0
            base, idx0 = owner_place, "0"

        off = str(int(field_label))  # seguro por canLowerField

        # t_off := 0 + off
        t_off = self.temp_pool.newTemp("int")
        self.emitBinary(t_off, "0", "+", off)

        # t_sum := idx0 + t_off
        t_sum = self.temp_pool.newTemp("int")
        self.emitBinary(t_sum, idx0, "+", t_off)

        # dst := base[t_sum]
        q = self.emit(Op.INDEX_LOAD, arg1=base, arg2=t_sum, res=dst_place)

        # liberar temporales internos
        self.temp_pool.free(t_off, "*")
        self.temp_pool.free(t_sum, "*")

        log(f"[Emitter.lowerFieldLoad] {dst_place} := {base}[{idx0}+{off}]", channel="tac")
        return q

    def lowerFieldStore(self, owner_place: str | None, value_place: str | None, field_label: str | int | None) -> Quad | None:
        """
        Convierte:
            FIELD_STORE arg1=owner_place(base[idx0]), res=value_place, label=off
        en:
            t_off := 0 + off
            t_sum := idx0 + t_off
            base[t_sum] := value_place
        Si no aplica, devuelve None (caller emitirá FIELD_STORE normal).
        """
        if not self.canLowerField(owner_place, field_label) or not value_place:
            return None

        parsed = self.parseAddress(owner_place)
        if parsed:
            base, idx0 = parsed
        else:
            # owner simple (ej. t2): tratamos como base + 0
            base, idx0 = owner_place, "0"

        off = str(int(field_label))  # seguro por canLowerField

        # t_off := 0 + off
        t_off = self.temp_pool.newTemp("int")
        self.emitBinary(t_off, "0", "+", off)

        # t_sum := idx0 + t_off
        t_sum = self.temp_pool.newTemp("int")
        self.emitBinary(t_sum, idx0, "+", t_off)

        # base[t_sum] := value_place
        q = self.emit(Op.INDEX_STORE, arg1=base, arg2=t_sum, res=value_place)

        # liberar temporales internos
        self.temp_pool.free(t_off, "*")
        self.temp_pool.free(t_sum, "*")

        log(f"[Emitter.lowerFieldStore] {base}[{idx0}+{off}] := {value_place}", channel="tac")
        return q



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

        Además: baja (lowering) FIELD_LOAD / FIELD_STORE a secuencias con temporales
        e INDEX_LOAD / INDEX_STORE cuando:
          - label es un offset numérico
          - arg1 tiene forma base[idx] (p. ej. fp[0])
        """
        if self.flow_terminated and op not in (Op.LABEL, Op.LEAVE):
            return None

        # Lowering de FIELD_LOAD / FIELD_STORE a acceso con temporales + INDEX_*
        if op is Op.FIELD_LOAD:
            lowered = self.lowerFieldLoad(arg1, res, label)
            if lowered:
                return lowered

        if op is Op.FIELD_STORE:
            lowered = self.lowerFieldStore(arg1, res, label)
            if lowered:
                return lowered

        q = Quad(op=op, arg1=arg1, arg2=arg2, res=res, label=label)
        self.quads.append(q)

        if op in (Op.FIELD_LOAD, Op.FIELD_STORE):
            label_type = type(label).__name__ if label is not None else "None"
            log(
                f"[Emitter] {op.name}: arg1={arg1}, arg2={arg2}, res={res}, "
                f"label={label} (type={label_type})",
                channel="tac"
            )

        return q
    
    def emitLabel(self, name: str) -> Quad | None:
        return self.emit(Op.LABEL, res=name)

    def newLabel(self, prefix: str = "L") -> str:
        return self.label_maker.newLabel(prefix)


    # ---------- atajos frecuentes ----------
    def emitCall(self, fname: str, nargs: int, dst: str | None = None) -> None:
        self.emit(Op.CALL, arg1=fname, arg2=str(nargs))
        if dst is not None:
            self.emitAssign(dst, "R")

    def emitCallC(self, fname: str, nargs: int, dst: str | None = None) -> None:
        self.emit(Op.CALLC, arg1=fname, arg2=str(nargs))
        if dst is not None:
            self.emitAssign(dst, "R")

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

    def emitFieldLoad(self, base_place: str, field_label: str | int, dst_place: str) -> Quad | None:
        return self.emit(Op.FIELD_LOAD, arg1=base_place, res=dst_place, label=field_label)

    def emitFieldStore(self, base_place: str, field_label: str | int, src_place: str) -> Quad | None:
        return self.emit(Op.FIELD_STORE, arg1=base_place, res=src_place, label=field_label)


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

        # Cierre de la función (necesario para que salga "END FUNCTION ...")
        self.emit(Op.LEAVE, arg1=self.current_function)

        # Activa la barrera para suprimir emisión posterior (menos LABEL/LEAVE)
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
