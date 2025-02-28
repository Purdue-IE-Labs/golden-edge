from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gedge.node.gtypes import TagValue

@dataclass
class Reply:
    key_expr: str
    code: int
    body: dict[str, TagValue]
    error: str
