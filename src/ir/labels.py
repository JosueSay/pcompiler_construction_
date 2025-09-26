from __future__ import annotations


class LabelMaker:
    def __init__(self) -> None:
        self.next_id: int = 0

    def newLabel(self, prefix: str = "L") -> str:
        self.next_id += 1
        return f"{prefix}{self.next_id}"
