from gedge import proto
from typing import Self, Any
from gedge.edge.types import Type

class DataType:
    def __init__(self, type: Type):
        if isinstance(type, DataType):
            type = type.type
        elif not isinstance(type, int):
            # print(f"type {type} not of instance int")
            type = self.from_py_type(type)
        # print(f"type: {type}")

        self.type: int = type
    
    def to_proto(self) -> proto.DataType:
        return self.type
    
    @classmethod
    def from_proto(self, proto: proto.DataType) -> Self:
        return DataType(proto)
    
    @classmethod
    def from_py_type(self, type: Any) -> Self:
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
        
        return new_type

    def __repr__(self):
        return f"Datatype type: {self.type}"