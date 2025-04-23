from dataclasses import dataclass
from typing import Any, Self

from gedge import proto
from gedge.py_proto.base_type import BaseType
from gedge.py_proto.data_model_config import DataModelItemConfig
from gedge.py_proto.data_model_object_config import DataModelObjectConfig


@dataclass
class Config:
    config: BaseType | DataModelObjectConfig

    def to_proto(self) -> proto.Config:
        if isinstance(self.config, BaseType):
            return proto.Config(base_config=self.config.to_proto())
        else:
            return proto.Config(data_model_config=self.config.to_proto())
    
    @classmethod
    def from_proto(cls, proto: proto.Config) -> Self:
        oneof = proto.WhichOneof("config")
        if oneof == "base_config":
            return cls(BaseType.from_proto(proto.base_config))
        elif oneof == "data_model_config":
            return cls(DataModelObjectConfig.from_proto(proto.data_model_config))
        else:
            raise LookupError("No value set in Config proto")
    
    @classmethod
    def from_json5(cls, json5: Any, is_base: bool = False) -> Self:
        if is_base:
            res = BaseType.from_json5(json5)
        else:
            res = DataModelObjectConfig.from_json5(json5)
        return cls(res)
    
    def to_json5(self):
        return self.config.to_json5()
    
    def is_base_type(self) -> bool:
        return isinstance(self.config, BaseType)
    
    def is_model_object_config(self) -> bool:
        return isinstance(self.config, DataModelObjectConfig)
    
    def get_base_type(self) -> BaseType | None:
        if not self.is_base_type():
            return None
        return self.config # type: ignore
    
    def get_model_object_config(self) -> DataModelObjectConfig | None:
        if not self.is_model_object_config():
            return None
        return self.config # type: ignore
    
    def get_model_items(self) -> list[DataModelItemConfig] | None:
        if not self.is_model_object_config():
            return None
        model = self.config.get_embedded() # type: ignore
        if not model:
            return None
        return model.items

