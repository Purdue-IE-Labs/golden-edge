from __future__ import annotations
from dataclasses import dataclass

from gedge.node.body import BodyConfig
from gedge.node.data_type import DataType
from gedge.node.param import Param
from gedge.py_proto.props import Props
from gedge import proto
from gedge.node.method_response import MethodResponse

from typing import Any, Self, TYPE_CHECKING
if TYPE_CHECKING:
    from gedge.node.gtypes import TagBaseValue, Type, MethodHandler

@dataclass
class Method:
    path: str
    handler: MethodHandler | None
    props: Props
    params: dict[str, Param]
    responses: list[MethodResponse]

    def to_proto(self) -> proto.Method:
        params = {key:value.to_proto() for key, value in self.params.items()}
        responses = [r.to_proto() for r in self.responses]
        props = self.props.to_proto()
        return proto.Method(path=self.path, props=props, params=params, responses=responses)

    @classmethod
    def from_proto(cls, proto: proto.Method) -> Self:
        props = Props.from_proto(proto.props)
        params = {key:Param.from_proto(value) for key, value in proto.params.items()}
        responses = [MethodResponse.from_proto(r) for r in proto.responses]
        return cls(proto.path, None, props, params, responses)
    
    @classmethod
    def from_json5(cls, json: Any) -> Self:
        if not isinstance(json, dict):
            raise ValueError(f"Invalid method {json}")
        
        if "path" not in json:
            raise LookupError(f"Method must have path, {json}")
        path = json["path"]
        props = Props.from_json5(json.get("props", {}))

        params = {}
        if "params" in json and isinstance(json["params"], dict):
            params = {key:Param.from_json5(value) for key, value in json["params"].items()}
        
        responses = []
        if "responses" in json:
            for response in json["responses"]:
                r = MethodResponse.from_json5(response)
                responses.append(r)

        return cls(path, None, props, params, responses)

    def add_response(self, code: int, props: dict[str, TagValue] = {}, body: dict[str, Body] = {}): 
        props_ = Props.from_value(props)
        body_ = body
        response = MethodResponse(code, props_, body_)
        self.responses.append(response)
        return response
