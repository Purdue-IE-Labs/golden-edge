from . import type_pb2 as _type_pb2
from . import data_model_session_pb2 as _data_model_session_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataModelConfig(_message.Message):
    __slots__ = ("path", "extends_path", "version", "items")
    PATH_FIELD_NUMBER: _ClassVar[int]
    EXTENDS_PATH_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    path: str
    extends_path: str
    version: int
    items: _containers.RepeatedCompositeFieldContainer[DataModelItemConfig]
    def __init__(self, path: _Optional[str] = ..., extends_path: _Optional[str] = ..., version: _Optional[int] = ..., items: _Optional[_Iterable[_Union[DataModelItemConfig, _Mapping]]] = ...) -> None: ...

class DataModelItemConfig(_message.Message):
    __slots__ = ("path", "config")
    PATH_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    path: str
    config: DataObjectConfig
    def __init__(self, path: _Optional[str] = ..., config: _Optional[_Union[DataObjectConfig, _Mapping]] = ...) -> None: ...

class DataObjectConfig(_message.Message):
    __slots__ = ("config", "props")
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    config: Config
    props: Props
    def __init__(self, config: _Optional[_Union[Config, _Mapping]] = ..., props: _Optional[_Union[Props, _Mapping]] = ...) -> None: ...

class DataModelObjectConfig(_message.Message):
    __slots__ = ("path", "embedded")
    PATH_FIELD_NUMBER: _ClassVar[int]
    EMBEDDED_FIELD_NUMBER: _ClassVar[int]
    path: _type_pb2.DataModelType
    embedded: DataModelConfig
    def __init__(self, path: _Optional[_Union[_type_pb2.DataModelType, _Mapping]] = ..., embedded: _Optional[_Union[DataModelConfig, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("base_config", "data_model_config")
    BASE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DATA_MODEL_CONFIG_FIELD_NUMBER: _ClassVar[int]
    base_config: _type_pb2.BaseType
    data_model_config: DataModelObjectConfig
    def __init__(self, base_config: _Optional[_Union[_type_pb2.BaseType, str]] = ..., data_model_config: _Optional[_Union[DataModelObjectConfig, _Mapping]] = ...) -> None: ...

class Prop(_message.Message):
    __slots__ = ("config", "value")
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    config: Config
    value: _data_model_session_pb2.DataObject
    def __init__(self, config: _Optional[_Union[Config, _Mapping]] = ..., value: _Optional[_Union[_data_model_session_pb2.DataObject, _Mapping]] = ...) -> None: ...

class Props(_message.Message):
    __slots__ = ("props",)
    class PropsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Prop
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Prop, _Mapping]] = ...) -> None: ...
    PROPS_FIELD_NUMBER: _ClassVar[int]
    props: _containers.MessageMap[str, Prop]
    def __init__(self, props: _Optional[_Mapping[str, Prop]] = ...) -> None: ...
