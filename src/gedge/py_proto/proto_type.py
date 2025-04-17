

from dataclasses import dataclass
from typing import Any, Self
from unittest.mock import Base

from gedge import proto
from gedge.py_proto.base_type import BaseType
from gedge.py_proto.data_model_type import DataModelType


# @dataclass
# class Type:
#     type: BaseType | DataModelType

#     def to_proto(self) -> proto.Type:
#         if isinstance(self.type, BaseType):
#             return proto.Type(base_type=self.type.to_proto())
#         else:
#             return proto.Type(data_model_type=self.type.to_proto())
    
#     @classmethod
#     def from_proto(cls, proto: proto.Type) -> Self:
#         # TODO: does proto.base_type populate if not set?
#         if proto.base_type:
#             return cls(BaseType.from_proto(proto.base_type))
#         return cls(DataModelType.from_proto(proto.data_model_type))
    
#     def to_json5(self) -> str:
#         return self.type.to_json5()
    
#     @classmethod
#     def from_json5(cls, json5: Any) -> Self:
#         raise NotImplementedError
    
#     @classmethod
#     def from_base_type_json5(cls, json5: str) -> Self:
#         t = BaseType.from_json5(json5)
#         return cls(t)
    
#     @classmethod
#     def from_model_type(cls, path: str) -> Self:
#         return cls(type=DataModelType(path))
    
#     @classmethod
#     def from_py_type(cls, type: Any) -> Self:
#         new_type = -1
#         if type == int:
#             new_type = BaseType.INT
#         elif type == float:
#             new_type = BaseType.FLOAT
#         elif type == str:
#             new_type = BaseType.STRING
#         elif type == bool:
#             new_type = BaseType.BOOL
#         elif type == list[int]:
#             new_type = BaseType.LIST_INT
#         elif type == list[float]:
#             new_type = BaseType.LIST_FLOAT
#         elif type == list[str]:
#             new_type = BaseType.LIST_STRING
#         elif type == list[bool]:
#             new_type = BaseType.LIST_BOOL
#         if new_type == -1:
#             raise ValueError(f"Illegal type {type} for tag")
        
#         return cls(new_type)

