from __future__ import annotations
from dataclasses import dataclass

from gedge.py_proto.params_config import ParamsConfig
from gedge.py_proto.props import Props
from gedge import proto
from gedge.node.method_response import MethodResponseConfig

from typing import Any, Self, TYPE_CHECKING
if TYPE_CHECKING:
    from gedge.node.gtypes import TagBaseValue, Type, MethodHandler

@dataclass
class MethodConfig:
    path: str
    handler: MethodHandler | None
    props: Props
    params: ParamsConfig
    responses: list[MethodResponseConfig]

    def to_proto(self) -> proto.MethodConfig:
        params = self.params.to_proto()
        responses = [r.to_proto() for r in self.responses]
        props = self.props.to_proto()
        return proto.MethodConfig(path=self.path, props=props, params=params, responses=responses)

    @classmethod
    def from_proto(cls, proto: proto.MethodConfig) -> Self:
        props = Props.from_proto(proto.props)
        params = ParamsConfig.from_proto(proto.params)
        responses = [MethodResponseConfig.from_proto(r) for r in proto.responses]
        return cls(proto.path, None, props, params, responses)
    
    @classmethod
    def from_json5(cls, j: Any) -> Self:
        if not isinstance(j, dict):
            raise ValueError(f"Invalid method {j}")
        
        if "path" not in j:
            raise LookupError(f"Method must have path, {j}")
        path = j["path"]
        props = Props.from_json5(j)

        params = ParamsConfig.empty()
        if "params" in j and isinstance(j["params"], dict):
            params = ParamsConfig.from_json5(j["params"])
        
        responses = []
        if "responses" in j:
            for response in j["responses"]:
                r = MethodResponseConfig.from_json5(response)
                responses.append(r)

        return cls(path, None, props, params, responses)
