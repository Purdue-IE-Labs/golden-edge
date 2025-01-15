from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TagData(_message.Message):
    __slots__ = ("data",)
    class DataType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[TagData.DataType]
        INT: _ClassVar[TagData.DataType]
        FLOAT: _ClassVar[TagData.DataType]
        STRING: _ClassVar[TagData.DataType]
        BOOL: _ClassVar[TagData.DataType]
        LIST_INT: _ClassVar[TagData.DataType]
        LIST_FLOAT: _ClassVar[TagData.DataType]
        LIST_STRING: _ClassVar[TagData.DataType]
        LIST_BOOL: _ClassVar[TagData.DataType]
    UNKNOWN: TagData.DataType
    INT: TagData.DataType
    FLOAT: TagData.DataType
    STRING: TagData.DataType
    BOOL: TagData.DataType
    LIST_INT: TagData.DataType
    LIST_FLOAT: TagData.DataType
    LIST_STRING: TagData.DataType
    LIST_BOOL: TagData.DataType
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: TagData.DataType
    def __init__(self, data: _Optional[_Union[TagData.DataType, str]] = ...) -> None: ...
