from . import base_data_pb2 as _base_data_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataModel(_message.Message):
    __slots__ = ("data",)
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: DataItem
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[DataItem, _Mapping]] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.MessageMap[str, DataItem]
    def __init__(self, data: _Optional[_Mapping[str, DataItem]] = ...) -> None: ...

class DataItem(_message.Message):
    __slots__ = ("base_data", "model_data")
    BASE_DATA_FIELD_NUMBER: _ClassVar[int]
    MODEL_DATA_FIELD_NUMBER: _ClassVar[int]
    base_data: _base_data_pb2.BaseData
    model_data: DataModel
    def __init__(self, base_data: _Optional[_Union[_base_data_pb2.BaseData, _Mapping]] = ..., model_data: _Optional[_Union[DataModel, _Mapping]] = ...) -> None: ...
