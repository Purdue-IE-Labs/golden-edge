from . import props_pb2 as _props_pb2
from . import type_pb2 as _type_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TagConfig(_message.Message):
    __slots__ = ("path", "type", "props", "writable", "responses")
    PATH_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    WRITABLE_FIELD_NUMBER: _ClassVar[int]
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    path: str
    type: _type_pb2.Type
    props: _props_pb2.Props
    writable: bool
    responses: _containers.RepeatedCompositeFieldContainer[TagWriteResponseConfig]
    def __init__(self, path: _Optional[str] = ..., type: _Optional[_Union[_type_pb2.Type, _Mapping]] = ..., props: _Optional[_Union[_props_pb2.Props, _Mapping]] = ..., writable: bool = ..., responses: _Optional[_Iterable[_Union[TagWriteResponseConfig, _Mapping]]] = ...) -> None: ...

class TagWriteResponseConfig(_message.Message):
    __slots__ = ("code", "props")
    CODE_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    code: int
    props: _props_pb2.Props
    def __init__(self, code: _Optional[int] = ..., props: _Optional[_Union[_props_pb2.Props, _Mapping]] = ...) -> None: ...
