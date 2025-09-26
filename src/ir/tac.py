from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Op(Enum):
    # Pseudo-ops de RA
    ENTER = "enter"
    LEAVE = "leave"
    RETURN = "return"

    # Flujo
    LABEL = "label"
    GOTO = "goto"
    IF_GOTO = "if_goto"
    IF_FALSE_GOTO = "if_false_goto"

    # Asignaciones y expr
    ASSIGN = "assign"          # res = arg1
    UNARY = "unary"            # res = op arg1 (arg2 guarda el operador textual si se necesitara)
    BINARY = "binary"          # res = arg1 op arg2 (label guarda el operador textual)

    # Llamadas
    PARAM = "param"
    CALL = "call"              # [res =] call f, n
    CALLC = "callc"            # [res =] callc clos, n  (closures)

    # Estructuras de datos
    INDEX_LOAD = "index_load"  # res = a[i]
    INDEX_STORE = "index_store"# a[i] = res
    FIELD_LOAD = "field_load"  # res = obj.f
    FIELD_STORE = "field_store"# obj.f = res
    LEN = "len"                # res = len a
    NEWLIST = "newlist"        # res = newlist n
    NEWOBJ = "newobj"          # res = newobj C, size

    # Closures
    MKENV = "mkenv"            # res = mkenv ...
    MKCLOS = "mkclos"          # res = mkclos f_label, env


@dataclass
class Quad:
    op: Op
    arg1: str | None = None
    arg2: str | None = None
    res: str | None = None
    label: str | None = None   # uso contextual: operador textual, nombre de campo, etc.

    def toText(self) -> str:
        o = self.op

        if o is Op.LABEL:
            # res = nombre de la etiqueta
            return f"{self.res}:"

        if o is Op.GOTO:
            return f"goto {self.arg1}"

        if o is Op.IF_GOTO:
            # arg1 = condición textual (p. ej., "x < y"), arg2 = destino
            return f"if {self.arg1} goto {self.arg2}"

        if o is Op.IF_FALSE_GOTO:
            return f"ifFalse {self.arg1} goto {self.arg2}"

        if o is Op.ENTER:
            # arg1 = nombre función, arg2 = tamaño frame
            return f"enter {self.arg1}, {self.arg2}"

        if o is Op.LEAVE:
            return f"leave {self.arg1}" if self.arg1 else "leave"

        if o is Op.RETURN:
            return "return" if self.arg1 is None else f"return {self.arg1}"

        if o is Op.PARAM:
            return f"param {self.arg1}"

        if o is Op.CALL:
            # arg1 = f_label, arg2 = n_args
            return f"{self.res} = call {self.arg1}, {self.arg2}" if self.res else f"call {self.arg1}, {self.arg2}"

        if o is Op.CALLC:
            # arg1 = closure, arg2 = n_args
            return f"{self.res} = callc {self.arg1}, {self.arg2}" if self.res else f"callc {self.arg1}, {self.arg2}"

        if o is Op.ASSIGN:
            # res = arg1
            return f"{self.res} = {self.arg1}"

        if o is Op.UNARY:
            # label almacena el operador textual
            op_txt = self.label or ""
            return f"{self.res} = {op_txt} {self.arg1}".strip()

        if o is Op.BINARY:
            # label almacena el operador textual
            op_txt = self.label or "?"
            return f"{self.res} = {self.arg1} {op_txt} {self.arg2}"

        if o is Op.INDEX_LOAD:
            # res = a[i]
            return f"{self.res} = {self.arg1}[{self.arg2}]"

        if o is Op.INDEX_STORE:
            # arg1[i] = res  (res contiene el valor a almacenar)
            return f"{self.arg1}[{self.label}] = {self.res}"

        if o is Op.FIELD_LOAD:
            # res = obj.f  (label = "f")
            return f"{self.res} = {self.arg1}.{self.label}"

        if o is Op.FIELD_STORE:
            # obj.f = res  (label = "f")
            return f"{self.arg1}.{self.label} = {self.res}"

        if o is Op.LEN:
            # res = len a
            return f"{self.res} = len {self.arg1}"

        if o is Op.NEWLIST:
            # res = newlist n
            return f"{self.res} = newlist {self.arg1}"

        if o is Op.NEWOBJ:
            # res = newobj C, size
            return f"{self.res} = newobj {self.arg1}, {self.arg2}"

        if o is Op.MKENV:
            # res = mkenv a,b,c
            return f"{self.res} = mkenv {self.arg1}"

        if o is Op.MKCLOS:
            # res = mkclos f_label, env
            return f"{self.res} = mkclos {self.arg1}, {self.arg2}"

        # Fallback (no debería alcanzarse)
        return f"; <unknown quad> {self}"
