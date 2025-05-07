from . import data_model_config_pb2 as _data_model_config_pb2
from . import response_config_pb2 as _response_config_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TagConfig(_message.Message):
    __slots__ = ("data_config", "write_config", "group_config")
    DATA_CONFIG_FIELD_NUMBER: _ClassVar[int]
    WRITE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    GROUP_CONFIG_FIELD_NUMBER: _ClassVar[int]
    data_config: _containers.RepeatedCompositeFieldContainer[_data_model_config_pb2.DataItemConfig]
    write_config: _containers.RepeatedCompositeFieldContainer[TagWriteConfig]
    group_config: _containers.RepeatedCompositeFieldContainer[TagGroupConfig]
    def __init__(self, data_config: _Optional[_Iterable[_Union[_data_model_config_pb2.DataItemConfig, _Mapping]]] = ..., write_config: _Optional[_Iterable[_Union[TagWriteConfig, _Mapping]]] = ..., group_config: _Optional[_Iterable[_Union[TagGroupConfig, _Mapping]]] = ...) -> None: ...

class TagWriteConfig(_message.Message):
    __slots__ = ("path", "responses")
    PATH_FIELD_NUMBER: _ClassVar[int]
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    path: str
    responses: _containers.RepeatedCompositeFieldContainer[_response_config_pb2.ResponseConfig]
    def __init__(self, path: _Optional[str] = ..., responses: _Optional[_Iterable[_Union[_response_config_pb2.ResponseConfig, _Mapping]]] = ...) -> None: ...

class TagGroupConfig(_message.Message):
    __slots__ = ("path", "items", "writable", "responses")
    PATH_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    WRITABLE_FIELD_NUMBER: _ClassVar[int]
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    path: str
    items: _containers.RepeatedScalarFieldContainer[str]
    writable: bool
    responses: _containers.RepeatedCompositeFieldContainer[_response_config_pb2.ResponseConfig]
    def __init__(self, path: _Optional[str] = ..., items: _Optional[_Iterable[str]] = ..., writable: bool = ..., responses: _Optional[_Iterable[_Union[_response_config_pb2.ResponseConfig, _Mapping]]] = ...) -> None: ...
