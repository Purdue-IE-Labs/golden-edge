from __future__ import annotations

from dataclasses import dataclass
from gedge.comm.keys import NodeKeySpace
from gedge.node import codes

import logging
logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING, Any, Callable
if TYPE_CHECKING: # pragma: no cover
    from gedge.node.method_response import MethodResponse

@dataclass
class MethodQuery:
    key_expr: str
    params: dict[str, Any]
    _reply: Callable[[int, dict[str, Any], str], None]
    _responses: list[MethodResponse]
    
    def reply(self, code: int, body: dict[str, Any] = {}, error: str = ""):
        if not isinstance(error, str):
            raise ValueError(f"Argument 'error' in method reply must be a string. Did you pass an Exception?") # pragma: no cover
        logger.info(f"Replying to method query at path {NodeKeySpace.method_path_from_call_key(self.key_expr)} with code {code}")
        if code not in {i.code for i in self._responses} and code not in {codes.DONE, codes.METHOD_ERROR, codes.TAG_ERROR}:
            raise ValueError(f"invalid repsonse code {code}") # pragma: no cover
        self._reply(code, body, error)
