from __future__ import annotations

from dataclasses import dataclass
import pathlib
from typing import TYPE_CHECKING, Any, Self

import json5

from gedge.py_proto.data_model_type import DataModelType
from gedge import proto
from gedge.py_proto.singleton import Singleton

if TYPE_CHECKING:
    from gedge.comm.comm import Comm
    from gedge.py_proto.data_model_config import DataModelConfig

@dataclass
class DataModelObjectConfig:
    repr: DataModelType | DataModelConfig

    @property
    def path(self) -> str:
        if self.is_path():
            return self.repr.full_path # type: ignore
        return DataModelType(self.repr.path, self.repr.version).full_path

    def to_proto(self) -> proto.DataModelObjectConfig:
        if isinstance(self.repr, DataModelType):
            return proto.DataModelObjectConfig(path=self.repr.to_proto())
        return proto.DataModelObjectConfig(embedded=self.repr.to_proto())

    @classmethod
    def from_proto(cls, proto: proto.DataModelObjectConfig) -> Self:
        from gedge.py_proto.data_model_config import DataModelConfig
        oneof = proto.WhichOneof("repr")
        if oneof == "path":
            return cls(DataModelType.from_proto(proto.path))
        elif oneof == "embedded":
            return cls(DataModelConfig.from_proto(proto.embedded))
        else:
            raise ValueError(f"none of fields for DataModelObjectConfig were set")
    
    @classmethod
    def from_json5(cls, j: Any) -> Self:
        if not isinstance(j, dict):
            raise ValueError(f"Invalid json {j} for data model configuration")

        if not (("model_path" in j) ^ ("model" in j) ^ ("model_file" in j)):
            raise LookupError(f"Model object must set one and only one of ['model_path', 'model', 'model_file']")

        elif j.get("model_path"):
            config = DataModelType.from_json5(j["model_path"])
        elif j.get("model_file"):
            json5_dir = Singleton().get_json5_dir()
            if not json5_dir:
                raise ValueError
            path = pathlib.Path(json5_dir) / j["model_file"]
            config = load_from_file(str(path))
        else:
            config = DataModelConfig.from_json5(j["model"])
        return cls(config)
    
    def to_json5(self) -> dict:
        """
        We never put the file back in the json when we're writing it, that's only a convenience things for the user
        """
        j = {}
        if self.is_embedded():
            j["model"] = self.repr.to_json5()
        else:
            j["model_path"] = self.repr.to_json5()

        return j
    
    def load(self, path: DataModelType) -> DataModelConfig:
        config = load(path)
        self.repr = config
        return config
    
    def is_path(self):
        return isinstance(self.repr, DataModelType)
    
    def is_embedded(self):
        from gedge.py_proto.data_model_config import DataModelConfig
        return isinstance(self.repr, DataModelConfig)
    
    def get_path(self) -> DataModelType | None:
        if self.is_path():
            return self.repr # type: ignore
        return self.repr.path # type: ignore

    def get_embedded(self) -> DataModelConfig | None:
        if not self.is_embedded():
            return None
        return self.repr # type: ignore
    
    def to_file_path(self) -> str:
        return self.repr.to_file_path()
    
    def to_model_path(self):
        if self.is_embedded():
            self.repr = DataModelType(self.repr.path, self.repr.version)


def load(path: DataModelType) -> DataModelConfig:
    directory = Singleton().get_model_dir()
    if not directory:
        raise LookupError(f"Trying to find model {path.path} but no --model-dir passed in")
    path_to_json = pathlib.Path(directory) / path.to_file_path()
    return load_from_file(str(path_to_json))

def load_from_file(path: str) -> DataModelConfig:
    from gedge.py_proto.data_model_config import DataModelConfig
    with open(path, "r") as f:
        j = json5.load(f)
    config = DataModelConfig.from_json5(j)
    return config
