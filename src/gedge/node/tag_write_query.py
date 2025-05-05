from __future__ import annotations

from dataclasses import dataclass 
from gedge.comm.keys import NodeKeySpace
from gedge.node.codes import ERR, OK
from gedge.node.error import MethodEnd
from gedge.node.method_response import ResponseConfig, ResponseType

from typing import Any, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from gedge.node.gtypes import TagValue, TagBaseValue

import logging

from gedge.node import codes
logger = logging.getLogger(__name__)

"""
We love inheritance, until we don't :)
"""
@dataclass
class Query:
    key_expr: str
    _reply_func: Callable[[int, dict[str, TagValue]], None]
    _responses: list[ResponseConfig]
    _types_sent: list[ResponseType]

    def _log_message(self, message_type: str, code: int):
        raise NotImplementedError

    def _reply(self, code: int, body: dict[str, TagValue], type: ResponseType):
        # this is to allow the node to have access to this later
        self.code = code
        self.body = body

        if not self._is_valid_type(code, type):
            raise ValueError(f"invalid code ({code}) or response type ({type})")

        logger.info(f"Replying to tag value write with code {code}")
        self._types_sent.append(type)
        self._reply_func(code, body)

    def reply_ok(self, code: int = codes.OK, body: dict[str, Any] = {}):
        """
        Reply OK to a gedge query. Only call this once in a handler.

        Parameters:
            code (int): code to return to caller (defaults to OK)
            body (dict): body to return to caller (defaults to {})
        """

        logger.info(self._log_message("OK", code))
        self._reply(code, body, ResponseType.OK)
    
    def reply_err(self, code: int = codes.ERR, body: dict[str, Any] = {}):
        """
        Reply ERR to a gedge query. Only call this once in a handler.

        Parameters:
            code (int): code to return to caller (defaults to ERR)
            body (dict): body to return to caller (defaults to {})
        """

        logger.info(self._log_message("ERR", code))
        self._reply(code, body, ResponseType.ERR)
    
    def reply_info(self, code: int, body: dict[str, Any] = {}):
        """
        Reply INFO to a gedge query. This will likely be called multiple times.

        Parameters:
            code (int): code to return to caller (defaults to INFO)
            body (dict): body to return to caller (defaults to {})
        """

        logger.info(self._log_message("INFO", code))
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

@dataclass
class TagWriteQuery(Query):
    value: TagBaseValue

    def _log_message(self, message_type: str, code: int):
        return f"Replying {message_type} to tag write query at path {NodeKeySpace.tag_path_from_key(self.key_expr)} with code {code}"

@dataclass
class MethodQuery(Query):
    params: dict[str, TagValue]

    def _log_message(self, message_type: str, code: int):
        return f"Replying {message_type} to method query at path {NodeKeySpace.method_path_from_call_key(self.key_expr)} with code {code}"

    def reply_ok(self, code: int = codes.OK, body: dict[str, Any] = {}):
        super().reply_ok(code, body)
        # this ensures that the method stops when we reply_ok or reply_err
        raise MethodEnd(code, body)
    
    def reply_err(self, code: int = codes.ERR, body: dict[str, Any] = {}):
        super().reply_err(code, body)
        raise MethodEnd(code, body)