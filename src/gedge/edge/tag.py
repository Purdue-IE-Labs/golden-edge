from typing import Any, Dict, Union
from types import GenericAlias
from gedge.proto import TagData, DataType, ListInt, ListBool, ListFloat, ListLong, ListString, Property

class Tag:
    def __init__(self, name: str, type: Any, key_expr: str, properties: Dict[str, Any] = {}):
        self.name = name
        if not isinstance(type, int):
            type = Tag._convert_type(type)
        self.type: int = type

        self.properties: dict[str, Property] = {}
        for name, value in properties.items():
            type_ = Tag._intuit_property_type(value)
            self.properties[name] = Property(type=type_, value=self.convert_property(value, type_))

        self.key_expr = key_expr

    def convert(self, value: Any) -> TagData:
        tag_data = TagData()
        match self.type:
            case DataType.INT:
                tag_data.int_data = int(value)
            case DataType.LONG:
                tag_data.long_data = int(value)
            case DataType.FLOAT:
                tag_data.float_data = float(value)
            case DataType.STRING:
                tag_data.string_data = str(value)
            case DataType.BOOL:
                tag_data.bool_data = bool(value)
            case DataType.LIST_INT:
                tag_data.list_int_data.list.extend(list([int(x) for x in value]))
            case DataType.LIST_LONG:
                tag_data.list_long_data.list.extend(list([int(x) for x in value]))
            case DataType.LIST_FLOAT:
                tag_data.list_float_data.list.extend(list([float(x) for x in value]))
            case DataType.LIST_STRING:
                tag_data.list_string_data.list.extend(list([str(x) for x in value]))
            case DataType.LIST_BOOL:
                tag_data.list_bool_data.list.extend(list([bool(x) for x in value]))
            case _:
                raise ValueError("unknown tag type")
        return tag_data

    def convert_property(self, value: Any, type: int) -> TagData:
        tag_data = TagData()
        match type:
            case DataType.INT:
                tag_data.int_data = int(value)
            case DataType.LONG:
                tag_data.long_data = int(value)
            case DataType.FLOAT:
                tag_data.float_data = float(value)
            case DataType.STRING:
                tag_data.string_data = str(value)
            case DataType.BOOL:
                tag_data.bool_data = bool(value)
            case DataType.LIST_INT:
                tag_data.list_int_data.list.extend(list([int(x) for x in value]))
            case DataType.LIST_LONG:
                tag_data.list_long_data.list.extend(list([int(x) for x in value]))
            case DataType.LIST_FLOAT:
                tag_data.list_float_data.list.extend(list([float(x) for x in value]))
            case DataType.LIST_STRING:
                tag_data.list_string_data.list.extend(list([str(x) for x in value]))
            case DataType.LIST_BOOL:
                tag_data.list_bool_data.list.extend(list([bool(x) for x in value]))
            case _:
                raise ValueError("unknown tag type")
        return tag_data

    @staticmethod
    def from_tag_data(tag_data: TagData, type: DataType) -> Any:
        match type:
            case DataType.INT:
                return int(tag_data.int_data)
            case DataType.LONG:
                return int(tag_data.long_data)
            case DataType.FLOAT:
                return float(tag_data.float_data)
            case DataType.STRING:
                return str(tag_data.string_data)
            case DataType.BOOL:
                return bool(tag_data.bool_data)
            case DataType.LIST_INT:
                return list(tag_data.list_int_data.list)
            case DataType.LIST_LONG:
                return list(tag_data.list_long_data.list)
            case DataType.LIST_FLOAT:
                return list(tag_data.list_float_data.list)
            case DataType.LIST_STRING:
                return list(tag_data.list_string_data.list)
            case DataType.LIST_BOOL:
                return list(tag_data.list_bool_data.list)
        raise ValueError("cannot convert")


    @staticmethod
    def _convert_type(type_: Any) -> DataType:
        """
        Note: Python does not support the notion of a "long" data type.
        In fact, there are several data types that may be supported 
        in our protocol that are not recognized in Python
        Thus, users can also pass in a DataType object directly, which 
        has all the types allowed by our protocol. As an API convenience,
        we allow the user to use built-in Python types.
        """
        if type_ == int:
            return DataType.INT
        elif type_ == float:
            return DataType.FLOAT
        elif type_ == str:
            return DataType.STRING
        elif type_ == bool:
            return DataType.BOOL
        elif type_ == list[int]:
            return DataType.LIST_INT
        elif type_ == list[float]:
            return DataType.LIST_FLOAT
        elif type_ == list[str]:
            return DataType.LIST_STRING
        elif type_ == list[bool]:
            return DataType.LIST_BOOL
        else:
            raise ValueError("unknown type")
        
    @staticmethod
    def _intuit_property_type(value: Any) -> DataType:
        if isinstance(value, str):
            return DataType.STRING
        elif isinstance(value, int):
            return DataType.INT
        elif isinstance(value, float):
            return DataType.FLOAT
        elif isinstance(value, bool):
            return DataType.BOOL
        else:
            raise ValueError("illegal type for property")

if __name__ == "__main__":
    print("list int")
    t = Tag("my_tag", list[int], properties={"joe": "buck"})
    print(t.type)
    print(f"\nDatatype.LIST_BOOL")
    t = Tag("my_tag", DataType.LIST_BOOL, properties={"joe": "buck"})
    print(t.type)
    print(f"\nint")
    t = Tag("my_tag", int, properties={"joe": "buck"})
    print(t.type)
    t = Tag("my_tag", list[float])
    t = Tag("my_tag", type=list[str])
    t = Tag("my_tag", DataType.LIST_LONG)
    print(t.type)
