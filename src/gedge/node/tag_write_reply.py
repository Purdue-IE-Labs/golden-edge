from __future__ import annotations

from dataclasses import dataclass
from gedge.node.tag import Tag
from typing import Any

@dataclass
class TagWriteReply:
    key_expr: str
    code: int
    error: str | None
    attempted_write_value: Any
    tag_config: Tag
    response_props: dict[str, Any]
