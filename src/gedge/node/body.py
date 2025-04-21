from dataclasses import dataclass
from typing import Any, Self

from gedge.py_proto.data_object_config import DataObjectConfig
from gedge import proto

@dataclass
class BodyConfig:
    body: dict[str, DataObjectConfig]

    def to_proto(self):
        body = {key:value.to_proto() for key, value in self.body.items()}
        return proto.BodyConfig(body=body)
    
    @classmethod
    def from_proto(cls, proto: proto.BodyConfig) -> Self:
        body = {key: DataObjectConfig.from_proto(value) for key, value in proto.body.items()}
        return cls(body)
    
    @classmethod
    def from_json5(cls, j: Any) -> Self:
        if not isinstance(j, dict):
            raise ValueError(f"invalid body {j}")
        body = {key: DataObjectConfig.from_json5(value) for key, value in j.items()}
        return cls(body)
    
    @classmethod
    def empty(cls) -> Self:
        return cls({})
    
    def __getitem__(self, key: str):
        return self.body[key]
