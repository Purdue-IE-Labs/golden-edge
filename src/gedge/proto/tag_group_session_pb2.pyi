from . import base_data_pb2 as _base_data_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TagGroup(_message.Message):
    __slots__ = ("data",)
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _base_data_pb2.BaseData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_base_data_pb2.BaseData, _Mapping]] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.MessageMap[str, _base_data_pb2.BaseData]
    def __init__(self, data: _Optional[_Mapping[str, _base_data_pb2.BaseData]] = ...) -> None: ...
