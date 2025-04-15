from . import type_pb2 as _type_pb2
from . import props_pb2 as _props_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataModelConfig(_message.Message):
    __slots__ = ("type", "extends_path", "version", "items")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    EXTENDS_PATH_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    type: _type_pb2.DataModelType
    extends_path: str
    version: int
    items: _containers.RepeatedCompositeFieldContainer[DataModelItemConfig]
    def __init__(self, type: _Optional[_Union[_type_pb2.DataModelType, _Mapping]] = ..., extends_path: _Optional[str] = ..., version: _Optional[int] = ..., items: _Optional[_Iterable[_Union[DataModelItemConfig, _Mapping]]] = ...) -> None: ...

class DataModelItemConfig(_message.Message):
    __slots__ = ("path", "config")
    PATH_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    path: str
    config: DataObjectConfig
    def __init__(self, path: _Optional[str] = ..., config: _Optional[_Union[DataObjectConfig, _Mapping]] = ...) -> None: ...

class DataObjectConfig(_message.Message):
    __slots__ = ("base_config", "data_model_config", "props")
    BASE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DATA_MODEL_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    base_config: _type_pb2.BaseType
    data_model_config: DataModelConfig
    props: _props_pb2.Props
    def __init__(self, base_config: _Optional[_Union[_type_pb2.BaseType, str]] = ..., data_model_config: _Optional[_Union[DataModelConfig, _Mapping]] = ..., props: _Optional[_Union[_props_pb2.Props, _Mapping]] = ...) -> None: ...

class DataModelConfigFetched(_message.Message):
    __slots__ = ("type", "extends_path", "version", "items")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    EXTENDS_PATH_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    type: _type_pb2.DataModelType
    extends_path: str
    version: int
    items: _containers.RepeatedCompositeFieldContainer[DataModelItemConfigFetched]
    def __init__(self, type: _Optional[_Union[_type_pb2.DataModelType, _Mapping]] = ..., extends_path: _Optional[str] = ..., version: _Optional[int] = ..., items: _Optional[_Iterable[_Union[DataModelItemConfigFetched, _Mapping]]] = ...) -> None: ...

class DataModelItemConfigFetched(_message.Message):
    __slots__ = ("path", "config")
    PATH_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    path: str
    config: DataObjectConfigFetched
    def __init__(self, path: _Optional[str] = ..., config: _Optional[_Union[DataObjectConfigFetched, _Mapping]] = ...) -> None: ...

class DataObjectConfigFetched(_message.Message):
    __slots__ = ("base_config", "data_model_config", "props")
    BASE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DATA_MODEL_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    base_config: _type_pb2.BaseType
    data_model_config: DataModelConfigFetched
    props: _props_pb2.Props
    def __init__(self, base_config: _Optional[_Union[_type_pb2.BaseType, str]] = ..., data_model_config: _Optional[_Union[DataModelConfigFetched, _Mapping]] = ..., props: _Optional[_Union[_props_pb2.Props, _Mapping]] = ...) -> None: ...
