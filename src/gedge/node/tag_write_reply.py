from __future__ import annotations

from dataclasses import dataclass
from gedge.node import codes
from typing import Any

@dataclass
class TagWriteReply:
    key_expr: str
    code: int
    body: dict[str, Any]
    attempted_write_value: Any
    props: dict[str, Any]

    def is_error(self):
        return self.code == codes.TAG_ERROR