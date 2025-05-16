from . import method_config_pb2 as _method_config_pb2
from . import tag_config_pb2 as _tag_config_pb2
from . import subnode_config_pb2 as _subnode_config_pb2
from . import data_model_config_pb2 as _data_model_config_pb2
from . import prop_pb2 as _prop_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Meta(_message.Message):
    __slots__ = ("key", "tags", "methods", "subnodes", "models", "props")
    KEY_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    METHODS_FIELD_NUMBER: _ClassVar[int]
    SUBNODES_FIELD_NUMBER: _ClassVar[int]
    MODELS_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    key: str
    tags: _tag_config_pb2.TagConfig
    methods: _containers.RepeatedCompositeFieldContainer[_method_config_pb2.MethodConfig]
    subnodes: _containers.RepeatedCompositeFieldContainer[_subnode_config_pb2.SubnodeConfig]
    models: _containers.RepeatedCompositeFieldContainer[_data_model_config_pb2.DataModelConfig]
    props: _containers.RepeatedCompositeFieldContainer[_prop_pb2.Prop]
    def __init__(self, key: _Optional[str] = ..., tags: _Optional[_Union[_tag_config_pb2.TagConfig, _Mapping]] = ..., methods: _Optional[_Iterable[_Union[_method_config_pb2.MethodConfig, _Mapping]]] = ..., subnodes: _Optional[_Iterable[_Union[_subnode_config_pb2.SubnodeConfig, _Mapping]]] = ..., models: _Optional[_Iterable[_Union[_data_model_config_pb2.DataModelConfig, _Mapping]]] = ..., props: _Optional[_Iterable[_Union[_prop_pb2.Prop, _Mapping]]] = ...) -> None: ...
