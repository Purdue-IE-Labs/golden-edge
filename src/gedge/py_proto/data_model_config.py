from __future__ import annotations

from dataclasses import dataclass
import logging
import pathlib
from typing import Any, Self, TYPE_CHECKING

import json5

from gedge.py_proto.base_type import BaseType
from gedge.py_proto.data_model_object_config import DataModelObjectConfig, load_from_file
from gedge.py_proto.data_model_type import DataModelType, to_file_path
from gedge import proto
from gedge.py_proto.singleton import Singleton

if TYPE_CHECKING:
    from gedge.py_proto.data_object_config import DataObjectConfig
    from gedge.comm.comm import Comm

logger = logging.getLogger(__name__)

@dataclass
class DataModelItemConfig:
    path: str
    config: DataObjectConfig

    def to_proto(self) -> proto.DataModelItemConfig:
        return proto.DataModelItemConfig(path=self.path, config=self.config.to_proto())
    
    @classmethod
    def from_proto(cls, proto: proto.DataModelItemConfig) -> Self:
        from gedge.py_proto.data_object_config import DataObjectConfig
        path = proto.path
        config = DataObjectConfig.from_proto(proto.config)
        return cls(path, config)
    
    def to_json5(self) -> dict:
        j = {}
        j["path"] = self.path
        j.update(self.config.to_json5())
        return j
    
    @classmethod
    def from_json5(cls, json5: Any) -> Self:
        from gedge.py_proto.data_object_config import DataObjectConfig
        assert isinstance(json5, dict)
        path = json5["path"]
        config = DataObjectConfig.from_json5(json5)
        return cls(path, config)

@dataclass
class DataModelConfig:
    path: str
    parent: DataModelObjectConfig | None
    version: int
    items: list[DataModelItemConfig]

    def to_proto(self) -> proto.DataModelConfig:
        items = [i.to_proto() for i in self.items]
        parent = None
        if self.parent is not None:
            parent = self.parent.to_proto()
        return proto.DataModelConfig(path=self.path, parent=parent, version=self.version, items=items)

    @classmethod
    def from_proto(cls, proto: proto.DataModelConfig) -> Self:
        items = [DataModelItemConfig.from_proto(i) for i in proto.items]
        parent = None
        if proto.HasField("parent"):
            parent = DataModelObjectConfig.from_proto(proto.parent)
        return cls(proto.path, parent, proto.version, items)
    
    def to_json5(self) -> dict[str, Any]:
        j = {}
        j["model_path"] = self.path
        if self.parent is not None:
            j["parent"] = self.parent.to_json5()
        j["version"] = self.version
        j["tags"] = []
        for tag in self.items:
            j["tags"].append(tag.to_json5())

        return j
    
    def to_file(self, model_dir: str) -> bool:
        for tag in self.items:
            config = tag.config
            if config.is_base_type() or config.is_model_path():
                continue
            model = config.get_model_config()
            if not (model and model.to_file(model_dir) and config.to_model_path()):
                return False
        if self.parent is not None and self.parent.is_embedded():
            p = self.parent
            model = p.get_embedded()
            if not (model and model.to_file(model_dir)):
                logger.debug("could not write parent to file")
                return False
            p.to_model_path()
        j = self.to_json5()
        root_dir = pathlib.Path(model_dir)
        root_dir.mkdir(parents=True, exist_ok=True)
        here = root_dir / self.path
        here.mkdir(parents=True, exist_ok=True)
        here = here / f"v{self.version}.json5"
        with open(str(here), "w") as f:
            f.writelines(["/*\n", "THIS FILE IS AUTO-GENERATED\nDO NOT MOVE OR EDIT THIS FILE\n", "*/\n"])
            f.write(json5.dumps(j, indent=4))
        return True 
    
    def to_file_path(self) -> str:
        path = to_file_path(self.path, self.version)
        return path
    
    @classmethod
    def from_json5(cls, json5: Any) -> Self:
        assert isinstance(json5, dict)
        path = json5["model_path"]
        parent = None
        if json5.get("parent"):
            parent = DataModelObjectConfig.from_json5(json5["parent"])
        version = json5["version"]
        tags = []
        for tag in json5["tags"]:
            tags.append(DataModelItemConfig.from_json5(tag))
        
        return cls(path, parent, version, tags)
    
    def get_config_items(self) -> list[DataObjectConfig]:
        return [i.config for i in self.items]
    
    def add_parent_tags(self):
        if not self.parent:
            return
        model_dir = Singleton().get_model_dir()
        if not model_dir:
            raise LookupError(f"No model directory provided, needed to find parent of model {self.path}")
        path = pathlib.Path(model_dir) / self.parent.to_file_path()
        model = load_from_file(str(path))
        model.add_parent_tags()

        # where the inheritance happens
        for tag in model.items:
            self.items.append(tag)

        return
