from . import tag_config_pb2 as _tag_config_pb2
from . import type_pb2 as _type_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataModelConfig(_message.Message):
    __slots__ = ("type", "extends_path", "version", "tags")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    EXTENDS_PATH_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    type: _type_pb2.DataModelType
    extends_path: str
    version: int
    tags: _containers.RepeatedCompositeFieldContainer[_tag_config_pb2.TagConfig]
    def __init__(self, type: _Optional[_Union[_type_pb2.DataModelType, _Mapping]] = ..., extends_path: _Optional[str] = ..., version: _Optional[int] = ..., tags: _Optional[_Iterable[_Union[_tag_config_pb2.TagConfig, _Mapping]]] = ...) -> None: ...
