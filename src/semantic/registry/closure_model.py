from dataclasses import dataclass
from typing import Tuple

@dataclass
class CaptureInfo:
    """
    Modelo mínimo para describir *capturas* de una función anidada.

    ¿Qué es una “captura”?
      Cuando una función se define dentro de otra, puede referirse a variables
      que viven en el ámbito (scope) externo. Esas referencias no son parámetros
      ni variables locales de la función interna: son **capturas**.

    ¿Para qué se usa en el pipeline?
      - Fase semántica: registramos qué nombres externos usa cada función
        anidada y con qué tipo fueron vistos. Esto permite validar el acceso y
        preparar la información necesaria para construir entornos/closures.
      - Fase TAC (3AC): con la lista de capturas podemos:
          * materializar un *environment* (mkenv) con los valores a cerrar,
          * construir un *closure* (mkclos) que viaja con esos valores,
          * o resolver llamadas a funciones anidadas correctamente.
    """
    captured: list[Tuple[str, str, int]]  # (name, type_str, original_scope_id)

    def asDebug(self) -> str:
        """
        Devuelve una representación compacta y legible para logs,
        con el formato:  "name:type@scopeID, name2:type2@scopeID2, ...".
        """
        return ", ".join(f"{n}:{t}@scope{sid}" for n, t, sid in self.captured)
