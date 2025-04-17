from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Self, TYPE_CHECKING

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
        j["props"] = self.config.props.to_json5()
        # TODO: this is gross lol, config.config.config
        # However, it allows for the flatter structure of the json5 
        # while the protobuf has more of a layered structure for 
        # reusability
        c = self.config.config.config
        if isinstance(c, BaseType):
            j["base_type"] = c.to_json5()
        elif isinstance(c.repr, DataModelType):
            j["model_path"] = c.to_json5()
        else:
            j["model"] = c.to_json5()
        return j
    
    @classmethod
    def from_json5(cls, json5: Any) -> Self:
        from gedge.py_proto.data_object_config import DataObjectConfig
        from gedge.py_proto.config import Config
        from gedge.py_proto.props import Props
        assert isinstance(json5, dict)
        path = json5["path"]
        props = Props.from_json5(json5["props"])
        if not (("base_type" in json5) ^ ("model_path" in json5) ^ ("model" in json5)):
            raise ValueError
        if json5.get("base_type"):
            config = Config.from_json5(json5["base_type"], True)
        elif json5.get("model_path"):
            config = Config.from_json5(json5["model_path"], False)
        else:
            config = Config.from_json5(json5["model"], False)
        config = DataObjectConfig(config, props)
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
    
    def to_json5(self) -> dict:
        j = {}
        j["model_path"] = self.type.path
        if self.extends_path:
            j["extends_path"] = self.extends_path
        j["version"] = self.version
        j["tags"] = []
        for tag in self.items:
            j["tags"].append(tag.to_json5())

        return j
    
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
    
    def fetch(self, comm: Comm, recurse: bool = True):
        '''
        Embed all models by fetching from path
        '''

        for item in self.items:
            c = item.config.config.config
            if isinstance(c, BaseType):
                continue
            if isinstance(c.repr, DataModelType):
                path = c.repr.path
                c.repr = comm.pull_model(path)
            elif isinstance(c.repr, DataModelConfig):
                c.repr.fetch(comm, recurse)
