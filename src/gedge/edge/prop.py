from gedge import proto
from typing import Any, Self

class Prop:
    def __init__(self, type: int, value: proto.TagData):
        self.type = type
        self.value = value
    
    def to_proto(self) -> proto.Prop:
        return proto.Prop(self.type, self.value) 
    
    @classmethod
    def from_proto(self, prop: proto.Prop) -> Self:
        type = prop.type
        value = prop.value
        return Prop(type, value)
    
    @classmethod
    def from_value(cls, value: Any) -> Self:
        type = cls.intuit_type(value)
        return Prop(type, value)
    
    @staticmethod
    def intuit_type(value: Any) -> int:
        if isinstance(value, str):
            return proto.DataType.STRING
        elif isinstance(value, int):
            return proto.DataType.INT
        elif isinstance(value, float):
            return proto.DataType.FLOAT
        elif isinstance(value, bool):
            return proto.DataType.BOOL
        else:
            raise ValueError(f"Illegal type for property. Allowed properties are str, int, float, bool. value is of type {type(value)}")


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
    