from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class BaseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[BaseType]
    INT: _ClassVar[BaseType]
    LONG: _ClassVar[BaseType]
    FLOAT: _ClassVar[BaseType]
    STRING: _ClassVar[BaseType]
    BOOL: _ClassVar[BaseType]
    LIST_INT: _ClassVar[BaseType]
    LIST_LONG: _ClassVar[BaseType]
    LIST_FLOAT: _ClassVar[BaseType]
    LIST_STRING: _ClassVar[BaseType]
    LIST_BOOL: _ClassVar[BaseType]
UNKNOWN: BaseType
INT: BaseType
LONG: BaseType
FLOAT: BaseType
STRING: BaseType
BOOL: BaseType
LIST_INT: BaseType
LIST_LONG: BaseType
LIST_FLOAT: BaseType
LIST_STRING: BaseType
LIST_BOOL: BaseType

class DataModelType(_message.Message):
    __slots__ = ("path", "version")
    PATH_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    path: str
    version: int
    def __init__(self, path: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...
