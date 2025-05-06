from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto

from gedge.node import codes
from gedge.py_proto.data_model import DataItem
from gedge.py_proto.data_model_config import DataItemConfig
from gedge.py_proto.props import Prop
from gedge import proto
from typing import Any, Self, TYPE_CHECKING

from gedge.py_proto.conversions import list_from_proto, list_to_proto, props_from_json5

if TYPE_CHECKING:
    from gedge.node.gtypes import TagValue

# CONFIG object
@dataclass
class ResponseConfig:
    code: int
    type: ResponseType
    body: list[DataItemConfig]
    props: list[Prop]
    
    def to_proto(self) -> proto.ResponseConfig:
        props = list_to_proto(self.props)
        body = list_to_proto(self.body)
        type = self.type.to_proto()
        return proto.ResponseConfig(code=self.code, type=type, body=body, props=props)

    @classmethod
    def from_proto(cls, proto: proto.ResponseConfig) -> Self:
        type = ResponseType.from_proto(proto.type)
        props = list_from_proto(Prop, proto.props)
        body = list_from_proto(DataItemConfig, proto.body)
        return cls(proto.code, type, body, props)
    
    @classmethod
    def from_json5(cls, j: Any) -> Self:
        if not isinstance(j, dict):
            raise ValueError(f"Invalid method repsonse type, expected dict, got {j}")
        
        if "code" not in j:
            raise LookupError(f"Method response must include 'code', got {j}")
        if "type" not in j:
            raise LookupError(f"Method response must include 'type', got {j}")
        code = int(j["code"])

        props = props_from_json5(j["props"])
        body = [DataItemConfig.from_json5(b) for b in j.get("body", [])]
        type = ResponseType.from_json5(j)
        return cls(code, type, body, props)
    
    def is_ok(self) -> bool:
        return self.type == ResponseType.OK
    
    def is_err(self) -> bool:
        return self.type == ResponseType.ERR
    
    def is_info(self) -> bool:
        return self.type == ResponseType.INFO
    
    def body_proto_to_value(self, body: dict[str, proto.DataItem]) -> dict[str, TagValue]:
        new_body: dict[str, TagValue] = {}
        for key, value in body.items():
            body_config = [c for c in self.body if c.path == key][0]
            # new_body[key] = DataItem.from_proto(value, body_config).to_value()
            new_body[key] = DataItem.proto_to_py(value, body_config)
        return new_body
    
    def body_value_to_proto(self, body: dict[str, TagValue]) -> dict[str, proto.DataItem]:
        new_body: dict[str, proto.DataItem] = {}
        for key, value in body.items():
            body_config = [c for c in self.body if c.path == key][0]
            # new_body[key] = DataItem.from_value(value, body_config).to_proto()
            new_body[key] = DataItem.py_to_proto(value, body_config)
        return new_body
    
def get_response_config(code: int, responses: list[ResponseConfig]) -> ResponseConfig:
    res = {r.code: r for r in responses}
    if code not in res:
        return codes.config_from_predefined_code(code)
    r = res[code]
    return r

class ResponseType(Enum):
    OK = proto.ResponseType.OK
    ERR = auto()
    INFO = auto()

    def to_json5(self) -> dict:
        mapping = {
            ResponseType.OK: "ok",
            ResponseType.ERR: "err",
            ResponseType.INFO: "info"
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
            return cls(ResponseType.OK)
        elif t in {"err", "error"}:
            return cls(ResponseType.ERR)
        elif t in {"info"}:
            return cls(ResponseType.INFO)
        else:
            raise ValueError(f"invalid method response type {t}, must be one of ['ok', 'err', 'info']")
    
    def to_proto(self) -> proto.ResponseType:
        return self.value # type: ignore
    
    @classmethod
    def from_proto(cls, p: proto.ResponseType):
        return cls(int(p))