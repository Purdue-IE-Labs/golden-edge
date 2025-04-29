from typing import Self
from gedge import proto
from enum import Enum, auto

class BaseType(Enum):
    UNKNOWN = proto.BaseType.UNKNOWN
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
        if isinstance(type, BaseType):
            return type
        return cls.from_py_type(type)

    @classmethod
    def from_proto(cls, proto: proto.BaseType) -> Self:
        return cls(int(proto))
    
    def to_json5(self) -> dict:
        mapping = {
            BaseType.INT: "int",
            BaseType.LONG: "long",
            BaseType.FLOAT: "float",
            BaseType.STRING: "string",
            BaseType.BOOL: "bool",
            BaseType.LIST_INT: "list[int]",
            BaseType.LIST_LONG: "list[long]",
            BaseType.LIST_FLOAT: "list[float]",
            BaseType.LIST_STRING: "list[string]",
            BaseType.LIST_BOOL: "list[bool]",
        }
        j = {
            "base_type": mapping[self]
        }
        return j
    
    @classmethod
    def from_json5(cls, j: dict) -> Self:
        type: str = j["base_type"]
        type = type.lower()
        return cls.from_json5_base_type(type)
    
    @classmethod
    def from_json5_base_type(cls, t: str) -> Self:
        mapping = {
            "int": BaseType.INT,
            "long": BaseType.LONG,
            "float": BaseType.FLOAT,
            "string": BaseType.STRING,
            "bool": BaseType.BOOL,
            "list[int]": BaseType.LIST_INT,
            "list[long]": BaseType.LIST_LONG,
            "list[float]": BaseType.LIST_FLOAT,
            "list[string]": BaseType.LIST_STRING,
            "list[bool]": BaseType.LIST_BOOL,
        }
        if t not in mapping:
            raise ValueError(f"Invalid type {t}")
        return cls(mapping[t])

    def to_proto(self) -> proto.BaseType:
        return self.value # type: ignore

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
            new_type = BaseType.INT
        elif type == float:
            new_type = BaseType.FLOAT
        elif type == str:
            new_type = BaseType.STRING
        elif type == bool:
            new_type = BaseType.BOOL
        elif type == list[int]:
            new_type = BaseType.LIST_INT
        elif type == list[float]:
            new_type = BaseType.LIST_FLOAT
        elif type == list[str]:
            new_type = BaseType.LIST_STRING
        elif type == list[bool]:
            new_type = BaseType.LIST_BOOL
        if new_type == -1:
            raise ValueError(f"Illegal type {type} for tag")
        
        return cls(new_type.value)

    def __repr__(self):
        return self.name

