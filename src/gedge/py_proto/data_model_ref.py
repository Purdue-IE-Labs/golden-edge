from __future__ import annotations

from dataclasses import dataclass, field
import pathlib
from typing import Any, Self, TYPE_CHECKING

import json5

from gedge import proto
from gedge.comm import keys
from gedge.py_proto.load_models import load, to_file_path
from gedge.py_proto.singleton import Singleton

if TYPE_CHECKING:
    from gedge.py_proto.data_model_config import DataModelConfig

'''
This will not include MODELS/ but will be able to convert to a path with a version
'''
@dataclass
class DataModelRef:
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

    def to_proto(self) -> proto.DataModelRef:
        return proto.DataModelRef(path=self.path, version=self.version)

    @classmethod
    def from_proto(cls, proto: proto.DataModelRef):
        if proto.HasField("version"):
            return cls(proto.path, proto.version)
        return cls(proto.path)
    
    def to_json5(self) -> str:
        return self.full_path
    
    def to_file_path(self) -> str:
        if not self.version:
            raise LookupError(f"Must provide version to get file path of model {self.full_path}")
        return to_file_path(self.path, self.version)
    
    # TODO: what should a dictionary parent look like
    @classmethod
    def from_json5(cls, json5: Any) -> Self:
        if isinstance(json5, dict):
            if "model_path" not in json5:
                raise ValueError(f"Invalid model ref {json5}, must specify either a base_type or a model_path")
            return cls.from_json5(json5["model_path"])

        components = json5.split("/")
        if keys.VERSION in components:
            version = int(components[-1])
            path = keys.key_join(*components[:-2])
            return cls(path, version)
        return cls(keys.key_join(*components))
    
    def load_model(self) -> DataModelConfig:
        m = load(self)
        m.add_parent_tags()
        return m