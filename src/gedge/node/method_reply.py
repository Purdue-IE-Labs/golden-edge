from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING

from gedge.node.method import Method
from gedge.node.method_response import MethodResponse
if TYPE_CHECKING:
    from gedge.node.gtypes import TagValue

@dataclass
class MethodReply:
    key_expr: str
    code: int
    body: dict[str, TagValue]
    error: str | None
    method_config: Method
    response_config: MethodResponse
