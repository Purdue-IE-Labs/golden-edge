from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class WriteResponseData(_message.Message):
    __slots__ = ("code", "error")
    CODE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    code: int
    error: str
    def __init__(self, code: _Optional[int] = ..., error: _Optional[str] = ...) -> None: ...
