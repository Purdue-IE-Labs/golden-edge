from . import data_object_config_pb2 as _data_object_config_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BodyConfig(_message.Message):
    __slots__ = ("body",)
    class BodyEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _data_object_config_pb2.DataObjectConfig
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_data_object_config_pb2.DataObjectConfig, _Mapping]] = ...) -> None: ...
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: _containers.MessageMap[str, _data_object_config_pb2.DataObjectConfig]
    def __init__(self, body: _Optional[_Mapping[str, _data_object_config_pb2.DataObjectConfig]] = ...) -> None: ...
