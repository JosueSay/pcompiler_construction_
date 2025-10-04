from __future__ import annotations

from semantic.errors import SemanticError
from logs.logger import log


class Diagnostics:
    """
    Acumulador simple de errores semánticos.

    Uso típico:
        diag = Diagnostics()
        diag.report("mensaje de error", ctx)
        if diag.hasErrors():
            for e in diag.getAll():
                print(e)

    Notas:
      - Los errores se registran también en el canal de log "semantic".
      - `ctx` (si viene de ANTLR) se usa para extraer línea y columna.
    """

    def __init__(self) -> None:
        self.errors: list[SemanticError] = []

    def report(self, message: str, ctx=None, error_type: str = "SemanticError") -> SemanticError:
        """
        Crea y agrega un `SemanticError` a la lista.

        Args:
            message: Descripción humana del problema.
            ctx: Contexto ANTLR (opcional) para capturar línea y columna.
            error_type: Etiqueta opcional para clasificar el error.

        Returns:
            El `SemanticError` recién agregado.
        """
        line = getattr(getattr(ctx, "start", None), "line", None) if ctx is not None else None
        col = getattr(getattr(ctx, "start", None), "column", None) if ctx is not None else None
        err = SemanticError(message, line=line, column=col, error_type=error_type)
        self.errors.append(err)
        log(f"ERROR: {err}", channel="semantic")
        return err

    def extend(self, err: SemanticError) -> SemanticError:
        """
        Agrega un `SemanticError` ya construido y lo registra en el log.

        Args:
            err: La instancia de error a agregar.

        Returns:
            La misma instancia de `SemanticError`.
        """
        self.errors.append(err)
        log(f"ERROR: {err}", channel="semantic")
        return err

    def hasErrors(self) -> bool:
        """
        Indica si existe al menos un error registrado.
        """
        return len(self.errors) > 0

    def getAll(self) -> list[SemanticError]:
        """
        Devuelve una copia de la lista completa de errores.
        """
        return list(self.errors)
