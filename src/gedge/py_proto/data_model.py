from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Self, TYPE_CHECKING

from gedge import proto
from gedge.py_proto.base_type import BaseType
from gedge.py_proto.data_model_object_config import DataModelObjectConfig
from gedge.py_proto.data_model_type import DataModelType

if TYPE_CHECKING:
    from gedge.py_proto.config import Config
    from gedge.py_proto.data_object_config import DataObjectConfig
    from gedge.py_proto.base_data import BaseData

@dataclass
class DataObject:
    data: BaseData | list[Self]

    @classmethod
    def from_json5(cls, json5: Any, config: Config) -> Self:
        from gedge.py_proto.base_data import BaseData
        if not isinstance(json5, dict):
            data = BaseData.from_json5(json5)
            return cls(data)

        assert isinstance(config.config, DataModelObjectConfig)
        if isinstance(config.config.repr, DataModelType):
            # config.config.fetch()
            raise NotImplementedError

        data = []
        for key, value in json5.items():
            c = [i for i in config.config.repr.items if i.path == key]
            data.append(DataObject.from_json5(value, c[0].config.config))
        return cls(data)

    def to_json5(self, config: Config) -> dict | Any:
        from gedge.py_proto.data_model_config import DataModelConfig
        from gedge.py_proto.data_model_object_config import DataModelObjectConfig
        from gedge.py_proto.base_data import BaseData
        assert isinstance(config.config, DataModelObjectConfig)
        assert isinstance(config.config.repr, DataModelConfig)
        if isinstance(self.data, BaseData):
            return self.data.to_py()
        else:
            res = {}
            configs = [c for c in config.config.repr.items]
            for d, n in zip(self.data, configs):
                res[n.path] = d.to_json5(n.config.config)
            return d

    def to_proto(self) -> proto.DataObject:
        from gedge.py_proto.base_data import BaseData
        if isinstance(self.data, BaseData):
            return proto.DataObject(base_data=self.data.to_proto())
        else:
            res = [d.to_proto() for d in self.data]
            return proto.DataObject(model_data=proto.DataModel(data=res))

    @classmethod
    def from_proto(cls, proto: proto.DataObject, config: Config) -> Self:
        from gedge.py_proto.data_model_config import DataModelConfig
        from gedge.py_proto.data_model_object_config import DataModelObjectConfig
        from gedge.py_proto.base_data import BaseData
        # how to handle this?
        if proto.base_data:
            type = config.config
            assert isinstance(type, BaseType)
            data = BaseData.from_proto(proto.base_data, type)
        else:
            assert isinstance(config.config, DataModelObjectConfig)
            assert isinstance(config.config.repr, DataModelConfig)
            data = list(proto.model_data.data)
            configs = [i for i in config.config.repr.items]
            # TODO: what to do here, we only have the path to the data model here
            data = [DataObject.from_proto(d, c.config.config) for d, c in zip(data, configs)]
        return cls(data)
    
    @classmethod
    def from_value(cls, value: DataModel):
        # TODO: what does a model value look like?
        pass
    
    def to_value(self):
        pass
