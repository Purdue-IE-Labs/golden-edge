from __future__ import annotations
from dataclasses import dataclass

from gedge import proto

from typing import Any, Self, TYPE_CHECKING

from gedge.py_proto.base_type import BaseType
from gedge.py_proto.data_model import DataObject
from gedge.py_proto.data_model_object_config import DataModelObjectConfig
from gedge.py_proto.data_model_type import DataModelType
from gedge.py_proto.data_object_config import DataObjectConfig

if TYPE_CHECKING:
    from gedge.node.gtypes import TagBaseValue
    from gedge.py_proto.base_data import BaseData

@dataclass
class Prop:
    value: DataObject

    @property
    def config(self):
        return self.value.config.config
    
    def to_proto(self) -> proto.Prop:
        config = self.config.to_proto()
        value = self.value.to_proto()
        return proto.Prop(config=config, value=value) 
    
    def to_value(self) -> BaseData:
        from gedge.py_proto.base_data import BaseData
        assert isinstance(self.value.data, BaseData)
        return self.value.data

    @classmethod
    def from_json5(cls, json5: Any):
        from gedge.py_proto.config import Config
        if isinstance(json5, dict):
            # we do not pull the model from the historian
            # we instead use a local version of it
            path = DataModelType.from_json5(json5["model_path"])
            config = Config(DataModelObjectConfig(path))
            c = config.config.load(path) # type: ignore
            res = DataObject.from_json5(json5["model"], DataObjectConfig.from_model_config(c))
            return cls(res)
        else:
            t = Prop.intuit_type(json5)
            ob = DataObjectConfig.from_base_type(t)
            res = DataObject.from_py_value(json5, ob)
            return cls(res)
    
    def to_json5(self) -> dict | Any:
        if self.config.is_base_type():
            return self.value.data.value # type: ignore
        j = {}
        data: list[DataObject] = self.value.data # type: ignore
        model_path = self.config.get_model_object_config().get_path() # type: ignore
        configs = self.config.get_model_items()
        if configs is None:
            raise ValueError(f"No model items defined on model {model_path.full_path}") # type: ignore

        for d, c in zip(data, configs):
            j["model_path"] = model_path
            j["model"] = {
                c.path: d.to_json5()
            }
        return j
    
    @classmethod
    def from_proto(cls, proto: proto.Prop) -> Self:
        from gedge.py_proto.config import Config
        config = Config.from_proto(proto.config)
        value = DataObject.from_proto(proto.value, DataObjectConfig.from_config(config))
        return cls(value)
    
    @classmethod
    def from_value(cls, value: TagBaseValue) -> Self:
        type_ = cls.intuit_type(value)
        ob = DataObjectConfig.from_base_type(type_)
        value_ = DataObject.from_py_value(value, ob)
        return cls(value_)
    
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

@dataclass
class Props:
    props: dict[str, Prop]
    
    def to_proto(self) -> proto.Props:
        return proto.Props(props={key:value.to_proto() for key, value in self.props.items()})
    
    def to_value(self) -> dict[str, Any]:
        return {key:value.to_value() for key, value in self.props.items()}
    
    @classmethod
    def from_proto(cls, props: proto.Props) -> Self:
        return cls({key:Prop.from_proto(value) for key, value in props.props.items()})
    
    @classmethod
    def from_value(cls, props: dict[str, Any]) -> Self:
        return cls({key:Prop.from_value(value) for key, value in props.items()})
    
    @classmethod
    def from_json5(cls, props: Any) -> Self:
        if not isinstance(props, dict):
            raise ValueError(f"invalid props {props}")
        props = {key:Prop.from_json5(value) for key, value in props.items()}
        return cls(props)
    
    def to_json5(self) -> dict:
        if self.is_empty():
            return {}
        j = {key:value.to_json5() for key, value in self.props.items()}
        return {"props": j}
    
    def is_empty(self) -> bool:
        return len(self.props) == 0
    
    @classmethod
    def empty(cls) -> Self:
        return cls({})
    
    def add_prop(self, key: str, value: Any):
        self.props[key] = Prop.from_value(value)
    
    def __iter__(self):
        yield from self.props
    
    def __getitem__(self, key: str):
        return self.props[key]
    