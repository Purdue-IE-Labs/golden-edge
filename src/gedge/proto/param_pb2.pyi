from . import tag_data_pb2 as _tag_data_pb2
from . import prop_pb2 as _prop_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Param(_message.Message):
    __slots__ = ("type", "props")
    class PropsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _prop_pb2.Prop
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_prop_pb2.Prop, _Mapping]] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    type: _tag_data_pb2.DataType
    props: _containers.MessageMap[str, _prop_pb2.Prop]
    def __init__(self, type: _Optional[_Union[_tag_data_pb2.DataType, str]] = ..., props: _Optional[_Mapping[str, _prop_pb2.Prop]] = ...) -> None: ...
