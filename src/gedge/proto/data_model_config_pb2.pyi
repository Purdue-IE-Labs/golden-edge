from . import type_pb2 as _type_pb2
from . import prop_pb2 as _prop_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataModelConfig(_message.Message):
    __slots__ = ("path", "version", "parent", "items")
    PATH_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PARENT_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    path: str
    version: int
    parent: _type_pb2.DataModelRef
    items: _containers.RepeatedCompositeFieldContainer[DataItemConfig]
    def __init__(self, path: _Optional[str] = ..., version: _Optional[int] = ..., parent: _Optional[_Union[_type_pb2.DataModelRef, _Mapping]] = ..., items: _Optional[_Iterable[_Union[DataItemConfig, _Mapping]]] = ...) -> None: ...

class DataItemConfig(_message.Message):
    __slots__ = ("path", "type", "props")
    PATH_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    path: str
    type: _type_pb2.Type
    props: _containers.RepeatedCompositeFieldContainer[_prop_pb2.Prop]
    def __init__(self, path: _Optional[str] = ..., type: _Optional[_Union[_type_pb2.Type, _Mapping]] = ..., props: _Optional[_Iterable[_Union[_prop_pb2.Prop, _Mapping]]] = ...) -> None: ...
