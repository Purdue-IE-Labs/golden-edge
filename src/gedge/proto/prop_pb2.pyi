from . import type_pb2 as _type_pb2
from . import base_data_pb2 as _base_data_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Prop(_message.Message):
    __slots__ = ("key", "type", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    type: _type_pb2.BaseType
    value: _base_data_pb2.BaseData
    def __init__(self, key: _Optional[str] = ..., type: _Optional[_Union[_type_pb2.BaseType, str]] = ..., value: _Optional[_Union[_base_data_pb2.BaseData, _Mapping]] = ...) -> None: ...
