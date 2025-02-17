from gedge import proto
from gedge.edge.data_type import DataType
from typing import Any, Self

from gedge.edge.types import Type

class TagData:
    def __init__(self, type: int, value: proto.TagData):
        self.type = DataType(type)
        self.value: proto.TagData = value
    
    def to_proto(self) -> proto.TagData:
        return self.value
    
    @classmethod
    def from_proto(cls, proto: proto.TagData, type: Type) -> Self:
        value = from_tag_data(proto, type)
        return TagData(type, value)
    
    @classmethod
    def from_value(cls, value: Any, type: Type) -> Self:
        type: DataType = DataType(type)
        value = convert(value, type.type)
        return TagData(type, value)


def from_tag_data(tag_data: proto.TagData, type: int) -> Any:
    match type:
        case proto.DataType.INT:
            return int(tag_data.int_data)
        case proto.DataType.LONG:
            return int(tag_data.long_data)
        case proto.DataType.FLOAT:
            return float(tag_data.float_data)
        case proto.DataType.STRING:
            return str(tag_data.string_data)
        case proto.DataType.BOOL:
            return bool(tag_data.bool_data)
        case proto.DataType.LIST_INT:
            return list(tag_data.list_int_data.list)
        case proto.DataType.LIST_LONG:
            return list(tag_data.list_long_data.list)
        case proto.DataType.LIST_FLOAT:
            return list(tag_data.list_float_data.list)
        case proto.DataType.LIST_STRING:
            return list(tag_data.list_string_data.list)
        case proto.DataType.LIST_BOOL:
            return list(tag_data.list_bool_data.list)
    raise ValueError(f"Cannot convert tag to type {type}")

def convert_type(type: Any) -> proto.DataType:
    """
    Note: Python does not support the notion of a "long" data type.
    In fact, there are several data types that may be supported 
    in our protocol that are not recognized in Python
    Thus, users can also pass in a DataType object directly, which 
    has all the types allowed by our protocol. As an API convenience,
    we allow the user to use built-in Python types.
    """
    if type == int:
        return proto.DataType.INT
    elif type == float:
        return proto.DataType.FLOAT
    elif type == str:
        return proto.DataType.STRING
    elif type == bool:
        return proto.DataType.BOOL
    elif type == list[int]:
        return proto.DataType.LIST_INT
    elif type == list[float]:
        return proto.DataType.LIST_FLOAT
    elif type == list[str]:
        return proto.DataType.LIST_STRING
    elif type == list[bool]:
        return proto.DataType.LIST_BOOL
    else:
        raise ValueError(f"Illegal type {type} for tag")

def convert(value: Any, type: int) -> proto.TagData:
    # Use the type of a TagData to convert to a TagData from a python type
    tag_data = proto.TagData()
    match type:
        case proto.DataType.INT:
            tag_data.int_data = int(value)
        case proto.DataType.LONG:
            tag_data.long_data = int(value)
        case proto.DataType.FLOAT:
            tag_data.float_data = float(value)
        case proto.DataType.STRING:
            tag_data.string_data = str(value)
        case proto.DataType.BOOL:
            tag_data.bool_data = bool(value)
        case proto.DataType.LIST_INT:
            tag_data.list_int_data.list.extend(list([int(x) for x in value]))
        case proto.DataType.LIST_LONG:
            tag_data.list_long_data.list.extend(list([int(x) for x in value]))
        case proto.DataType.LIST_FLOAT:
            tag_data.list_float_data.list.extend(list([float(x) for x in value]))
        case proto.DataType.LIST_STRING:
            tag_data.list_string_data.list.extend(list([str(x) for x in value]))
        case proto.DataType.LIST_BOOL:
            tag_data.list_bool_data.list.extend(list([bool(x) for x in value]))
        case _:
            raise ValueError(f"Unknown tag type {type}")
    return tag_data