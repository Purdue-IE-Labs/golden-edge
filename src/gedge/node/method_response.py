from __future__ import annotations
from dataclasses import dataclass

from gedge.node.body import BodyConfig
from gedge.node.data_type import DataType
from gedge.py_proto.props import Props
from gedge import proto
from typing import Any, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from gedge.node.gtypes import Type

# CONFIG object
@dataclass
class MethodResponse:
    code: int
    props: Props
    body: BodyConfig
    
    def to_proto(self) -> proto.MethodResponseConfig:
        props = self.props.to_proto()
        # body = {key:value.to_proto() for key, value in self.body.items()}
        body = self.body.to_proto()
        return proto.MethodResponseConfig(code=self.code, props=props, body=body)

    @classmethod
    def from_proto(cls, proto: proto.Response) -> Self:
        props = Props.from_proto(proto.props)
        body = {key:Body.from_proto(value) for key, value in proto.body.items()}
        return cls(proto.code, props, body)
    
    @classmethod
    def from_json5(cls, json: Any) -> Self:
        if isinstance(json, int):
            return cls(json, Props.empty(), {}) 
        if not isinstance(json, dict):
            raise ValueError(f"Invalid method repsonse type, {json}")
        
        if "code" not in json:
            raise LookupError(f"Method response must include code, {json}")
        code = int(json["code"])

        props = Props.from_json5(json.get("props", {}))
        body = {key:Body.from_json5(value) for key, value in json.get("body", {}).items()}
        return cls(code, props, body)
    
    def add_prop(self, key: str, value: Any):
        self.props.add_prop(key, value)
    