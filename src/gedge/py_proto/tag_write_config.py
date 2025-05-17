

from dataclasses import dataclass
from typing import Any

from gedge import proto
from gedge.node.method_response import ResponseConfig
from gedge.py_proto.conversions import list_from_proto, list_to_proto


@dataclass
class TagWriteConfig:
    path: str
    responses: list[ResponseConfig]

    def to_proto(self) -> proto.TagWriteConfig:
        return proto.TagWriteConfig(path=self.path, responses=list_to_proto(self.responses))
    
    @classmethod
    def from_proto(cls, proto: proto.TagWriteConfig):
        responses = list_from_proto(ResponseConfig, proto.responses)
        return cls(proto.path, responses)