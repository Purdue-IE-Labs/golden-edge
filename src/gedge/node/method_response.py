from __future__ import annotations
from dataclasses import dataclass

from gedge.node.body import Body
from gedge.node.data_type import DataType
from gedge.node.prop import Props
from gedge import proto
from typing import Any, Self, TYPE_CHECKING

if TYPE_CHECKING: # pragma: no cover
    from gedge.node.gtypes import Type

# CONFIG object
@dataclass
class MethodResponse:
    code: int
    props: Props
    body: dict[str, Body]
    
    def to_proto(self) -> proto.Response:
        props = self.props.to_proto()
        body = {key:value.to_proto() for key, value in self.body.items()}
        return proto.Response(code=self.code, props=props, body=body)

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
            raise ValueError(f"Invalid method response type, {json}")
        
        if "code" not in json:
            raise LookupError(f"Method response must include code, {json}")
        
        try:
            code = int(json["code"])
        except:
            raise ValueError(f"The passed code cannot be converted to an integer: {json["code"]}")


        try:
            body = {key:Body.from_json5(value) for key, value in json.get("body", {}).items()}
        except:
            raise ValueError(f"The passed body is not a dict object: {json.get("body", {})}")
        
        props = Props.from_json5(json.get("props", {}))
        
        return cls(code, props, body)
    
    def add_prop(self, key: str, value: Any):
        self.props.add_prop(key, value)
    