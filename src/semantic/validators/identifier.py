from __future__ import annotations

from typing import Any, Mapping
from semantic.custom_types import ErrorType
from semantic.errors import SemanticError
from logs.logger import log, logFunction


@logFunction
def validateIdentifier(
    name: str,
    symbol_table: Mapping[str, Any],
    error_list: list[SemanticError],
    ctx: Any | None = None,
):
    """
    Verifica que un identificador exista en la “tabla plana” de símbolos y
    devuelve su tipo. Si no existe, registra un SemanticError y retorna ErrorType.

    Parámetros:
      - name: nombre del identificador a validar.
      - symbol_table: mapeo nombre → símbolo. Se espera que cada símbolo tenga
        al menos el atributo `type`.
      - error_list: lista mutable donde se acumulan errores semánticos.
      - ctx: (opcional) nodo del parser para extraer línea/columna.

    Retorna:
      - `symbol.type` si el identificador está declarado.
      - `ErrorType()` si no lo está (y se agrega el error a `error_list`).
    """
    log(f"Validating identifier: {name}", channel="semantic")

    symbol = symbol_table.get(name)

    if not symbol:
        line = getattr(getattr(ctx, "start", None), "line", None) if ctx else None
        column = getattr(getattr(ctx, "start", None), "column", None) if ctx else None
        error = SemanticError(
            message=f"Uso de variable no declarada: '{name}'",
            line=line,
            column=column,
        )
        log(f"ERROR: {error}", channel="semantic")
        error_list.append(error)
        return ErrorType()

    sym_type = getattr(symbol, "type", ErrorType())
    log(f"Identifier '{name}' resolved with type: {sym_type}", channel="semantic")
    return sym_type
