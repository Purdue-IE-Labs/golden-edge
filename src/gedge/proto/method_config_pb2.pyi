from . import props_pb2 as _props_pb2
from . import params_config_pb2 as _params_config_pb2
from . import body_config_pb2 as _body_config_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MethodConfig(_message.Message):
    __slots__ = ("path", "props", "params", "responses")
    PATH_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    path: str
    props: _props_pb2.Props
    params: _params_config_pb2.ParamsConfig
    responses: _containers.RepeatedCompositeFieldContainer[MethodResponseConfig]
    def __init__(self, path: _Optional[str] = ..., props: _Optional[_Union[_props_pb2.Props, _Mapping]] = ..., params: _Optional[_Union[_params_config_pb2.ParamsConfig, _Mapping]] = ..., responses: _Optional[_Iterable[_Union[MethodResponseConfig, _Mapping]]] = ...) -> None: ...

class MethodResponseConfig(_message.Message):
    __slots__ = ("code", "props", "body")
    CODE_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    code: int
    props: _props_pb2.Props
    body: _body_config_pb2.BodyConfig
    def __init__(self, code: _Optional[int] = ..., props: _Optional[_Union[_props_pb2.Props, _Mapping]] = ..., body: _Optional[_Union[_body_config_pb2.BodyConfig, _Mapping]] = ...) -> None: ...
