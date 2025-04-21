from __future__ import annotations

from dataclasses import dataclass
from tkinter import W
from typing import Any, Self, TYPE_CHECKING

from gedge import proto
from gedge.node.gtypes import TagBaseValue
from gedge.py_proto.base_type import BaseType

if TYPE_CHECKING:
    from gedge.py_proto.config import Config
    from gedge.py_proto.data_object_config import DataObjectConfig
    from gedge.py_proto.base_data import BaseData

@dataclass
class DataObject:
    data: BaseData | list[DataObject]
    config: DataObjectConfig

    @classmethod
    def from_json5(cls, json5: Any, config: DataObjectConfig) -> Self:
        from gedge.py_proto.base_data import BaseData
        if not isinstance(json5, dict):
            type = config.get_base_type()
            if not type:
                raise Exception
            data = BaseData.from_value(json5, type)
            return cls(data, config)

        config_objects = config.get_config_items()
        if config_objects is None:
            raise Exception
        data = []
        for c, value in zip(config_objects, json5.values()):
            data.append(DataObject.from_json5(value, c))
        return cls(data, config)

    def to_json5(self) -> dict | Any:
        if self.is_base_data():
            return self.data.to_py() # type: ignore
        if not self.config.is_model_object():
            raise Exception
        res = {}
        data: list[DataObject] = self.data # type: ignore
        configs = self.config.get_model_items()
        if configs is None:
            raise Exception
        for d, c in zip(data, configs):
            res[c.path] = d.to_json5()
        return res

    def to_proto(self) -> proto.DataObject:
        if self.is_base_data():
            return proto.DataObject(base_data=self.data.to_proto()) # type: ignore
        res = [d.to_proto() for d in self.data] # type: ignore
        return proto.DataObject(model_data=proto.DataModel(data=res))

    @classmethod
    def from_proto(cls, proto: proto.DataObject, config: DataObjectConfig) -> Self:
        from gedge.py_proto.base_data import BaseData
        if proto.base_data:
            type = config.get_base_type()
            if not type:
                raise Exception
            data = BaseData.from_proto(proto.base_data, type)
        else:
            data = list(proto.model_data.data)
            configs = config.get_config_items()
            if configs is None:
                raise Exception
            data = [DataObject.from_proto(d, c) for d, c in zip(data, configs)]
        return cls(data, config)
    
    @classmethod
    def from_model_value(cls, value: list[Any], config: DataObjectConfig) -> Self:
        res = cls([], config)
        configs = config.get_config_items()
        if configs is None:
            raise Exception
        for val, c in zip(value, configs):
            if isinstance(val, list):
                res.data.append(cls.from_model_value(val, c)) # type: ignore
            res.data.append(cls.from_py_value(val, c)) # type: ignore
        return res
    
    @classmethod
    def from_py_value(cls, value: Any, config: DataObjectConfig) -> Self:
        from gedge.py_proto.base_data import BaseData
        type = config.get_base_type()
        if type is None:
            raise Exception(value, config)
        return cls(BaseData.from_value(value, type), config)
    
    def to_value(self) -> TagBaseValue | dict[str, Any]:
        if self.is_base_data():
            return self.data.to_py() # type: ignore

        data: list[DataObject] = self.data # type: ignore
        configs = self.config.get_model_items()
        if configs is None:
            raise Exception
        j = {}
        for d, c in zip(data, configs):
            j[c.path] = d.to_value()
        return j

    def is_base_data(self) -> bool:
        from gedge.py_proto.base_data import BaseData
        return isinstance(self.data, BaseData)
    
    def is_model_data(self) -> bool:
        from gedge.py_proto.base_data import BaseData
        return not isinstance(self.data, BaseData)
    
    def get_base_data(self) -> BaseData | None:
        if not self.is_base_data():
            return None
        return self.data # type: ignore

    def get_model_data(self) -> list[DataObject] | None:
        if self.is_base_data():
            return None
        return self.data  # type: ignore
