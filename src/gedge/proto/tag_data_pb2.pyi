from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[DataType]
    INT: _ClassVar[DataType]
    FLOAT: _ClassVar[DataType]
    STRING: _ClassVar[DataType]
    BOOL: _ClassVar[DataType]
    LIST_INT: _ClassVar[DataType]
    LIST_FLOAT: _ClassVar[DataType]
    LIST_STRING: _ClassVar[DataType]
    LIST_BOOL: _ClassVar[DataType]
UNKNOWN: DataType
INT: DataType
FLOAT: DataType
STRING: DataType
BOOL: DataType
LIST_INT: DataType
LIST_FLOAT: DataType
LIST_STRING: DataType
LIST_BOOL: DataType

class TagData(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: DataType
    def __init__(self, data: _Optional[_Union[DataType, str]] = ...) -> None: ...
