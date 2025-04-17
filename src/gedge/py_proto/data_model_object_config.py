from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from gedge.py_proto.data_model_config import DataModelConfig
from gedge.py_proto.data_model_type import DataModelType
from gedge import proto

if TYPE_CHECKING:
    from gedge.comm.comm import Comm

@dataclass
class DataModelObjectConfig:
    repr: DataModelType | DataModelConfig

    def to_proto(self) -> proto.DataModelObjectConfig:
        if isinstance(self.repr, DataModelType):
            return proto.DataModelObjectConfig(path=self.repr.to_proto())
        else:
            return proto.DataModelObjectConfig(embedded=self.repr.to_proto())

    @classmethod
    def from_proto(cls, proto: proto.DataModelObjectConfig) -> Self:
        if proto.path:
            return cls(DataModelType.from_proto(proto.path))
        else:
            return cls(DataModelConfig.from_proto(proto.embedded))
    
    @classmethod
    def from_json5(cls, json5: Any) -> Self:
        if isinstance(json5, dict):
            return cls(DataModelConfig.from_json5(json5))
        return cls(DataModelType.from_json5(json5))
    
    def to_json5(self) -> dict | str:
        return self.repr.to_json5()
    
    def fetch(self, comm: Comm):
        if isinstance(self.repr, DataModelConfig):
            return self.repr
        self.repr = comm.pull_model(self.repr.path)
        
