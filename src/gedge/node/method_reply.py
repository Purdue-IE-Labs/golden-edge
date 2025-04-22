from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING

from gedge.node import codes
if TYPE_CHECKING:
    from gedge.node.gtypes import TagBaseValue
    from gedge.py_proto.data_model import DataObject

@dataclass
class MethodReply:
    key_expr: str
    code: int
    body: dict[str, DataObject]
    error: str | None
    # method_config: Method
    # response_config: MethodResponse
    props: dict[str, DataObject]

    def is_error(self):
        return self.code == codes.METHOD_ERROR
    
    def is_done(self):
        return self.code == codes.DONE