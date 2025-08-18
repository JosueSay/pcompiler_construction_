from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class CaptureInfo:
    """
    Información de variables capturadas por una función anidada.
    """
    # Lista de (name, type_str, scope_id_original)
    captured: List[Tuple[str, str, int]]

    def as_debug(self) -> str:
        return ", ".join(f"{n}:{t}@scope{sid}" for n, t, sid in self.captured)