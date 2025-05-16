from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING
import warnings

if TYPE_CHECKING:
    from gedge.node.gtypes import TagValue

from gedge.node import codes
from gedge.node.method_response import ResponseType

@dataclass
class Response:
    key_expr: str
    code: int
    type: ResponseType
    body: dict[str, TagValue]
    props: dict[str, TagValue]

    def is_ok(self):
        return self.type == ResponseType.OK
    
    def is_err(self):
        return self.type == ResponseType.ERR
