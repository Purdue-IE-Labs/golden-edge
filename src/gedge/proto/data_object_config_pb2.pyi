from . import type_pb2 as _type_pb2
from . import data_model_config_pb2 as _data_model_config_pb2
from . import props_pb2 as _props_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataObjectConfig(_message.Message):
    __slots__ = ("base_config", "data_model_config", "props")
    BASE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DATA_MODEL_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    base_config: _type_pb2.BaseType
    data_model_config: _data_model_config_pb2.DataModelConfig
    props: _props_pb2.Props
    def __init__(self, base_config: _Optional[_Union[_type_pb2.BaseType, str]] = ..., data_model_config: _Optional[_Union[_data_model_config_pb2.DataModelConfig, _Mapping]] = ..., props: _Optional[_Union[_props_pb2.Props, _Mapping]] = ...) -> None: ...
