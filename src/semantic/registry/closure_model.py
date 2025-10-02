from dataclasses import dataclass
from typing import Tuple

@dataclass
class CaptureInfo:
    """
    Información de variables capturadas por una función anidada.
    """
    captured: list[Tuple[str, str, int]]  # (name, type_str, original_scope_id)

    def asDebug(self) -> str:
        return ", ".join(f"{n}:{t}@scope{sid}" for n, t, sid in self.captured)
