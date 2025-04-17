from __future__ import annotations
from dataclasses import dataclass, field

from gedge import proto

from typing import Any, Self, TYPE_CHECKING

from gedge.py_proto.base_type import BaseType
from gedge.py_proto.data_model import DataObject
from gedge.py_proto.data_model_config import DataModelConfig
from gedge.py_proto.data_model_object_config import DataModelObjectConfig
from gedge.py_proto.data_model_type import DataModelType

if TYPE_CHECKING:
    from gedge.node.gtypes import TagBaseValue
    from gedge.py_proto.config import Config
    from gedge.comm.comm import Comm
    from gedge.py_proto.base_data import BaseData

@dataclass
class Prop:
    config: Config
    value: DataObject
    temp_object: dict | None = field(default=None)
    
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
        from gedge.py_proto.base_data import BaseData
        if isinstance(json5, dict):
            # we cannot pull model right now because we are just parsing the json5
            path: str = json5["model_path"]
            config = Config(DataModelObjectConfig(DataModelType(path)))
            return cls(config, DataObject([]), json5["model"])
        else:
            t = Prop.intuit_type(json5)
            data = BaseData.from_value(json5, t)
            return cls(Config(t), DataObject(data))
    
    def to_json5(self) -> dict | Any:
        from gedge.py_proto.base_data import BaseData
        if isinstance(self.config.config, BaseType):
            assert isinstance(self.value.data, BaseData)
            return self.value.data.value
        else:
            j = {}
            assert not isinstance(self.value.data, BaseData)
            for object in self.value.data:
                j = object.to_json5(self.config.config.repr)
            return j
    
    def fetch(self, comm: Comm):
        if not isinstance(self.config.config, DataModelObjectConfig):
            return
        if not isinstance(self.config.config.repr, DataModelConfig):
            return
        if not self.temp_object:
            return
        config = comm.pull_model(self.config.config.repr.path)
        # TODO
        # DataObject.from_json5(self.temp_object, config)
        return
    
    @classmethod
    def from_proto(cls, prop: proto.Prop) -> Self:
        from gedge.py_proto.config import Config
        config = Config.from_proto(prop.config)
        value = DataObject.from_proto(prop.value, config)
        return cls(config, value)
    
    @classmethod
    def from_value(cls, value: TagBaseValue) -> Self:
        type_ = cls.intuit_type(value)
        value_ = DataObject.from_value(value, type_)
        return cls(type_, value_)
    
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
    
    # @classmethod
    # def from_value(cls, props: dict[str, Any]) -> Self:
    #     return cls({key:Prop.from_value(value) for key, value in props.items()})
    
    @classmethod
    def from_json5(cls, props: Any) -> Self:
        if not isinstance(props, dict):
            raise ValueError(f"invalid props {props}")
        props = {key:Prop.from_json5(value) for key, value in props.items()}
        return cls(props)
    
    def to_json5(self) -> dict:
        j = {key:value.to_json5() for key, value in self.props.items()}
        return j
    
    @classmethod
    def empty(cls) -> Self:
        return cls({})
    
    def add_prop(self, key: str, value: Any):
        self.props[key] = Prop.from_value(value)
    