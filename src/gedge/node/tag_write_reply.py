from __future__ import annotations

from dataclasses import dataclass
from gedge.node import codes
from typing import Any

@dataclass
class TagWriteReply:
    key_expr: str
    code: int
    error: str | None
    attempted_write_value: Any
    # tag_config: Tag
    props: dict[str, Any]

    def is_error(self):
        return self.code == codes.TAG_ERROR