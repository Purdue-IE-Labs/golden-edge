from . import data_model_config_pb2 as _data_model_config_pb2
from . import prop_pb2 as _prop_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResponseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OK: _ClassVar[ResponseType]
    ERR: _ClassVar[ResponseType]
    INFO: _ClassVar[ResponseType]
OK: ResponseType
ERR: ResponseType
INFO: ResponseType

class ResponseConfig(_message.Message):
    __slots__ = ("code", "type", "body", "props")
    CODE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    code: int
    type: ResponseType
    body: _containers.RepeatedCompositeFieldContainer[_data_model_config_pb2.DataItemConfig]
    props: _containers.RepeatedCompositeFieldContainer[_prop_pb2.Prop]
    def __init__(self, code: _Optional[int] = ..., type: _Optional[_Union[ResponseType, str]] = ..., body: _Optional[_Iterable[_Union[_data_model_config_pb2.DataItemConfig, _Mapping]]] = ..., props: _Optional[_Iterable[_Union[_prop_pb2.Prop, _Mapping]]] = ...) -> None: ...
