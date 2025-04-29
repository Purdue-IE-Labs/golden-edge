from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from multiprocessing import Value

from gedge.node.body import BodyConfig
from gedge.py_proto.props import Props
from gedge import proto
from typing import Any, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from gedge.node.gtypes import Type

# CONFIG object
@dataclass
class MethodResponseConfig:
    code: int
    type: MethodResponseType
    props: Props
    body: BodyConfig
    
    def to_proto(self) -> proto.MethodResponseConfig:
        props = self.props.to_proto()
        body = self.body.to_proto()
        return proto.MethodResponseConfig(code=self.code, props=props, body=body)

    @classmethod
    def from_proto(cls, proto: proto.MethodResponseConfig) -> Self:
        type = MethodResponseType.from_proto(proto.type)
        props = Props.from_proto(proto.props)
        body = BodyConfig.from_proto(proto.body)
        return cls(proto.code, type, props, body)
    
    @classmethod
    def from_json5(cls, j: Any) -> Self:
        if not isinstance(j, dict):
            raise ValueError(f"Invalid method repsonse type, expected dict, got {j}")
        
        if "code" not in j:
            raise LookupError(f"Method response must include 'code', got {j}")
        if "type" not in j:
            raise LookupError(f"Method response must include 'type', got {j}")
        code = int(j["code"])

        props = Props.from_json5(j)
        body = BodyConfig.from_json5(j.get("body", {}))
        type = MethodResponseType.from_json5(j)
        return cls(code, type, props, body)
    
    def is_ok(self) -> bool:
        return self.type == MethodResponseType.OK
    
    def is_err(self) -> bool:
        return self.type == MethodResponseType.ERR
    
    def is_info(self) -> bool:
        return self.type == MethodResponseType.INFO

class MethodResponseType(Enum):
    OK = proto.MethodResponseType.OK
    ERR = auto()
    INFO = auto()

    def to_json5(self) -> dict:
        mapping = {
            MethodResponseType.OK: "ok",
            MethodResponseType.ERR: "err",
            MethodResponseType.INFO: "info"
        }
        return {
            "type": mapping[self]
        }
    
    @classmethod
    def from_json5(cls, j: Any) -> Self:
        if not isinstance(j, dict):
            raise ValueError(f"invalid method response type, expected keyword 'type', got {j}")
        
        t = j["type"].lower()
        if t == "ok":
            return cls(MethodResponseType.OK)
        elif t in {"err", "error"}:
            return cls(MethodResponseType.ERR)
        elif t in {"info"}:
            return cls(MethodResponseType.INFO)
        else:
            raise ValueError(f"invalid method response type {t}, must be one of ['ok', 'err', 'info']")
    
    def to_proto(self) -> proto.MethodResponseType:
        return self.value # type: ignore
    
    @classmethod
    def from_proto(cls, p: proto.MethodResponseType):
        return cls(int(p))