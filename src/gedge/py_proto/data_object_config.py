from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Self, TYPE_CHECKING, final

from gedge import proto
from gedge.node.data_type import DataType
from gedge.py_proto.base_type import BaseType
from gedge.py_proto.config import Config
from gedge.py_proto.data_model_config import DataModelItemConfig
from gedge.py_proto.data_model_object_config import DataModelObjectConfig
from gedge.py_proto.data_model_type import DataModelType

if TYPE_CHECKING:
    from gedge.py_proto.data_model_config import DataModelConfig
    from gedge.py_proto.props import Props
    from gedge.comm.comm import Comm

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
    def from_json5(cls, json: Any) -> Self:
        from gedge.py_proto.props import Props
        if not isinstance(json, dict):
            raise ValueError
        props = Props.from_json5(json.get("props", {}))
        if not (("base_type" in json) ^ ("model_path" in json) ^ ("model" in json)):
            raise ValueError
        if json.get("base_type"):
            config = Config.from_json5(json["base_type"], True)
        elif json.get("model_path"):
            config = Config.from_json5(json["model_path"], False)
        else:
            config = Config.from_json5(json["model"], False)
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
    
    def set_model_config(self, model: DataModelConfig) -> bool:
        if not self.is_model_type():
            return False
        self.config.config.repr = model # type: ignore
        return True
    
    def set_model_path(self, path: str) -> bool:
        if not self.is_model_type():
            return False
        self.config.config.repr = DataModelType(path) # type: ignore
        return True
    
    def to_model_path(self) -> bool:
        if self.is_model_path():
            return True
        model = self.get_model_config()
        if not model:
            return False
        path = model.path
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
    
    def fetch(self, comm: Comm) -> bool:
        path = self.get_model_path()
        if not path:
            return True
        model = comm.pull_model(path.path)
        if not model:
            return False
        self.set_model_config(model)
        return True
