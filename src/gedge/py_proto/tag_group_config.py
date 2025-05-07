from dataclasses import dataclass
from typing import Any

from gedge import proto
from gedge.node.gtypes import GroupWriteHandler, TagBaseValue
from gedge.node.method_response import ResponseConfig
from gedge.py_proto.base_data import BaseData
from gedge.py_proto.conversions import list_from_json5, list_from_proto, list_to_proto
from gedge.py_proto.data_model_config import DataItemConfig
from gedge.py_proto.tag_config import TagConfig

@dataclass
class TagGroupConfig:
    path: str # path of the group! group_path, if you will
    items: dict[str, DataItemConfig] # maps the tag path to the config for that path, which is not the same as config.path
    writable: bool
    responses: list[ResponseConfig]
    handler: GroupWriteHandler | None

    def to_proto(self) -> proto.TagGroupConfig:
        path = self.path
        items = list(self.items)
        writable = self.writable
        responses = list_to_proto(self.responses)
        return proto.TagGroupConfig(path=path, items=items, writable=writable, responses=responses)
    
    @classmethod
    def from_proto(cls, proto: proto.TagGroupConfig, tag_config: TagConfig):
        path = proto.path
        items = list(proto.items)
        dict_items = {}
        for i in items:
            dict_items[i] = tag_config.get_config(i)
        writable = proto.writable
        responses = list_from_proto(ResponseConfig, proto.responses)
        return cls(path, dict_items, writable, responses, None)
    
    @classmethod
    def from_json5(cls, j: Any):
        if not isinstance(j, dict):
            raise ValueError(f"Tag group configuration must be a dict, found {j}")
        path = j["group_path"]
        items = j["tag_paths"]

        if "writable" in j:
            writable = bool(j["writable"])
        else:
            writable = True if len(j.get("responses", [])) > 0 else False
        
        responses = []
        if writable:
            responses = list_from_json5(ResponseConfig, j.get("responses", []))

        return cls(path, items, writable, responses, None)
    
    def convert_proto_to_py(self, proto: proto.TagGroup) -> dict[str, TagBaseValue]:
        data = dict(proto.data)
        for k, v in data.items():
            c = self.items[k]
            base_type = c.get_base_type()
            if not base_type:
                raise ValueError
            BaseData.proto_to_py(v, base_type)
    
    def convert_py_to_proto(self, value: dict[str, TagBaseValue]) -> proto.TagGroup:
        pass