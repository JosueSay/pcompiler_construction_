from __future__ import annotations


class LabelMaker:
    """
    Generador simple de etiquetas únicas para TAC.

    - Entrega nombres secuenciales como 'L1', 'L2', ... o con el prefijo que se pida.
    - No se resetea por función: la monotonía global evita colisiones en el programa.
      (Si alguna fase quisiera “reiniciar” la numeración, debería crear otra instancia.)
    """

    def __init__(self) -> None:
        self.next_id: int = 0  # contador global para todas las etiquetas del programa

    def newLabel(self, prefix: str = "L") -> str:
        """
        Crea una etiqueta única con el prefijo dado.
        Mantiene compatibilidad con Emitter.newLabel(...).
        """
        self.next_id += 1
        return f"{prefix}{self.next_id}"
