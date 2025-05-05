from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING
import warnings

if TYPE_CHECKING:
    from gedge.node.gtypes import TagValue

from gedge.node import codes
from gedge.node.method_response import ResponseType

@dataclass
class MethodReply:
    key_expr: str
    code: int
    body: dict[str, TagValue]
    type: ResponseType
    # method_config: Method
    # response_config: MethodResponse
    props: dict[str, TagValue]

    def is_ok(self):
        return codes.is_ok(self.code) or self.type == ResponseType.OK
    
    def is_err(self):
        return codes.is_err(self.code) or self.type == ResponseType.ERR

    def is_error(self):
        warnings.warn("is_error is deprecated, use is_err", category=DeprecationWarning)
        return self.code == codes.METHOD_ERROR
    
    def is_done(self):
        warnings.warn("is_done is deprecated, use is_ok", category=DeprecationWarning)
        return self.code == codes.DONE
    