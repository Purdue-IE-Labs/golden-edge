from __future__ import annotations
from dataclasses import dataclass

from gedge.py_proto.data_model_config import DataItemConfig
from gedge.py_proto.props import Prop
from gedge import proto

from typing import Any, Self, TYPE_CHECKING

from gedge.py_proto.conversions import list_from_json5, list_from_proto, list_to_proto
if TYPE_CHECKING:
    from gedge.node.gtypes import MethodHandler
    from gedge.node.method_response import ResponseConfig

@dataclass
class MethodConfig:
    path: str
    params: list[DataItemConfig]
    responses: list[ResponseConfig]
    props: list[Prop]
    handler: MethodHandler | None

    def to_proto(self) -> proto.MethodConfig:
        params = list_to_proto(self.params)
        responses = list_to_proto(self.responses)
        props = list_to_proto(self.props)
        return proto.MethodConfig(path=self.path, props=props, params=params, responses=responses)

    @classmethod
    def from_proto(cls, proto: proto.MethodConfig) -> Self:
        from gedge.node.method_response import ResponseConfig
        props = list_from_proto(Prop, proto.props)
        params = list_from_proto(DataItemConfig, proto.params)
        responses = list_from_proto(ResponseConfig, proto.responses)
        return cls(proto.path, params, responses, props, None)
    
    @classmethod
    def from_json5(cls, j: Any) -> Self:
        from gedge.node.method_response import ResponseConfig
        if not isinstance(j, dict):
            raise ValueError(f"Invalid method config {j}")
        if "path" not in j:
            raise LookupError(f"Method must have path, {j}")
        path = j["path"]
        props = []
        for k, v in j.get("props", {}).items():
            props.append(Prop.from_json5(k, v))
        params = list_from_json5(DataItemConfig, j.get("params", []))
        responses = list_from_json5(ResponseConfig, j.get("responses", []))

        return cls(path, params, responses, props, None)
