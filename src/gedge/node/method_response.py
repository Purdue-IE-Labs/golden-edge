from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto

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
            raise LookupError(f"Method response must include 'type' (which is one of ['ok', 'err', 'info']), got {j}")
        code = int(j["code"])

        props = props_from_json5(j.get("props", {}))
        body = [DataItemConfig.from_json5(b) for b in j.get("body", [])]
        type = ResponseType.from_json5(j)
        return cls(code, type, body, props)
    
    def is_ok(self) -> bool:
        return self.type == ResponseType.OK
    
    def is_err(self) -> bool:
        return self.type == ResponseType.ERR
    
    def is_info(self) -> bool:
        return self.type == ResponseType.INFO
    
    def body_proto_to_value(self, proto: dict[str, proto.DataItem]) -> dict[str, TagValue]:
        config = {i.path: i for i in self.body}
        body: dict[str, TagValue] = {k: DataItem.proto_to_py(v, config[k]) for k, v in proto.items()}
        return body
    
    def body_value_to_proto(self, value: dict[str, TagValue]) -> dict[str, proto.DataItem]:
        config = {i.path: i for i in self.body}
        body: dict[str, proto.DataItem] = {k: DataItem.py_to_proto(v, config[k]) for k, v in value.items()}
        return body
    
def get_response_config(code: int, responses: list[ResponseConfig]) -> ResponseConfig:
    from gedge.node import codes
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
        elif t == "info":
            return cls(ResponseType.INFO)
        else:
            raise ValueError(f"invalid method response type {t}, must be one of ['ok', 'err', 'info']")
    
    def to_proto(self) -> proto.ResponseType:
        return self.value # type: ignore
    
    @classmethod
    def from_proto(cls, p: proto.ResponseType):
        return cls(int(p))