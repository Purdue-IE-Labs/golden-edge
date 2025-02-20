from gedge import proto
from typing import Any, Self
from gedge.edge.data_type import DataType
from gedge.edge.gtypes import TagValue
from gedge.edge.tag_data import TagData

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
        return Prop(type, value)
    
    @classmethod
    def from_value(cls, value: TagValue) -> Self:
        type = cls.intuit_type(value)
        value = TagData.from_value(value, type)
        return Prop(type, value)
    
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
    def from_proto(self, props: dict[str, proto.Prop]) -> Self:
        return Props({key:Prop.from_proto(value) for key, value in props.items()})
    
    @classmethod
    def from_value(self, props: dict[str, Any]) -> Self:
        return Props({key:Prop.from_value(value) for key, value in props.items()})
    
    def add_prop(self, key: str, value: Any):
        self.props[key] = Prop.from_value(value)
    
    def __repr__(self):
        return f"Props({self.props})"
    