from . import method_config_pb2 as _method_config_pb2
from . import tag_config_pb2 as _tag_config_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SubnodeConfig(_message.Message):
    __slots__ = ("name", "tags", "methods", "subnodes")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    METHODS_FIELD_NUMBER: _ClassVar[int]
    SUBNODES_FIELD_NUMBER: _ClassVar[int]
    name: str
    tags: _tag_config_pb2.TagConfig
    methods: _containers.RepeatedCompositeFieldContainer[_method_config_pb2.MethodConfig]
    subnodes: _containers.RepeatedCompositeFieldContainer[SubnodeConfig]
    def __init__(self, name: _Optional[str] = ..., tags: _Optional[_Union[_tag_config_pb2.TagConfig, _Mapping]] = ..., methods: _Optional[_Iterable[_Union[_method_config_pb2.MethodConfig, _Mapping]]] = ..., subnodes: _Optional[_Iterable[_Union[SubnodeConfig, _Mapping]]] = ...) -> None: ...
