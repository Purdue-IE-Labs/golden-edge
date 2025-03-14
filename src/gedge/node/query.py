from __future__ import annotations

from dataclasses import dataclass

from gedge.comm.comm import Comm
from gedge.node.tag_data import TagData
from gedge.node import codes
from gedge import proto

import logging
logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING, Any, Callable
if TYPE_CHECKING:
    from gedge.node.method_response import MethodResponse

@dataclass
class MethodQuery:
    key_expr: str
    params: dict[str, Any]
    _reply: Callable[[int, dict[str, Any], str], None]
    _responses: list[MethodResponse]
    
    def reply(self, code: int, body: dict[str, Any] = {}, error: str = ""):
        logger.info(f"Replying to method with code {code} on path TODO: fix")
        if code not in {i.code for i in self._responses} and code not in {codes.DONE, codes.METHOD_ERROR, codes.TAG_ERROR}:
            raise ValueError(f"invalid repsonse code {code}")
        self._reply(code, body, error)
