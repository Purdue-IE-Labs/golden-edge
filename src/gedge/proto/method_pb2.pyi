from . import tag_data_pb2 as _tag_data_pb2
from . import prop_pb2 as _prop_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Method(_message.Message):
    __slots__ = ("path", "props", "parameters", "responses")
    class PropsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _prop_pb2.Prop
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_prop_pb2.Prop, _Mapping]] = ...) -> None: ...
    class ParametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _tag_data_pb2.DataType
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_tag_data_pb2.DataType, str]] = ...) -> None: ...
    PATH_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    path: str
    props: _containers.MessageMap[str, _prop_pb2.Prop]
    parameters: _containers.ScalarMap[str, _tag_data_pb2.DataType]
    responses: _containers.RepeatedCompositeFieldContainer[Response]
    def __init__(self, path: _Optional[str] = ..., props: _Optional[_Mapping[str, _prop_pb2.Prop]] = ..., parameters: _Optional[_Mapping[str, _tag_data_pb2.DataType]] = ..., responses: _Optional[_Iterable[_Union[Response, _Mapping]]] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ("code", "success", "props", "body", "final")
    class PropsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _prop_pb2.Prop
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_prop_pb2.Prop, _Mapping]] = ...) -> None: ...
    class BodyEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _tag_data_pb2.DataType
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_tag_data_pb2.DataType, str]] = ...) -> None: ...
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    FINAL_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    props: _containers.MessageMap[str, _prop_pb2.Prop]
    body: _containers.ScalarMap[str, _tag_data_pb2.DataType]
    final: bool
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., props: _Optional[_Mapping[str, _prop_pb2.Prop]] = ..., body: _Optional[_Mapping[str, _tag_data_pb2.DataType]] = ..., final: bool = ...) -> None: ...

class MethodCall(_message.Message):
    __slots__ = ("parameters",)
    class ParametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _tag_data_pb2.TagData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_tag_data_pb2.TagData, _Mapping]] = ...) -> None: ...
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    parameters: _containers.MessageMap[str, _tag_data_pb2.TagData]
    def __init__(self, parameters: _Optional[_Mapping[str, _tag_data_pb2.TagData]] = ...) -> None: ...

class ResponseData(_message.Message):
    __slots__ = ("code", "body", "error")
    class BodyEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _tag_data_pb2.TagData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_tag_data_pb2.TagData, _Mapping]] = ...) -> None: ...
    CODE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    code: int
    body: _containers.MessageMap[str, _tag_data_pb2.TagData]
    error: str
    def __init__(self, code: _Optional[int] = ..., body: _Optional[_Mapping[str, _tag_data_pb2.TagData]] = ..., error: _Optional[str] = ...) -> None: ...
