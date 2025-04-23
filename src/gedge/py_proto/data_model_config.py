from __future__ import annotations

from dataclasses import dataclass
import pathlib
from typing import Any, Self, TYPE_CHECKING

import json5

from gedge.py_proto.base_type import BaseType
from gedge.py_proto.data_model_type import DataModelType
from gedge import proto

if TYPE_CHECKING:
    from gedge.py_proto.data_object_config import DataObjectConfig
    from gedge.comm.comm import Comm

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
        if not self.config.props.is_empty():
            j["props"] = self.config.props.to_json5()
        # TODO: this is gross lol, config.config.config
        # However, it allows for the flatter structure of the json5 
        # while the protobuf has more of a layered structure for 
        # reusability
        c = self.config.config.config
        if self.config.is_base_type():
            j["base_type"] = c.to_json5()
        elif self.config.is_model_path():
            # we do not pull the model here
            path = self.config.get_model_path()
            if not path:
                raise Exception
            j["model_path"] = c.to_json5()
        else:
            j["model"] = c.to_json5()
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
    type: DataModelType
    extends_path: str | None
    version: int
    items: list[DataModelItemConfig]

    @property
    def path(self):
        return self.type.path

    def to_proto(self) -> proto.DataModelConfig:
        items = [i.to_proto() for i in self.items]
        return proto.DataModelConfig(type=self.type.to_proto(), extends_path=self.extends_path, version=self.version, items=items)

    @classmethod
    def from_proto(cls, proto: proto.DataModelConfig) -> Self:
        type_ = DataModelType.from_proto(proto.type)
        items = [DataModelItemConfig.from_proto(i) for i in proto.items]
        return cls(type_, proto.extends_path, proto.version, items)
    
    def to_json5(self) -> dict[str, Any]:
        j = {}
        j["model_path"] = self.type.path
        if self.extends_path:
            j["extends_path"] = self.extends_path
        j["version"] = self.version
        j["tags"] = []
        for tag in self.items:
            j["tags"].append(tag.to_json5())

        return j
    
    def to_file(self, model_dir: str, comm: Comm) -> bool:
        for tag in self.items:
            config = tag.config
            if config.is_base_type():
                continue
            if config.is_model_path():
                if not config.fetch(comm):
                    return False
            model = config.get_model_config()
            if not (model and model.to_file(model_dir, comm) and config.to_model_path()):
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
    
    @classmethod
    def from_json5(cls, json5: Any) -> Self:
        assert isinstance(json5, dict)
        path = DataModelType(json5["model_path"])
        extends_path = json5.get("extends_path", None)
        version = json5["version"]
        tags = []
        for tag in json5["tags"]:
            tags.append(DataModelItemConfig.from_json5(tag))
        
        return cls(path, extends_path, version, tags)
    
    def fetch(self, comm: Comm, recurse: bool = True) -> bool:
        '''
        Embed all models by fetching from path
        '''

        res = True
        for item in self.items:
            c = item.config.config.config
            if isinstance(c, BaseType):
                continue
            if isinstance(c.repr, DataModelType):
                path = c.repr.path
                model = comm.pull_model(path)
                if not model:
                    return False
                c.repr = model
            elif isinstance(c.repr, DataModelConfig):
                res = res and c.repr.fetch(comm, recurse)
        return True
    
    def get_config_items(self) -> list[DataObjectConfig]:
        return [i.config for i in self.items]

