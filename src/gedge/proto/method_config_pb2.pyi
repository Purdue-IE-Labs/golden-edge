from . import response_config_pb2 as _response_config_pb2
from . import data_model_config_pb2 as _data_model_config_pb2
from . import prop_pb2 as _prop_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MethodConfig(_message.Message):
    __slots__ = ("path", "params", "responses", "props")
    PATH_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    path: str
    params: _containers.RepeatedCompositeFieldContainer[_data_model_config_pb2.DataItemConfig]
    responses: _containers.RepeatedCompositeFieldContainer[_response_config_pb2.ResponseConfig]
    props: _containers.RepeatedCompositeFieldContainer[_prop_pb2.Prop]
    def __init__(self, path: _Optional[str] = ..., params: _Optional[_Iterable[_Union[_data_model_config_pb2.DataItemConfig, _Mapping]]] = ..., responses: _Optional[_Iterable[_Union[_response_config_pb2.ResponseConfig, _Mapping]]] = ..., props: _Optional[_Iterable[_Union[_prop_pb2.Prop, _Mapping]]] = ...) -> None: ...
