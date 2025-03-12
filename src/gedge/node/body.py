from dataclasses import dataclass
from multiprocessing import Value
from typing import Any, Self

from gedge.node.data_type import DataType
from gedge.node.gtypes import TagValue
from gedge.node.prop import Props
from gedge import proto

@dataclass
class Body:
    type: DataType
    props: Props

    def to_proto(self):
        type = self.type.to_proto()
        props = self.props.to_proto()
        return proto.Body(type=type, props=props)
    
    @classmethod
    def from_proto(cls, proto: proto.Body) -> Self:
        type = DataType.from_proto(proto.type)
        props = Props.from_proto(proto.props)
        return cls(type, props)
    
    @classmethod
    def from_json5(cls, body: Any) -> Self:
        if not isinstance(body, dict):
            raise ValueError(f"invalid body {body}")
        
        if "type" not in body:
            raise ValueError(f"body {body} must have type")
        type = DataType.from_json5(body["type"])
        props = Props.from_json5(body.get("props", {}))
        return cls(type, props)

@dataclass
class BodyData:
    value: TagValue
    props: dict[str, TagValue]
