from __future__ import annotations

from dataclasses import dataclass
import logging
import pathlib
from typing import Any, Self, TYPE_CHECKING

import json5

from gedge.py_proto.base_type import BaseType
from gedge.py_proto.data_model_ref import DataModelRef
from gedge.py_proto.load_models import load, to_file_path
from gedge import proto
from gedge.py_proto.singleton import Singleton
from gedge.py_proto.type import Type

if TYPE_CHECKING:
    from gedge.py_proto.props import Prop

logger = logging.getLogger(__name__)

@dataclass
class DataItemConfig:
    path: str
    type: Type
    props: list[Prop]

    def to_proto(self) -> proto.DataItemConfig:
        props = [p.to_proto() for p in self.props]
        return proto.DataItemConfig(path=self.path, type=self.type.to_proto(), props=props)
    
    @classmethod
    def from_proto(cls, proto: proto.DataItemConfig) -> Self:
        from gedge.py_proto.props import Prop
        path = proto.path
        type = Type.from_proto(proto.type)
        props = [Prop.from_proto(p) for p in proto.props]
        return cls(path, type, props)
    
    def to_json5(self) -> dict:
        j = {}
        j["path"] = self.path
        j.update(self.type.to_json5())
        for p in self.props:
            j.update(p.to_json5())
        return j
    
    @classmethod
    def from_json5(cls, j: Any) -> Self:
        from gedge.py_proto.props import Prop
        if not isinstance(j, dict):
            raise ValueError(f"Data Item Config must be of type dictionary, found {j}")

        if "path" not in j:
            raise LookupError(f"Every tag must have a path! Tag provided with no keyword 'path': {j}")
        path = j["path"]
        type = Type.from_json5(j)
        props = [Prop.from_json5(key, p) for key, p in j.get("props", {}).items()]
        return cls(path, type, props)
    
    def is_base_type(self) -> bool:
        return self.type.is_base_type()
    
    def get_base_type(self) -> BaseType | None:
        return self.type.get_base_type()
    
    def is_model_ref(self) -> bool:
        return self.type.is_model_ref()
    
    def get_model_ref(self) -> DataModelRef | None:
        return self.type.get_model_ref()
    
    def load_model(self) -> DataModelConfig | None:
        return self.type.load_model()

# def to_dict_value(l: list[DataItemConfig]) -> dict[str, TagValue]:
#     return {i.path: i.to_value() for i in l}

@dataclass
class DataModelConfig:
    path: str
    parent: DataModelRef | None
    version: int
    items: list[DataItemConfig]

    @property
    def full_path(self):
        return DataModelRef(self.path, self.version).full_path

    def to_proto(self) -> proto.DataModelConfig:
        items = [i.to_proto() for i in self.items]
        parent = None
        if self.parent is not None:
            parent = self.parent.to_proto()
        return proto.DataModelConfig(path=self.path, parent=parent, version=self.version, items=items)

    @classmethod
    def from_proto(cls, proto: proto.DataModelConfig) -> Self:
        items = [DataItemConfig.from_proto(i) for i in proto.items]
        parent = None
        if proto.HasField("parent"):
            parent = DataModelRef.from_proto(proto.parent)
        return cls(proto.path, parent, proto.version, items)
    
    def to_json5(self) -> dict[str, Any]:
        j = {}
        j["path"] = self.path
        if self.parent is not None:
            j["parent"] = self.parent.to_json5()
        j["version"] = self.version
        j["tags"] = []
        for tag in self.items:
            j["tags"].append(tag.to_json5())

        return j
    
    def to_file(self, model_dir: str) -> bool:
        for tag in self.items:
            config = tag.type
            if config.is_base_type():
                continue
            model = config.load_model()
            if not (model and model.to_file(model_dir)):
                return False
        if self.parent is not None:
            p = self.parent
            model = p.load_model()
            if not (model and model.to_file(model_dir)):
                logger.debug("could not write parent to file")
                return False
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
    def from_json5(cls, j: Any) -> Self:
        if not isinstance(j, dict):
            raise ValueError(f"Expected model config to be dict, found {j}")
        if "path" not in j:
            raise LookupError(f"Model config must include keyword 'path', found {j}")
        if "version" not in j:
            raise LookupError(f"Model config must include version, found {j}")

        path = j["path"]
        parent = None
        if j.get("parent"):
            parent = DataModelRef.from_json5(j["parent"])
        version = j["version"]
        tags = []
        for tag in j.get("tags", []):
            tags.append(DataItemConfig.from_json5(tag))
        
        return cls(path, parent, version, tags)
    
    def add_parent_tags(self):
        if not self.parent:
            return
        model = load(self.parent)
        model.add_parent_tags()

        # where the inheritance happens
        for tag in model.items:
            self.items.append(tag)

        return
