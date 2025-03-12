from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING

from gedge.node.tag_data import TagData

if TYPE_CHECKING:
    from gedge.node.gtypes import TagValue

@dataclass
class MethodReply:
    key_expr: str
    code: int
    body: dict[str, dict]
    error: str | None
    # method_config: Method
    # response_config: MethodResponse
    props: dict[str, TagValue]
