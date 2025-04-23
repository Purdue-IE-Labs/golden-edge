from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Self, TYPE_CHECKING

from gedge import proto
from gedge.comm import keys

if TYPE_CHECKING:
    from gedge.py_proto.data_model_config import DataModelConfig

'''
This will not include MODELS/ but will be able to convert to a path with a version
'''
@dataclass
class DataModelType:
    path: str
    version: int | None = field(default=None)

    @property
    def full_path(self):
        if not self.version:
            return self.path
        return keys.key_join(self.path, keys.VERSION, str(self.version))
    
    @classmethod
    def from_model(cls, model: DataModelConfig) -> Self:
        return cls(model.path, model.version)

    def to_proto(self) -> proto.DataModelType:
        return proto.DataModelType(path=self.path, version=self.version)

    @classmethod
    def from_proto(cls, proto: proto.DataModelType):
        return cls(proto.path, proto.version)
    
    def to_json5(self) -> str:
        return self.full_path
    
    def to_file_path(self) -> str:
        return f"{self.path}/v{self.version}.json5"
    
    @classmethod
    def from_json5(cls, json5: Any) -> Self:
        assert isinstance(json5, str)
        components = json5.split("/")
        if keys.VERSION in components:
            version = int(components[-1])
            path = keys.key_join(*components[:-2])
            return cls(path, version)
        return cls(keys.key_join(*components))
    