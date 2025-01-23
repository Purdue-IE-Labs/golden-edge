from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[DataType]
    INT: _ClassVar[DataType]
    LONG: _ClassVar[DataType]
    FLOAT: _ClassVar[DataType]
    STRING: _ClassVar[DataType]
    BOOL: _ClassVar[DataType]
    LIST_INT: _ClassVar[DataType]
    LIST_LONG: _ClassVar[DataType]
    LIST_FLOAT: _ClassVar[DataType]
    LIST_STRING: _ClassVar[DataType]
    LIST_BOOL: _ClassVar[DataType]
UNKNOWN: DataType
INT: DataType
LONG: DataType
FLOAT: DataType
STRING: DataType
BOOL: DataType
LIST_INT: DataType
LIST_LONG: DataType
LIST_FLOAT: DataType
LIST_STRING: DataType
LIST_BOOL: DataType

class ListInt(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, list: _Optional[_Iterable[int]] = ...) -> None: ...

class ListLong(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, list: _Optional[_Iterable[int]] = ...) -> None: ...

class ListFloat(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, list: _Optional[_Iterable[int]] = ...) -> None: ...

class ListString(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, list: _Optional[_Iterable[int]] = ...) -> None: ...

class ListBool(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, list: _Optional[_Iterable[int]] = ...) -> None: ...

class TagData(_message.Message):
    __slots__ = ("int_data", "long_data", "float_data", "string_data", "bool_data", "list_int_data", "list_long_data", "list_float_data", "list_string_data", "list_bool_data")
    INT_DATA_FIELD_NUMBER: _ClassVar[int]
    LONG_DATA_FIELD_NUMBER: _ClassVar[int]
    FLOAT_DATA_FIELD_NUMBER: _ClassVar[int]
    STRING_DATA_FIELD_NUMBER: _ClassVar[int]
    BOOL_DATA_FIELD_NUMBER: _ClassVar[int]
    LIST_INT_DATA_FIELD_NUMBER: _ClassVar[int]
    LIST_LONG_DATA_FIELD_NUMBER: _ClassVar[int]
    LIST_FLOAT_DATA_FIELD_NUMBER: _ClassVar[int]
    LIST_STRING_DATA_FIELD_NUMBER: _ClassVar[int]
    LIST_BOOL_DATA_FIELD_NUMBER: _ClassVar[int]
    int_data: int
    long_data: int
    float_data: float
    string_data: str
    bool_data: bool
    list_int_data: ListInt
    list_long_data: ListLong
    list_float_data: ListFloat
    list_string_data: ListString
    list_bool_data: ListBool
    def __init__(self, int_data: _Optional[int] = ..., long_data: _Optional[int] = ..., float_data: _Optional[float] = ..., string_data: _Optional[str] = ..., bool_data: bool = ..., list_int_data: _Optional[_Union[ListInt, _Mapping]] = ..., list_long_data: _Optional[_Union[ListLong, _Mapping]] = ..., list_float_data: _Optional[_Union[ListFloat, _Mapping]] = ..., list_string_data: _Optional[_Union[ListString, _Mapping]] = ..., list_bool_data: _Optional[_Union[ListBool, _Mapping]] = ...) -> None: ...
