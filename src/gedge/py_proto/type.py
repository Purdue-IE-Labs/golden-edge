from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from gedge import proto
from gedge.py_proto.base_type import BaseType
from gedge.py_proto.data_model_ref import DataModelRef

if TYPE_CHECKING:
    from gedge.py_proto.data_model_config import DataModelConfig

@dataclass
class Type:
    type: BaseType | DataModelRef

    def to_proto(self) -> proto.Type:
        if isinstance(self.type, BaseType):
            return proto.Type(base_type=self.type.to_proto())
        return proto.Type(data_model_ref=self.type.to_proto())
    
    @classmethod
    def from_proto(cls, proto: proto.Type) -> Self:
        oneof = proto.WhichOneof("type")
        if oneof == "base_type":
            return cls(BaseType.from_proto(proto.base_type))
        elif oneof == "data_model_ref":
            return cls(DataModelRef.from_proto(proto.data_model_ref))
        raise ValueError(f"none of fields for proto.Type were set")
    
    def to_json5(self):
        raise NotImplementedError
    
    @classmethod
    def from_json5(cls, j: Any):
        if not (("base_type" in j) ^ ("model_path" in j)):
            raise ValueError("couldn't find a type")
        if "base_type" in j:
            return cls.from_base_type(j["base_type"])
        return cls.from_model_ref(j["model_path"])
    
    @classmethod
    def from_base_type(cls, j: str) -> Self:
        return cls(BaseType.from_json5_base_type(j))
    
    @classmethod
    def from_model_ref(cls, j: str) -> Self:
        return cls(DataModelRef.from_json5(j))
    
    def is_base_type(self) -> bool:
        return isinstance(self.type, BaseType)
    
    def is_model_ref(self) -> bool:
        return isinstance(self.type, DataModelRef)
    
    def get_base_type(self) -> BaseType | None:
        if self.is_base_type():
            return self.type # type: ignore
        return None
    
    def get_model_ref(self) -> DataModelRef | None:
        if self.is_model_ref():
            return self.type # type: ignore
        return None
    
    def load_model(self) -> DataModelConfig | None:
        if self.is_model_ref():
            return self.type.load_model() # type: ignore
        return None
