from __future__ import annotations

from dataclasses import dataclass
from gedge.node.data_type import DataType
from gedge.py_proto.data_object_config import DataObjectConfig
from gedge.py_proto.props import Props
from gedge import proto

from typing import Any, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from gedge.node.gtypes import TagBaseValue

@dataclass
class ParamsConfig:
    params: dict[str, DataObjectConfig]

    def to_proto(self):
        body_proto = {key:value.to_proto() for key, value in self.params.items()}
        return proto.BodyConfig(body=body_proto)
    
    @classmethod
    def from_proto(cls, proto: proto.ParamsConfig) -> Self:
        body = {key:DataObjectConfig.from_proto(value) for key, value in proto.params.items()}
        return cls(body)
    
    @classmethod
    def from_json5(cls, json: Any) -> Self:
        if not isinstance(json, dict):
            raise ValueError
        params = {}
        for key, value in json.items():
            params[key] = DataObjectConfig.from_json5(value)
        return cls(params)


@dataclass
class ParamData:
    value: TagBaseValue
    props: dict[str, TagBaseValue]


# def params_proto_to_py(proto: dict[str, proto.DataObject], params_config: dict[str, Param]) -> dict[str, Any]:
#     params: dict[str, Any] = {}
#     for key, value in proto.items():
#         data_type = params_config[key].type
#         params[key] = TagData.proto_to_py(value, data_type)
#     return params