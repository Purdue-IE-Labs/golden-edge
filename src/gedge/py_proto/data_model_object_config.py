from __future__ import annotations

from dataclasses import dataclass
from tkinter import W
from typing import TYPE_CHECKING, Any, Self

import json5

from gedge.py_proto.data_model_config import DataModelConfig
from gedge.py_proto.data_model_type import DataModelType
from gedge import proto
from gedge.py_proto.singleton import Singleton

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
        oneof = proto.WhichOneof("repr")
        if oneof == "path":
            return cls(DataModelType.from_proto(proto.path))
        elif oneof == "embedded":
            return cls(DataModelConfig.from_proto(proto.embedded))
        else:
            raise Exception("none of the fields set")
    
    @classmethod
    def from_json5(cls, json5: Any) -> Self:
        if isinstance(json5, dict):
            return cls(DataModelConfig.from_json5(json5))
        return cls(DataModelType.from_json5(json5))
    
    def to_json5(self) -> dict | str:
        return self.repr.to_json5()
    
    def fetch(self, comm: Comm) -> DataModelConfig | None:
        if self.is_embedded():
            return None
        model = comm.pull_model(self.repr.path)
        if not model:
            return None
        self.repr = model
        return model
    
    def load(self, path: DataModelType) -> DataModelConfig:
        config = load(path)
        self.repr = config
        return config
    
    def is_path(self):
        return isinstance(self.repr, DataModelType)
    
    def is_embedded(self):
        return isinstance(self.repr, DataModelConfig)
    
    def get_path(self) -> DataModelType | None:
        if self.is_path():
            return self.repr # type: ignore
        return self.repr.path # type: ignore

    def get_embedded(self) -> DataModelConfig | None:
        if not self.is_embedded():
            return None
        return self.repr # type: ignore


def load(path: DataModelType) -> DataModelConfig:
    directory = Singleton().get_model_dir()
    print(directory, path.path)
    # TODO: need to include version
    path_to_json = f"{directory}/{path.path}/v1.json5"
    with open(path_to_json, "r") as f:
        j = json5.load(f)
    config = DataModelConfig.from_json5(j)
    return config