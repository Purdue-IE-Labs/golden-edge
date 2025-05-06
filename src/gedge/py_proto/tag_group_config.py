from dataclasses import dataclass
from typing import Any

from gedge import proto

@dataclass
class TagGroupConfig:
    path: str
    items: list[str]

    def to_proto(self) -> proto.TagGroupConfig:
        print(self.path, self.items)
        return proto.TagGroupConfig(path=self.path, items=list(self.items))
    
    @classmethod
    def from_proto(cls, proto: proto.TagGroupConfig):
        return cls(proto.path, list(proto.items))
    
    @classmethod
    def from_json5(cls, j: Any):
        if not isinstance(j, dict):
            raise ValueError(f"Tag group configuration must be a dict, found {j}")
        path = j["group_path"]
        items = j["tag_paths"]
        return cls(path, items)