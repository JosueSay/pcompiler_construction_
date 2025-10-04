from typing import Any, Dict, List, Tuple

class MethodRegistry:
    """
    Registro global de firmas de métodos.

    Qué guarda:
      - Clave: nombre calificado en la forma `"Clase.metodo"`.
      - Valor: tupla `(param_types, return_type)` donde:
          * `param_types` incluye **this** como primer parámetro.
          * `return_type` es el tipo de retorno (o `None` si es `void`).

    Por qué incluye `this`:
      Mantener `this` en la firma facilita el *lowering* posterior:
      el emisor TAC puede empujar el receptor como primer `param`
      sin tener que reconstituir la firma real del método.
    """

    def __init__(self):
        # qname -> (param_types, return_type)
        # Nota: usamos Any para no acoplar esto a las clases de tipos del analizador.
        self.methods: Dict[str, Tuple[List[Any], Any]] = {}

    def registerMethod(self, qname: str, param_types: List[Any], return_type: Any) -> None:
        """
        Registra (o actualiza) la firma de un método.

        Parámetros:
          - qname: "Clase.metodo".
          - param_types: lista de tipos, con **this** en el índice 0.
          - return_type: tipo de retorno (o None para `void`).
        """
        self.methods[qname] = (param_types or [], return_type)

    def lookupMethod(self, qname: str) -> Tuple[List[Any], Any] | None:
        """
        Devuelve la firma registrada para `qname` o `None` si no existe.
        """
        return self.methods.get(qname)

    def existsMethod(self, qname: str) -> bool:
        """
        True si hay una firma registrada para `qname`.
        """
        return qname in self.methods
