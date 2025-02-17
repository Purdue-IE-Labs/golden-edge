from . import tag_data_pb2 as _tag_data_pb2
from . import method_pb2 as _method_pb2
from . import prop_pb2 as _prop_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Meta(_message.Message):
    __slots__ = ("tracking", "key", "tags", "methods")
    class WriteResponse(_message.Message):
        __slots__ = ("code", "success", "props")
        class PropsEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: _prop_pb2.Prop
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_prop_pb2.Prop, _Mapping]] = ...) -> None: ...
        CODE_FIELD_NUMBER: _ClassVar[int]
        SUCCESS_FIELD_NUMBER: _ClassVar[int]
        PROPS_FIELD_NUMBER: _ClassVar[int]
        code: int
        success: bool
        props: _containers.MessageMap[str, _prop_pb2.Prop]
        def __init__(self, code: _Optional[int] = ..., success: bool = ..., props: _Optional[_Mapping[str, _prop_pb2.Prop]] = ...) -> None: ...
    class Tag(_message.Message):
        __slots__ = ("path", "type", "props", "writable", "responses")
        class PropsEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: _prop_pb2.Prop
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_prop_pb2.Prop, _Mapping]] = ...) -> None: ...
        PATH_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        PROPS_FIELD_NUMBER: _ClassVar[int]
        WRITABLE_FIELD_NUMBER: _ClassVar[int]
        RESPONSES_FIELD_NUMBER: _ClassVar[int]
        path: str
        type: _tag_data_pb2.DataType
        props: _containers.MessageMap[str, _prop_pb2.Prop]
        writable: bool
        responses: _containers.RepeatedCompositeFieldContainer[Meta.WriteResponse]
        def __init__(self, path: _Optional[str] = ..., type: _Optional[_Union[_tag_data_pb2.DataType, str]] = ..., props: _Optional[_Mapping[str, _prop_pb2.Prop]] = ..., writable: bool = ..., responses: _Optional[_Iterable[_Union[Meta.WriteResponse, _Mapping]]] = ...) -> None: ...
    TRACKING_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    METHODS_FIELD_NUMBER: _ClassVar[int]
    tracking: bool
    key: str
    tags: _containers.RepeatedCompositeFieldContainer[Meta.Tag]
    methods: _containers.RepeatedCompositeFieldContainer[_method_pb2.Method]
    def __init__(self, tracking: bool = ..., key: _Optional[str] = ..., tags: _Optional[_Iterable[_Union[Meta.Tag, _Mapping]]] = ..., methods: _Optional[_Iterable[_Union[_method_pb2.Method, _Mapping]]] = ...) -> None: ...
