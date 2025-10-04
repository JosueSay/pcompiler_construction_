from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class SemanticError:
    """
    Error semántico detectado durante el análisis del código fuente.

    Atributos:
        message: Descripción clara y humana del problema.
        line: Línea del archivo fuente donde ocurrió (si se conoce).
        column: Columna del archivo fuente donde ocurrió (si se conoce).
        error_type: Etiqueta de clasificación del error (por defecto "SemanticError").

    Notas de uso:
      - Mantén mensajes accionables: qué salió mal y, si aplica, qué esperaba el analizador.
      - `line` y `column` suelen venir de `ctx.start.line` y `ctx.start.column` (ANTLR).
    """
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    error_type: str = "SemanticError"

    def __str__(self) -> str:
        """
        Devuelve una representación amigable para logs/consola.
        """
        loc = f" at line {self.line}, column {self.column}" if self.line is not None else ""
        return f"[{self.error_type}]{loc}: {self.message}"

    def toDict(self) -> dict[str, Any]:
        """
        Serializa el error en un diccionario (útil para JSON u otros reportes).
        """
        return {
            "type": self.error_type,
            "message": self.message,
            "line": self.line,
            "column": self.column,
        }
