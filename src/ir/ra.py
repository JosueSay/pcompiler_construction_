from __future__ import annotations

from .tac import Quad, Op


class ActivationRecordTools:
    """
    Utilidades de emisión relacionadas al Registro de Activación (RA).
    Protocolo TAC:
      - enter f_label, local_frame_size
      - return [place]
      - (leave f_label) opcional
    """

    @staticmethod
    def emitEnter(func_label: str, frame_size: int) -> Quad:
        return Quad(op=Op.ENTER, arg1=func_label, arg2=str(frame_size))

    @staticmethod
    def emitLeave(func_label: str | None = None) -> Quad:
        return Quad(op=Op.LEAVE, arg1=func_label)

    @staticmethod
    def emitReturn(value: str | None = None) -> Quad:
        return Quad(op=Op.RETURN, arg1=value)
