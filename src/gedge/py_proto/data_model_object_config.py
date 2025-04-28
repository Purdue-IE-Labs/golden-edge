from __future__ import annotations

from dataclasses import dataclass
import os
import pathlib
import re
from typing import TYPE_CHECKING, Any, Self

import json5

from gedge.py_proto.data_model_type import DataModelType, to_file_path
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
        from gedge.py_proto.data_model_config import DataModelConfig
        if not isinstance(j, dict):
            raise ValueError(f"Invalid json for data model configuration, expected dict, found {j}")

        if not (("model_path" in j) ^ ("model" in j) ^ ("model_file" in j)):
            raise LookupError(f"Model object must set one and only one of ['model_path', 'model', 'model_file']")

        elif j.get("model_path"):
            config = DataModelType.from_json5(j["model_path"])
        elif j.get("model_file"):
            json5_dir = Singleton().get_json5_dir()
            if not json5_dir:
                raise ValueError("Passed path to model file without passing json-dir in which to look")
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
    try:
        p = path.to_file_path()
    except:
        p = file_path_latest_version(directory, path)
    path_to_json = pathlib.Path(directory) / p
    return load_from_file(str(path_to_json))

def load_from_file(path: str) -> DataModelConfig:
    from gedge.py_proto.data_model_config import DataModelConfig
    with open(path, "r") as f:
        j = json5.load(f)
    config = DataModelConfig.from_json5(j)
    return config

def file_path_latest_version(directory: str, path: DataModelType) -> str:
    dir = pathlib.Path(directory) / path.path
    version = find_latest_version(str(dir))
    return str(to_file_path(path.path, version))

def find_latest_version(dir: str) -> int:
    max_version = -1
    for f in os.listdir(dir):
        print(f)
        m = re.match(r'v(\d+).json5', f)
        if m:
            version = int(m.group(1))
            max_version = max(max_version, version)
    if max_version == -1:
        raise LookupError(f"No local version of model found in {dir}")
    return max_version