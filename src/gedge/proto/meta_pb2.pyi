from . import method_pb2 as _method_pb2
from . import tag_pb2 as _tag_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Meta(_message.Message):
    __slots__ = ("tracking", "key", "tags", "methods")
    TRACKING_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    METHODS_FIELD_NUMBER: _ClassVar[int]
    tracking: bool
    key: str
    tags: _containers.RepeatedCompositeFieldContainer[_tag_pb2.Tag]
    methods: _containers.RepeatedCompositeFieldContainer[_method_pb2.Method]
    def __init__(self, tracking: bool = ..., key: _Optional[str] = ..., tags: _Optional[_Iterable[_Union[_tag_pb2.Tag, _Mapping]]] = ..., methods: _Optional[_Iterable[_Union[_method_pb2.Method, _Mapping]]] = ...) -> None: ...
