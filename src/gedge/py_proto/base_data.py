from __future__ import annotations

from gedge import proto
from typing import Any, Self, TYPE_CHECKING

from gedge.py_proto.base_type import BaseType
from gedge.py_proto.props import Prop

if TYPE_CHECKING:
    from gedge.node.gtypes import TagBaseValue

class BaseData:
    def __init__(self, proto_: proto.BaseData, type: BaseType):
        self.type = type
        self.proto = proto_
        self.value = self.proto_to_py(self.proto, self.type)
    
    def to_proto(self) -> proto.BaseData:
        return self.proto
        
    def to_py(self) -> TagBaseValue:
        return self.value
    
    @classmethod
    def from_proto(cls, proto: proto.BaseData, type: BaseType) -> Self:
        return cls(proto, type)
    
    @classmethod
    def from_value(cls, value: TagBaseValue, type: BaseType) -> Self:
        proto = cls.py_to_proto(value, type)
        return cls(proto, type)
    
    @classmethod
    def from_json5(cls, json5: Any) -> Self:
        base_type = Prop.intuit_type(json5)
        return cls.from_value(json5, base_type)

    @classmethod
    def py_to_proto(cls, value: TagBaseValue, type: BaseType) -> proto.BaseData:
        data = proto.BaseData()
        match type:
            case BaseType.INT:
                data.int_data = int(value)
            case BaseType.LONG:
                data.long_data = int(value)
            case BaseType.FLOAT:
                data.float_data = float(value)
            case BaseType.STRING:
                data.string_data = str(value)
            case BaseType.BOOL:
                data.bool_data = bool(value)
            case BaseType.LIST_INT:
                data.list_int_data.list.extend(list([int(x) for x in value]))
            case BaseType.LIST_LONG:
                data.list_long_data.list.extend(list([int(x) for x in value]))
            case BaseType.LIST_FLOAT:
                data.list_float_data.list.extend(list([float(x) for x in value]))
            case BaseType.LIST_STRING:
                data.list_string_data.list.extend(list([str(x) for x in value]))
            case BaseType.LIST_BOOL:
                data.list_bool_data.list.extend(list([bool(x) for x in value]))
            case _:
                raise ValueError(f"Unknown tag type {type}")
        return data

    @classmethod
    def proto_to_py(cls, value: proto.BaseData, type: BaseType) -> TagBaseValue:
        tag_data = value
        match type:
            case BaseType.INT:
                return int(tag_data.int_data)
            case BaseType.LONG:
                return int(tag_data.long_data)
            case BaseType.FLOAT:
                return float(tag_data.float_data)
            case BaseType.STRING:
                return str(tag_data.string_data)
            case BaseType.BOOL:
                return bool(tag_data.bool_data)
            case BaseType.LIST_INT:
                return list(tag_data.list_int_data.list)
            case BaseType.LIST_LONG:
                return list(tag_data.list_long_data.list)
            case BaseType.LIST_FLOAT:
                return list(tag_data.list_float_data.list)
            case BaseType.LIST_STRING:
                return list(tag_data.list_string_data.list)
            case BaseType.LIST_BOOL:
                return list(tag_data.list_bool_data.list)
        raise ValueError(f"Cannot convert tag to type {type}")
    
    def __repr__(self) -> str:
        return f"BaseData('{self.value}')"
