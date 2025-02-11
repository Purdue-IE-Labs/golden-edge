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
    __slots__ = ("tracking", "key", "tags", "methods")
    class Method(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class WriteResponse(_message.Message):
        __slots__ = ("code", "success", "properties")
        class PropertiesEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: Property
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Property, _Mapping]] = ...) -> None: ...
        CODE_FIELD_NUMBER: _ClassVar[int]
        SUCCESS_FIELD_NUMBER: _ClassVar[int]
        PROPERTIES_FIELD_NUMBER: _ClassVar[int]
        code: int
        success: bool
        properties: _containers.MessageMap[str, Property]
        def __init__(self, code: _Optional[int] = ..., success: bool = ..., properties: _Optional[_Mapping[str, Property]] = ...) -> None: ...
    class WriteResponseData(_message.Message):
        __slots__ = ("code", "error")
        CODE_FIELD_NUMBER: _ClassVar[int]
        ERROR_FIELD_NUMBER: _ClassVar[int]
        code: int
        error: str
        def __init__(self, code: _Optional[int] = ..., error: _Optional[str] = ...) -> None: ...
    class Tag(_message.Message):
        __slots__ = ("path", "type", "properties", "writable", "responses")
        class PropertiesEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: Property
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Property, _Mapping]] = ...) -> None: ...
        PATH_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        PROPERTIES_FIELD_NUMBER: _ClassVar[int]
        WRITABLE_FIELD_NUMBER: _ClassVar[int]
        RESPONSES_FIELD_NUMBER: _ClassVar[int]
        path: str
        type: _tag_data_pb2.DataType
        properties: _containers.MessageMap[str, Property]
        writable: bool
        responses: _containers.RepeatedCompositeFieldContainer[Meta.WriteResponse]
        def __init__(self, path: _Optional[str] = ..., type: _Optional[_Union[_tag_data_pb2.DataType, str]] = ..., properties: _Optional[_Mapping[str, Property]] = ..., writable: bool = ..., responses: _Optional[_Iterable[_Union[Meta.WriteResponse, _Mapping]]] = ...) -> None: ...
    TRACKING_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    METHODS_FIELD_NUMBER: _ClassVar[int]
    tracking: bool
    key: str
    tags: _containers.RepeatedCompositeFieldContainer[Meta.Tag]
    methods: _containers.RepeatedCompositeFieldContainer[Meta.Method]
    def __init__(self, tracking: bool = ..., key: _Optional[str] = ..., tags: _Optional[_Iterable[_Union[Meta.Tag, _Mapping]]] = ..., methods: _Optional[_Iterable[_Union[Meta.Method, _Mapping]]] = ...) -> None: ...
