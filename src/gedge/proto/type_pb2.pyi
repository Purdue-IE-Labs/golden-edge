from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

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
    __slots__ = ("path",)
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class Type(_message.Message):
    __slots__ = ("base_type", "data_model_type")
    BASE_TYPE_FIELD_NUMBER: _ClassVar[int]
    DATA_MODEL_TYPE_FIELD_NUMBER: _ClassVar[int]
    base_type: BaseType
    data_model_type: DataModelType
    def __init__(self, base_type: _Optional[_Union[BaseType, str]] = ..., data_model_type: _Optional[_Union[DataModelType, _Mapping]] = ...) -> None: ...
