from . import type_pb2 as _type_pb2
from . import data_model_session_pb2 as _data_model_session_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Props(_message.Message):
    __slots__ = ("props",)
    class PropsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Prop
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Prop, _Mapping]] = ...) -> None: ...
    PROPS_FIELD_NUMBER: _ClassVar[int]
    props: _containers.MessageMap[str, Prop]
    def __init__(self, props: _Optional[_Mapping[str, Prop]] = ...) -> None: ...

class Prop(_message.Message):
    __slots__ = ("type", "value")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    type: _type_pb2.Type
    value: _data_model_session_pb2.DataObject
    def __init__(self, type: _Optional[_Union[_type_pb2.Type, _Mapping]] = ..., value: _Optional[_Union[_data_model_session_pb2.DataObject, _Mapping]] = ...) -> None: ...
