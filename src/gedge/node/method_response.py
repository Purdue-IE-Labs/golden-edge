from __future__ import annotations
from dataclasses import dataclass

from gedge.node.body import BodyConfig
from gedge.py_proto.props import Props
from gedge import proto
from typing import Any, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from gedge.node.gtypes import Type

# CONFIG object
@dataclass
class MethodResponseConfig:
    code: int
    props: Props
    body: BodyConfig
    
    def to_proto(self) -> proto.MethodResponseConfig:
        props = self.props.to_proto()
        body = self.body.to_proto()
        return proto.MethodResponseConfig(code=self.code, props=props, body=body)

    @classmethod
    def from_proto(cls, proto: proto.MethodResponseConfig) -> Self:
        props = Props.from_proto(proto.props)
        body = BodyConfig.from_proto(proto.body)
        return cls(proto.code, props, body)
    
    @classmethod
    def from_json5(cls, j: Any) -> Self:
        if isinstance(j, int):
            return cls(j, Props.empty(), BodyConfig.empty()) 
        if not isinstance(j, dict):
            raise ValueError(f"Invalid method repsonse type, {j}")
        
        if "code" not in j:
            raise LookupError(f"Method response must include code, {j}")
        code = int(j["code"])

        props = Props.from_json5(j.get("props", {}))
        body = BodyConfig.from_json5(j.get("body", {}))
        return cls(code, props, body)
    
    def add_prop(self, key: str, value: Any):
        self.props.add_prop(key, value)
    