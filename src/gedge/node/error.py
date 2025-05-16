from __future__ import annotations

from gedge.node import codes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gedge.node.gtypes import TagValue

class ConfigError(Exception):
    pass

class SessionError(Exception):
    pass

class TagLookupError(Exception):
    def __init__(self, path: str, node: str):
        message = f"Tag {path} not found on node {node}"
        super().__init__(message)

class MethodLookupError(Exception):
    def __init__(self, path: str, node: str):
        message = f"Method {path} not found on node {node}"
        super().__init__(message)

class NodeLookupError(Exception):
    def __init__(self, key: str):
        message = f"Node not found at key {key}"
        super().__init__(message)

class QueryEnd(Exception):
    def __init__(self, code: int, body: dict[str, TagValue] = {}) -> None:
        self.code = code
        self.body = body
        super().__init__(*[code, body])
    
    def is_callback_error(self) -> bool:
        return self.code == codes.CALLBACK_ERR
    
    def is_generic_error(self) -> bool:
        return self.code == codes.ERR
    
    def is_ok(self) -> bool:
        return self.code == codes.OK
