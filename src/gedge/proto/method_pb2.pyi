from . import tag_data_pb2 as _tag_data_pb2
from . import prop_pb2 as _prop_pb2
from . import param_pb2 as _param_pb2
from . import body_pb2 as _body_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Method(_message.Message):
    __slots__ = ("path", "props", "params", "responses")
    class PropsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _prop_pb2.Prop
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_prop_pb2.Prop, _Mapping]] = ...) -> None: ...
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _param_pb2.Param
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_param_pb2.Param, _Mapping]] = ...) -> None: ...
    PATH_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    path: str
    props: _containers.MessageMap[str, _prop_pb2.Prop]
    params: _containers.MessageMap[str, _param_pb2.Param]
    responses: _containers.RepeatedCompositeFieldContainer[Response]
    def __init__(self, path: _Optional[str] = ..., props: _Optional[_Mapping[str, _prop_pb2.Prop]] = ..., params: _Optional[_Mapping[str, _param_pb2.Param]] = ..., responses: _Optional[_Iterable[_Union[Response, _Mapping]]] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ("code", "props", "body")
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
        value: _body_pb2.Body
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_body_pb2.Body, _Mapping]] = ...) -> None: ...
    CODE_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    code: int
    props: _containers.MessageMap[str, _prop_pb2.Prop]
    body: _containers.MessageMap[str, _body_pb2.Body]
    def __init__(self, code: _Optional[int] = ..., props: _Optional[_Mapping[str, _prop_pb2.Prop]] = ..., body: _Optional[_Mapping[str, _body_pb2.Body]] = ...) -> None: ...

class MethodQueryData(_message.Message):
    __slots__ = ("params",)
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _tag_data_pb2.TagData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_tag_data_pb2.TagData, _Mapping]] = ...) -> None: ...
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    params: _containers.MessageMap[str, _tag_data_pb2.TagData]
    def __init__(self, params: _Optional[_Mapping[str, _tag_data_pb2.TagData]] = ...) -> None: ...

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
