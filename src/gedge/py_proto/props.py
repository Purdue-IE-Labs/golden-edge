from __future__ import annotations
from dataclasses import dataclass

from gedge import proto

from typing import Any, Self, TYPE_CHECKING

from gedge.py_proto.base_type import BaseType
from gedge.py_proto.data_model import DataItem
from gedge.py_proto.type import Type

if TYPE_CHECKING:
    from gedge.node.gtypes import TagBaseValue
    from gedge.node.gtypes import TagValue
    from gedge.py_proto.base_data import BaseData

@dataclass
class Prop:
    key: str
    value: BaseData

    @property
    def type(self) -> BaseType:
        return self.value.type
    
    def to_proto(self) -> proto.Prop:
        type = self.type.to_proto()
        value = self.value.to_proto()
        return proto.Prop(key=self.key, type=type, value=value) 
    
    def to_value(self) -> TagValue:
        return self.value.to_py()

    @classmethod
    def from_json5(cls, key: str, j: Any) -> Self:
        from gedge.py_proto.base_data import BaseData
        if isinstance(j, dict):
            # this is for if they want to specify both type and value
            raise NotImplementedError
        t = Prop.intuit_type(j)
        res = BaseData.from_value(j, t)
        return cls(key, res)
    
    def to_json5(self) -> dict | Any:
        j = {
            self.key: self.value.to_json5()
        }
        # data: list[DataObject] = self.value.data # type: ignore
        # model_config = self.type.load_model()
        # if not model_config:
        #     raise ValueError
        # configs = model_config.items
        # if configs is None:
        #     raise ValueError(f"No model items defined on model {model_config.full_path}") # type: ignore

        # for d, c in zip(data, configs):
        #     j["model_path"] = model_config.full_path
        #     j["model"] = {
        #         c.path: d.to_json5()
        #     }
        return j
    
    @classmethod
    def from_proto(cls, proto: proto.Prop) -> Self:
        from gedge.py_proto.base_data import BaseData
        type = BaseType.from_proto(proto.type)
        key = proto.key
        value = BaseData.from_proto(proto.value, type)
        return cls(key, value)
    
    @staticmethod
    def intuit_type(value: Any) -> BaseType:
        if isinstance(value, str):
            return BaseType.STRING
        elif isinstance(value, int):
            return BaseType.INT
        elif isinstance(value, float):
            return BaseType.FLOAT
        elif isinstance(value, bool):
            return BaseType.BOOL
        elif isinstance(value, list):
            if len(value) == 0:
                return BaseType.LIST_INT
            val0 = value[0]
            if isinstance(val0, str):
                return BaseType.LIST_STRING
            elif isinstance(val0, int):
                return BaseType.LIST_INT
            elif isinstance(val0, float):
                return BaseType.LIST_FLOAT
            elif isinstance(val0, bool):
                return BaseType.LIST_BOOL
        raise ValueError(f"Illegal type for property. Allowed properties are str, int, float, bool. value is of type {type(value)}")

# @dataclass
# class Props:
#     props: dict[str, Prop]
    
#     def to_proto(self) -> proto.Props:
#         return proto.Props(props={key:value.to_proto() for key, value in self.props.items()})
    
#     def to_value(self) -> dict[str, TagValue]:
#         return {key:value.to_value() for key, value in self.props.items()}
    
#     @classmethod
#     def from_proto(cls, props: proto.Props) -> Self:
#         return cls({key:Prop.from_proto(value) for key, value in props.props.items()})
    
#     @classmethod
#     def from_value(cls, props: dict[str, Any]) -> Self:
#         return cls({key:Prop.from_value(value) for key, value in props.items()})
    
#     @classmethod
#     def from_json5(cls, j: Any) -> Self:
#         if not isinstance(j, dict):
#             raise ValueError(f"invalid props {j}")
#         if "props" not in j:
#             return cls.empty()
#         props = j["props"]
#         if not isinstance(props, dict):
#             raise ValueError(f"props must be a dictionary, found {props}")
#         props = {key:Prop.from_json5(value) for key, value in props.items()}
#         return cls(props)
    
#     def to_json5(self) -> dict:
#         if self.is_empty():
#             return {}
#         j = {key:value.to_json5() for key, value in self.props.items()}
#         return {"props": j}
    
#     def is_empty(self) -> bool:
#         return len(self.props) == 0
    
#     @classmethod
#     def empty(cls) -> Self:
#         return cls({})
    
#     def add_prop(self, key: str, value: Any):
#         self.props[key] = Prop.from_value(value)
    
#     def __iter__(self):
#         yield from self.props
    
#     def __getitem__(self, key: str):
#         return self.props[key]
    