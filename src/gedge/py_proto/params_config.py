from __future__ import annotations

from dataclasses import dataclass
from gedge.py_proto.data_object_config import DataObjectConfig
from gedge.py_proto.props import Props
from gedge import proto

from typing import Any, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from gedge.node.gtypes import TagBaseValue

@dataclass
class ParamsConfig:
    params: dict[str, DataObjectConfig]

    def to_proto(self) -> proto.ParamsConfig:
        params = {key:value.to_proto() for key, value in self.params.items()}
        return proto.ParamsConfig(params=params)
    
    @classmethod
    def from_proto(cls, proto: proto.ParamsConfig) -> Self:
        params = {key:DataObjectConfig.from_proto(value) for key, value in proto.params.items()}
        return cls(params)
    
    @classmethod
    def from_json5(cls, json: Any) -> Self:
        if not isinstance(json, dict):
            raise ValueError
        params = {}
        for key, value in json.items():
            params[key] = DataObjectConfig.from_json5(value)
        return cls(params)

    @classmethod
    def empty(cls) -> Self:
        return cls({})
    
    def __getitem__(self, key: str) -> DataObjectConfig:
        return self.params[key]
    
    def __iter__(self):
        yield from self.params
