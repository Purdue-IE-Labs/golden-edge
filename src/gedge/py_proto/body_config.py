from __future__ import annotations

from dataclasses import dataclass

from gedge.py_proto.data_object_config import DataObjectConfig
from gedge.node.data_type import DataType
from gedge.py_proto.props import Props
from gedge import proto

from typing import Any, Self, TYPE_CHECKING
if TYPE_CHECKING:
    from gedge.node.gtypes import TagBaseValue

@dataclass
class BodyConfig:
    body: dict[str, DataObjectConfig]

    def to_proto(self):
        body_proto = {key:value.to_proto() for key, value in self.body.items()}
        return proto.BodyConfig(body=body_proto)
    
    @classmethod
    def from_proto(cls, proto: proto.BodyConfig) -> Self:
        body = {key:DataObjectConfig.from_proto(value) for key, value in proto.body.items()}
        return cls(body)
    
    @classmethod
    def from_json5(cls, json: Any) -> Self:
        if not isinstance(json, dict):
            raise ValueError
        body = {}
        for key, value in json.items():
            body[key] = DataObjectConfig.from_json5(value)
        return cls(body)

# @dataclass
# class BodyData:
#     value: TagValue
#     props: dict[str, TagValue]
