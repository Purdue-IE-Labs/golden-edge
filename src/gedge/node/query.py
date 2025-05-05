from __future__ import annotations

from dataclasses import dataclass, field
from gedge.comm.keys import NodeKeySpace
from gedge.node import codes

import logging

from gedge.node.error import MethodEnd
from gedge.node.method_response import ResponseType
logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING, Any, Callable
if TYPE_CHECKING:
    from gedge.node.method_response import ResponseConfig

@dataclass
class MethodQuery:
    key_expr: str
    params: dict[str, Any]
    _reply_func: Callable[[int, dict[str, Any]], None]
    _responses: list[ResponseConfig]
    _types_sent: list[ResponseType] = field(default_factory=list)
    
    def _reply(self, code: int, body: dict[str, Any], type: ResponseType):
        if not self._is_valid_type(code, type):
            raise ValueError(f"invalid code ({code}) or response type {type}")
        self._types_sent.append(type)
        self._reply_func(code, body)
    
    def reply_ok(self, code: int = codes.OK, body: dict[str, Any] = {}):
        logger.info(f"Replying OK to method query at path {NodeKeySpace.method_path_from_call_key(self.key_expr)} with code {code}")
        self._reply(code, body, ResponseType.OK)
        # this ensures that the method stops when we reply_ok or reply_err
        raise MethodEnd(code, body)
    
    def reply_err(self, code: int = codes.ERR, body: dict[str, Any] = {}):
        logger.info(f"Replying ERR to method query at path {NodeKeySpace.method_path_from_call_key(self.key_expr)} with code {code}")
        self._reply(code, body, ResponseType.ERR)
        raise MethodEnd(code, body)
    
    def reply_info(self, code: int, body: dict[str, Any] = {}):
        logger.info(f"Replying INFO to method query at path {NodeKeySpace.method_path_from_call_key(self.key_expr)} with code {code}")
        self._reply(code, body, ResponseType.INFO)
    
    def _is_valid_code(self, code: int) -> bool:
        return code in {i.code for i in self._responses} or codes.is_predefined_code(code)
    
    def _is_valid_type(self, code: int, type: ResponseType) -> bool:
        if not self._is_valid_code(code):
            return False
        if codes.is_predefined_code(code):
            config = codes.config_from_predefined_code(code)
        else:
            config = [i for i in self._responses if i.code == code][0]
        return config.type == type
