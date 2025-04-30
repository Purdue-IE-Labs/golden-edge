from __future__ import annotations
from dataclasses import dataclass
from email.mime import base
from typing import Any, Self, TYPE_CHECKING

from gedge import proto
from gedge.comm.keys import key_join
from gedge.py_proto.base_type import BaseType
from gedge.py_proto.data_model_config import DataModelConfig, DataModelItemConfig

if TYPE_CHECKING:
    from gedge.py_proto.config import Config
    from gedge.py_proto.data_object_config import DataObjectConfig
    from gedge.py_proto.base_data import BaseData
    from gedge.node.gtypes import TagBaseValue, TagValue

@dataclass
class DataObject:
    data: BaseData | list[DataObject]
    config: DataObjectConfig

    @classmethod
    def from_json5(cls, j: Any, config: DataObjectConfig) -> Self:
        from gedge.py_proto.base_data import BaseData
        if not isinstance(j, dict):
            type = config.get_base_type()
            if not type:
                raise ValueError(f"Data model configuration has a base type here, but you passed a model {j}")
            data = BaseData.from_value(j, type)
            return cls(data, config)

        config_objects = config.get_config_items()
        if config_objects is None:
            raise ValueError(f"No tags found for model {config.path}")
        data = []
        for c, value in zip(config_objects, j.values()):
            data.append(DataObject.from_json5(value, c))
        return cls(data, config)

    def to_json5(self) -> dict | Any:
        if self.is_base_data():
            return self.data.to_py() # type: ignore
        if not self.config.is_model_object():
            raise ValueError(f"Trying to put a data object into json without having the model ({self.config.path}) pulled")
        res = {}
        data: list[DataObject] = self.data # type: ignore
        configs = self.config.get_model_items()
        if configs is None:
            raise ValueError(f"No tags defined on model {self.config.path}")
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
        oneof = proto.WhichOneof("data")
        if oneof == "base_data":
            type = config.get_base_type()
            if not type:
                raise ValueError(f"config is not base type but proto has {proto.base_data} base data, {proto.model_data}")
            data = BaseData.from_proto(proto.base_data, type)
        elif oneof == "model_data":
            data = list(proto.model_data.data)
            configs = config.get_config_items()
            if configs is None:
                raise ValueError(f"No items in config {config}, but we have a list of {data}")
            data = [DataObject.from_proto(d, c) for d, c in zip(data, configs)]
        else:
            raise LookupError("No values set in protobuf DataObject")
        return cls(data, config)
    
    @classmethod
    def py_to_proto(cls, value: TagValue, config: DataObjectConfig) -> proto.DataObject:
        return cls.from_value(value, config).to_proto()
    
    @classmethod
    def proto_to_py(cls, proto: proto.DataObject, config: DataObjectConfig) -> TagValue:
        return cls.from_proto(proto, config).to_value()
    
    @classmethod
    def from_model_value(cls, value: dict, config: DataObjectConfig) -> Self:
        res = cls([], config)
        assert isinstance(res.data, list)
        configs = config.get_model_items()
        if configs is None:
            raise LookupError(f"No tags found on model {config.path}")
        configs = {c.path: c for c in configs}
        for k, v in configs.items():
            if k not in value:
                raise LookupError(f"No tag with path {k} included in model data for model {config.path}, but that tag is in the model definition!")
            res.data.append(cls.from_value(value[k], v.config))
        return res
    
    @classmethod
    def from_py_value(cls, value: Any, config: DataObjectConfig) -> Self:
        from gedge.py_proto.base_data import BaseData
        type = config.get_base_type()
        if type is None:
            raise LookupError(f"Passed in python value {value}, but configuration is a model!")
        return cls(BaseData.from_value(value, type), config)
    
    @classmethod
    def from_value(cls, value: Any | dict, config: DataObjectConfig) -> Self:
        if isinstance(value, dict):
            return cls.from_model_value(value, config)
        return cls.from_py_value(value, config) 
    
    def to_value(self) -> TagValue:
        if self.is_base_data():
            return self.data.to_py() # type: ignore

        data: list[DataObject] = self.data # type: ignore
        configs = self.config.get_model_items()
        if configs is None:
            raise LookupError(f"No tags defined for model {self.config.path}")
        j = {}
        for d, c in zip(data, configs):
            j[c.path] = d.to_value()
        return j
    
    @classmethod
    def from_flat_value(cls, value: dict[str, TagBaseValue], config: DataObjectConfig, prefix: str = "") -> Self:
        '''
        we have
        model {
            pump: Pump,
            tag: float,
        }
        value = {
            "tag": 1.1,
            "pump/speed": 10,
            "pump/temp": 12,
            "model/modeltag": 16,
        }
        config {
            items {
                "pump": {
                    items: {
                        "speed": 10,
                        "temp": 12,
                    }
                },
                "tag": BaseType,
                "model": {
                    items: {
                        "modeltag": 10
                    }
                }
            }
        }
        '''
        res = cls([], config)
        assert isinstance(res.data, list)
        configs = config.get_model_items()
        if configs is None:
            raise LookupError(f"No tags found on model {config.path}")
        configs = {c.path: c for c in configs}
        for k, v in configs.items():
            if k in value:
                res.data.append(cls.from_py_value(value[k], v.config))
        subsets: list[tuple[dict, DataModelItemConfig]] = []
        for k, v in configs.items():
            if k not in value:
                starts = key_join(prefix, k) if prefix else k
                subsets.append(({key[(len(starts) + 1):]: value for key, value in value.items() if key.startswith(starts)}, v))
        # TODO: handle those that fit into neither bucket
        for s in subsets:
            if s[0]:
                prefix = key_join(prefix, s[1].path) if prefix else s[1].path
                res.data.append(cls.from_flat_value(s[0], s[1].config, prefix))
        return res

    def to_flat_value(self, prefix: str = "") -> dict[str, TagBaseValue]:
        if self.is_base_data():
            base_data = { prefix: self.data.to_py() } # type: ignore
            return base_data

        data: list[DataObject] = self.data # type: ignore
        flat_data: dict[str, TagBaseValue] = {}
        if not self.config.is_model_object():
            raise LookupError()
        configs = self.config.get_model_config().items # type: ignore
        for d, c in zip(data, configs):
            new_path = key_join(prefix, c.path) if prefix else c.path
            flat_data.update(d.to_flat_value(new_path))
        return flat_data
    
    @classmethod
    def from_flat_proto(cls, value: dict[str, proto.BaseData], config: DataObjectConfig, prefix: str = "") -> Self:
        res = cls([], config)
        assert isinstance(res.data, list)
        configs = config.get_model_items()
        if configs is None:
            raise LookupError(f"No tags found on model {config.path}")
        configs = {c.path: c for c in configs}
        for k, v in configs.items():
            if k in value:
                res.data.append(DataObject(BaseData.from_proto(value[k], v.config.get_base_type()), v.config)) # type: ignore
        subsets: list[tuple[dict, DataModelItemConfig]] = []
        for k, v in configs.items():
            if k not in value:
                starts = key_join(prefix, k) if prefix else k
                subsets.append(({key[(len(starts) + 1):]: value for key, value in value.items() if key.startswith(starts)}, v))
        # TODO: handle those that fit into neither bucket, or should we just ignore them?
        for s in subsets:
            if s[0]:
                prefix = key_join(prefix, s[1].path) if prefix else s[1].path
                res.data.append(cls.from_flat_value(s[0], s[1].config, prefix))
        return res
    
    def to_flat_proto(self, prefix: str = "") -> dict[str, proto.BaseData]:
        if self.is_base_data():
            base_data = { prefix: self.data.to_proto() } # type: ignore
            return base_data

        data: list[DataObject] = self.data # type: ignore
        flat_data: dict[str, proto.BaseData] = {}
        if not self.config.is_model_object():
            raise LookupError()
        configs = self.config.get_model_config().items # type: ignore
        for d, c in zip(data, configs):
            new_path = key_join(prefix, c.path) if prefix else c.path
            flat_data.update(d.to_flat_proto(new_path))
        return flat_data

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
