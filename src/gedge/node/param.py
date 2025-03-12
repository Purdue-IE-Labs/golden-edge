from dataclasses import dataclass
from multiprocessing import Value
from typing import Any, Self

from gedge.node.data_type import DataType
from gedge.node.prop import Props
from gedge import proto

@dataclass
class Param:
    type: DataType
    props: Props

    def to_proto(self):
        type = self.type.to_proto()
        props = self.props.to_proto()
        return proto.Param(type=type, props=props)
    
    @classmethod
    def from_proto(cls, proto: proto.Param) -> Self:
        type = DataType.from_proto(proto.type)
        props = Props.from_proto(proto.props)
        return cls(type, props)
    
    @classmethod
    def from_json5(cls, param: Any) -> Self:
        if not isinstance(param, dict):
            raise ValueError(f"invalid param {param}")
        
        if "type" not in param:
            raise ValueError(f"param {param} must have type")
        type = DataType.from_json5(param["type"])
        props = Props.from_json5(param.get("props", {}))
        return cls(type, props)
