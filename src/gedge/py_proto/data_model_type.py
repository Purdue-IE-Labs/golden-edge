from dataclasses import dataclass
from typing import Any, Self

from gedge import proto

@dataclass
class DataModelType:
    path: str

    def to_proto(self) -> proto.DataModelType:
        return proto.DataModelType(path=self.path)

    @classmethod
    def from_proto(cls, proto: proto.DataModelType):
        return cls(proto.path)
    
    def to_json5(self) -> str:
        return self.path
    
    @classmethod
    def from_json5(cls, json5: Any) -> Self:
        assert isinstance(json5, str)
        return cls(json5)