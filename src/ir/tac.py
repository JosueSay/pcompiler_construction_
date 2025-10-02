from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Op(Enum):
    """
    Conjunto cerrado de operaciones 3AC (TAC) que el backend entiende.
    No hay alias ni nombres duplicados: estos son los únicos válidos.

    Convenciones de campos en cada Quad:
      - arg1, arg2: operandos o metadatos puntuales (p. ej., condición o n_args)
      - res:        destino (si aplica)
      - label:      campo contextual (operador textual, nombre de campo, etc.)
    """

    # --- Runtime activation (marcos de llamada) ---
    ENTER   = "enter"   # enter f_label, frame_size
    LEAVE   = "leave"   # leave
    RETURN  = "return"  # return [place]

    # --- Control de flujo ---
    LABEL         = "label"       # <L>:
    GOTO          = "goto"        # goto <L>
    IF_GOTO       = "if_goto"     # if <cond> goto <L>
    IF_FALSE_GOTO = "if_false_goto"  # ifFalse <cond> goto <L>

    # --- Expresiones / asignaciones ---
    ASSIGN = "assign"   # res = arg1
    UNARY  = "unary"    # res = (label) arg1          ; label guarda el operador textual
    BINARY = "binary"   # res = arg1 (label) arg2     ; label guarda el operador textual

    # --- Llamadas ---
    PARAM = "param"     # param arg1
    CALL  = "call"      # [res =] call f_label, n_args
    CALLC = "callc"     # [res =] callc clos_place, n_args  (closures)

    # --- Estructuras de datos ---
    INDEX_LOAD  = "index_load"   # res = a[i]
    INDEX_STORE = "index_store"  # a[i] = res                ; label = i si viene como texto
    FIELD_LOAD  = "field_load"   # res = obj.field           ; label = "field"
    FIELD_STORE = "field_store"  # obj.field = res           ; label = "field"
    LEN         = "len"          # res = len a
    NEWLIST     = "newlist"      # res = newlist n
    NEWOBJ      = "newobj"       # res = newobj ClassName, size

    # --- Closures ---
    MKENV  = "mkenv"    # res = mkenv x,y,z
    MKCLOS = "mkclos"   # res = mkclos f_label, env_place


@dataclass
class Quad:
    """
    Representa una instrucción TAC. Los campos son intencionalmente genéricos
    (Any) porque algunos backends pasan enteros (p. ej. n_args) o strings
    indistintamente. La serialización textual normaliza todo.
    """
    op: Op
    arg1: Any | None = None
    arg2: Any | None = None
    res: Any | None = None
    label: Any | None = None

    def toText(self) -> str:
        o = self.op

        if o is Op.LABEL:
            return f"{self.res}:"

        if o is Op.GOTO:
            return f"goto {self.arg1}"

        if o is Op.IF_GOTO:
            return f"if {self.arg1} goto {self.arg2}"

        if o is Op.IF_FALSE_GOTO:
            return f"ifFalse {self.arg1} goto {self.arg2}"

        if o is Op.ENTER:
            return f"enter {self.arg1}, {self.arg2}"

        if o is Op.LEAVE:
            return "leave"

        if o is Op.RETURN:
            return "return" if self.arg1 is None else f"return {self.arg1}"

        if o is Op.PARAM:
            return f"param {self.arg1}"

        if o is Op.CALL:
            return f"{self.res} = call {self.arg1}, {self.arg2}" if self.res else f"call {self.arg1}, {self.arg2}"

        if o is Op.CALLC:
            return f"{self.res} = callc {self.arg1}, {self.arg2}" if self.res else f"callc {self.arg1}, {self.arg2}"

        if o is Op.ASSIGN:
            return f"{self.res} = {self.arg1}"

        if o is Op.UNARY:
            op_txt = str(self.label or "")
            # Formato compacto: "t1 = - x" o "t1 = ! x"
            return f"{self.res} = {op_txt} {self.arg1}".strip()

        if o is Op.BINARY:
            op_txt = str(self.label or "?")
            return f"{self.res} = {self.arg1} {op_txt} {self.arg2}"

        if o is Op.INDEX_LOAD:
            return f"{self.res} = {self.arg1}[{self.arg2}]"

        if o is Op.INDEX_STORE:
            # Nota: usamos label para el índice textual si vino así
            return f"{self.arg1}[{self.label}] = {self.res}"

        if o is Op.FIELD_LOAD:
            return f"{self.res} = {self.arg1}.{self.label}"

        if o is Op.FIELD_STORE:
            return f"{self.arg1}.{self.label} = {self.res}"

        if o is Op.LEN:
            return f"{self.res} = len {self.arg1}"

        if o is Op.NEWLIST:
            return f"{self.res} = newlist {self.arg1}"

        if o is Op.NEWOBJ:
            return f"{self.res} = newobj {self.arg1}, {self.arg2}"

        if o is Op.MKENV:
            return f"{self.res} = mkenv {self.arg1}"

        if o is Op.MKCLOS:
            return f"{self.res} = mkclos {self.arg1}, {self.arg2}"

        # Si algo llega aquí, es un bug en la emisión.
        return f"; <unknown quad> {self}"
