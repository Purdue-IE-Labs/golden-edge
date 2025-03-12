from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gedge.node.gtypes import TagValue
    from gedge.node.body import BodyData

@dataclass
class MethodReply:
    key_expr: str
    code: int
    body: dict[str, BodyData]
    error: str | None
    # method_config: Method
    # response_config: MethodResponse
    props: dict[str, TagValue]
