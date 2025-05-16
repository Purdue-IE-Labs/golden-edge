from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class TagGroupConfig(_message.Message):
    __slots__ = ("path", "items")
    PATH_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    path: str
    items: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, path: _Optional[str] = ..., items: _Optional[_Iterable[str]] = ...) -> None: ...
