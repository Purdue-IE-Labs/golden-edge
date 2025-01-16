import tag_data_pb2 as _tag_data_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Meta(_message.Message):
    __slots__ = ("tags", "methods")
    class Method(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Tag(_message.Message):
        __slots__ = ("name", "type", "properties")
        class PropertiesEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: str
            def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
        NAME_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        PROPERTIES_FIELD_NUMBER: _ClassVar[int]
        name: str
        type: _tag_data_pb2.DataType
        properties: _containers.ScalarMap[str, str]
        def __init__(self, name: _Optional[str] = ..., type: _Optional[_Union[_tag_data_pb2.DataType, str]] = ..., properties: _Optional[_Mapping[str, str]] = ...) -> None: ...
    TAGS_FIELD_NUMBER: _ClassVar[int]
    METHODS_FIELD_NUMBER: _ClassVar[int]
    tags: _containers.RepeatedCompositeFieldContainer[Meta.Tag]
    methods: _containers.RepeatedCompositeFieldContainer[Meta.Method]
    def __init__(self, tags: _Optional[_Iterable[_Union[Meta.Tag, _Mapping]]] = ..., methods: _Optional[_Iterable[_Union[Meta.Method, _Mapping]]] = ...) -> None: ...
