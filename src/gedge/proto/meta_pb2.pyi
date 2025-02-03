from . import tag_data_pb2 as _tag_data_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Property(_message.Message):
    __slots__ = ("type", "value")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    type: _tag_data_pb2.DataType
    value: _tag_data_pb2.TagData
    def __init__(self, type: _Optional[_Union[_tag_data_pb2.DataType, str]] = ..., value: _Optional[_Union[_tag_data_pb2.TagData, _Mapping]] = ...) -> None: ...

class Meta(_message.Message):
    __slots__ = ("name", "key_prefix", "tags", "methods")
    class Method(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Tag(_message.Message):
        __slots__ = ("key", "type", "properties")
        class PropertiesEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: Property
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Property, _Mapping]] = ...) -> None: ...
        KEY_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        PROPERTIES_FIELD_NUMBER: _ClassVar[int]
        key: str
        type: _tag_data_pb2.DataType
        properties: _containers.MessageMap[str, Property]
        def __init__(self, key: _Optional[str] = ..., type: _Optional[_Union[_tag_data_pb2.DataType, str]] = ..., properties: _Optional[_Mapping[str, Property]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    KEY_PREFIX_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    METHODS_FIELD_NUMBER: _ClassVar[int]
    name: str
    key_prefix: str
    tags: _containers.RepeatedCompositeFieldContainer[Meta.Tag]
    methods: _containers.RepeatedCompositeFieldContainer[Meta.Method]
    def __init__(self, name: _Optional[str] = ..., key_prefix: _Optional[str] = ..., tags: _Optional[_Iterable[_Union[Meta.Tag, _Mapping]]] = ..., methods: _Optional[_Iterable[_Union[Meta.Method, _Mapping]]] = ...) -> None: ...
