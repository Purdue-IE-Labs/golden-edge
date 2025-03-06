from __future__ import annotations

from gedge import proto
from gedge.node.data_type import DataType
from gedge.node.tag_data import TagData

from typing import Any, Self, TYPE_CHECKING
if TYPE_CHECKING:
    from gedge.node.gtypes import TagValue

class Prop:
    def __init__(self, type: DataType, value: TagData):
        self.type = type
        self.value = value
    
    def to_proto(self) -> proto.Prop:
        return proto.Prop(type=self.type.to_proto(), value=self.value.to_proto()) 
    
    @classmethod
    def from_proto(cls, prop: proto.Prop) -> Self:
        type = DataType.from_proto(prop.type)
        value = TagData.from_proto(prop.value, type)
        return cls(type, value)
    
    @classmethod
    def from_value(cls, value: TagValue) -> Self:
        type_ = cls.intuit_type(value)
        value_ = TagData.from_value(value, type_)
        return cls(type_, value_)
    
    @staticmethod
    def intuit_type(value: Any) -> DataType:
        if isinstance(value, str):
            return DataType.STRING
        elif isinstance(value, int):
            return DataType.INT
        elif isinstance(value, float):
            return DataType.FLOAT
        elif isinstance(value, bool):
            return DataType.BOOL
        else:
            raise ValueError(f"Illegal type for property. Allowed properties are str, int, float, bool. value is of type {type(value)}")
    
    def __repr__(self):
        return f"{self.value}"


class Props:
    def __init__(self, props: dict[str, Prop]):
        self.props = props
    
    def to_proto(self) -> dict[str, proto.Prop]:
        return {key:value.to_proto() for key, value in self.props.items()}
    
    @classmethod
    def from_proto(cls, props: dict[str, proto.Prop]) -> Self:
        return cls({key:Prop.from_proto(value) for key, value in props.items()})
    
    @classmethod
    def from_value(cls, props: dict[str, Any]) -> Self:
        return cls({key:Prop.from_value(value) for key, value in props.items()})
    
    @classmethod
    def from_json5(cls, props: Any) -> Self:
        if not isinstance(props, dict):
            raise ValueError(f"invalid props {props}")
        return cls.from_value(props)
    
    @classmethod
    def empty(cls) -> Self:
        return cls({})
    
    def add_prop(self, key: str, value: Any):
        self.props[key] = Prop.from_value(value)
    
    def __repr__(self):
        return f"Props({self.props})"
    