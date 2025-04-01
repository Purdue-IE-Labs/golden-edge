from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING

from gedge.node import codes
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

    def is_error(self):
        return self.code == codes.METHOD_ERROR
    
    def is_done(self):
        return self.code == codes.DONE