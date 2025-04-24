from __future__ import annotations

from dataclasses import dataclass
from multiprocessing import Value
import pathlib
from typing import Any, Self, TYPE_CHECKING, final
import logging

from gedge import proto
from gedge.comm import keys
from gedge.py_proto.base_type import BaseType
from gedge.py_proto.config import Config
from gedge.py_proto.data_model_config import DataModelItemConfig
from gedge.py_proto.data_model_object_config import DataModelObjectConfig, load, load_from_file
from gedge.py_proto.data_model_type import DataModelType
from gedge.py_proto.singleton import Singleton

if TYPE_CHECKING:
    from gedge.py_proto.data_model_config import DataModelConfig
    from gedge.py_proto.props import Props
    from gedge.comm.comm import Comm

logger = logging.getLogger(__file__)

@dataclass
class DataObjectConfig:
    config: Config
    props: Props

    def to_proto(self) -> proto.DataObjectConfig:
        props = self.props.to_proto()
        config = self.config.to_proto()
        return proto.DataObjectConfig(config=config, props=props)
    
    @classmethod
    def from_proto(cls, proto: proto.DataObjectConfig) -> Self:
        from gedge.py_proto.props import Props
        config = Config.from_proto(proto.config)
        props = Props.from_proto(proto.props)
        return cls(config, props)
    
    def to_json5(self) -> dict:
        raise NotImplementedError
    
    @classmethod
    def from_json5(cls, j: Any) -> Self:
        from gedge.py_proto.props import Props
        if not isinstance(j, dict):
            raise ValueError
        config = Config.from_json5(j)
        props = Props.from_json5(j.get("props", {}))
        return cls(config, props)
    
    @classmethod
    def from_model_config(cls, model: DataModelConfig) -> Self:
        from gedge.py_proto.props import Props
        config = Config(DataModelObjectConfig(model))
        props = Props.empty()
        return cls(config, props)
    
    @classmethod
    def from_config(cls, config: Config) -> Self:
        from gedge.py_proto.props import Props
        props = Props.empty()
        return cls(config, props)
    
    @classmethod
    def from_base_type(cls, type: BaseType) -> Self:
        from gedge.py_proto.props import Props
        config = Config(type)
        props = Props.empty()
        return cls(config, props)
    
    @classmethod
    def from_model_path(cls, path: str) -> Self:
        from gedge.py_proto.props import Props
        config = Config(DataModelObjectConfig(DataModelType(path)))
        props = Props.empty()
        return cls(config, props)
    
    def is_base_type(self) -> bool:
        return isinstance(self.config.config, BaseType)
    
    def is_model_type(self) -> bool:
        return isinstance(self.config.config, DataModelObjectConfig)
    
    def is_model_path(self) -> bool:
        return self.is_model_type() and isinstance(self.config.config.repr, DataModelType) # type: ignore
    
    def is_model_object(self) -> bool:
        from gedge.py_proto.data_model_config import DataModelConfig
        return self.is_model_type() and isinstance(self.config.config.repr, DataModelConfig) # type: ignore
    
    def get_base_type(self) -> BaseType | None:
        if not self.is_base_type():
            return None
        return self.config.config # type: ignore
    
    def get_model_path(self) -> DataModelType | None:
        if not self.is_model_path():
            return None
        return self.config.config.repr # type: ignore
    
    def get_model_config(self) -> DataModelConfig | None:
        if not self.is_model_object():
            return None
        return self.config.config.repr # type: ignore
    
    def get_model_type(self) -> DataModelObjectConfig | None:
        if not self.is_model_type():
            return None
        return self.config.config # type: ignore
    
    def set_model_config(self, model: DataModelConfig) -> bool:
        if not self.is_model_type():
            return False
        self.config.config.repr = model # type: ignore
        return True
    
    def set_model_path(self, path: DataModelType) -> bool:
        if not self.is_model_type():
            return False
        self.config.config.repr = path # type: ignore
        return True
    
    def to_model_path(self) -> bool:
        if self.is_model_path():
            return True
        model = self.get_model_config()
        if not model:
            return False
        path = DataModelType.from_model(model)
        return self.set_model_path(path)
    
    def get_config_items(self) -> list[DataObjectConfig] | None:
        items = self.get_model_items()
        if items is None:
            return None
        return [i.config for i in items]
    
    def get_model_items(self) -> list[DataModelItemConfig] | None:
        model = self.get_model_config()
        if model is None:
            return None
        return [i for i in model.items]
