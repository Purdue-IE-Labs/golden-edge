from __future__ import annotations

from gedge.node.data_type import DataType
from gedge.node.prop import Props
from gedge import proto
from typing import Any, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from gedge.node.gtypes import Type

# CONFIG object
class MethodResponse:
    def __init__(self, code: int, props: Props, body: dict[str, DataType]):
        self.code = code
        self.props = props
        self.body = body
    
    def to_proto(self) -> proto.Response:
        props = self.props.to_proto()
        body = {key:value.to_proto() for key, value in self.body.items()}
        return proto.Response(code=self.code, props=props, body=body)

    @classmethod
    def from_proto(cls, proto: proto.Response) -> Self:
        props = Props.from_proto(proto.props)
        body = {key:DataType.from_proto(value) for key, value in proto.body.items()}
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
        body = {key:DataType.from_json5(value) for key, value in json.get("body", {}).items()}
        return cls(code, props, body)
    
    def add_prop(self, key: str, value: Any):
        self.props.add_prop(key, value)
    
    def add_body(self, **kwargs: Type):
        for key, value in kwargs.items():
            self.body[key] = DataType.from_type(value)
    
    def __repr__(self):
        return f"Response(code={self.code}, body={self.body})"
    