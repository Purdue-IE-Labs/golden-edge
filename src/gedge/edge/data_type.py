from typing import Self
from gedge import proto
from enum import Enum, auto

class DataType(Enum):
    UNKNOWN = proto.DataType.UNKNOWN
    INT = auto()
    LONG = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    LIST_INT = auto()
    LIST_LONG = auto()
    LIST_FLOAT = auto()
    LIST_STRING = auto()
    LIST_BOOL = auto()

    @classmethod
    def from_type(cls, type: Self | type) -> Self:
        if isinstance(type, DataType):
            return type
        return cls.from_py_type(type)

    @classmethod
    def from_proto(cls, proto: proto.DataType) -> Self:
        return cls(int(proto))
    
    @classmethod
    def from_json5(cls, type: str) -> Self:
        mapping = {
            "int": DataType.INT,
            "long": DataType.LONG,
            "float": DataType.FLOAT,
            "string": DataType.STRING,
            "bool": DataType.BOOL,
            "list[int]": DataType.LIST_INT,
            "list[long]": DataType.LIST_LONG,
            "list[float]": DataType.LIST_FLOAT,
            "list[string]": DataType.LIST_STRING,
            "list[bool]": DataType.LIST_BOOL,
        }
        if type not in mapping:
            raise ValueError(f"Invalid type {type}")
        return cls(mapping[type])

    def to_proto(self) -> int:
        return self.value

    @classmethod
    def from_py_type(cls, type) -> Self:
        """
        Note: Python does not support the notion of a "long" data type.
        In fact, there are several data types that may be supported 
        in our protocol that are not recognized in Python
        Thus, users can also pass in a DataType object directly, which 
        has all the types allowed by our protocol. As an API convenience,
        we allow the user to use built-in Python types.
        """
        new_type = -1
        if type == int:
            new_type = proto.DataType.INT
        elif type == float:
            new_type = proto.DataType.FLOAT
        elif type == str:
            new_type = proto.DataType.STRING
        elif type == bool:
            new_type = proto.DataType.BOOL
        elif type == list[int]:
            new_type = proto.DataType.LIST_INT
        elif type == list[float]:
            new_type = proto.DataType.LIST_FLOAT
        elif type == list[str]:
            new_type = proto.DataType.LIST_STRING
        elif type == list[bool]:
            new_type = proto.DataType.LIST_BOOL
        if new_type == -1:
            raise ValueError(f"Illegal type {type} for tag")
        
        return cls.from_proto(new_type)

    def __repr__(self):
        return self.name

