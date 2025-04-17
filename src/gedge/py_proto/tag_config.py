from __future__ import annotations
from dataclasses import dataclass, field
from tkinter import N

from gedge import proto
from gedge.py_proto.props import Props

from typing import Any, Self, TYPE_CHECKING
if TYPE_CHECKING:
    from gedge.py_proto.data_model_config import DataModelItemConfig
    from gedge.node.gtypes import TagWriteHandler

@dataclass
class TagWriteResponseConfig:
    code: int
    props: Props
    
    def to_proto(self) -> proto.TagWriteResponseConfig:
        code = self.code
        props = self.props.to_proto()
        return proto.TagWriteResponseConfig(code=code, props=props)

    @classmethod
    def from_proto(cls, response: proto.TagWriteResponseConfig) -> Self:
        code = response.code
        props = Props.from_proto(response.props)
        return cls(code, props)
    
    @classmethod
    def from_json5(cls, json: Any) -> Self:
        if isinstance(json, int):
            return cls(json, Props.empty())
        if not isinstance(json, dict):
            raise ValueError(f"invalid write response {json}")
        
        if "code" not in json:
            raise LookupError(f"Tag write response must include code")
        code = int(json["code"])
        props = Props.from_json5(json.get("props", {}))
        return cls(code, props)
    

@dataclass
class TagConfig:
    config: DataModelItemConfig
    _writable: bool
    responses: list[TagWriteResponseConfig]
    write_handle: TagWriteHandler | None = field(default=None)

    def to_proto(self) -> proto.TagConfig:
        config = self.config.to_proto()
        responses = [r.to_proto() for r in self.responses]
        return proto.TagConfig(config=config, writable=self._writable, responses=responses)

    @classmethod
    def from_proto(cls, tag: proto.TagConfig) -> Self:
        from gedge.py_proto.data_model_config import DataModelItemConfig
        config = DataModelItemConfig.from_proto(tag.config)
        responses = [TagWriteResponseConfig.from_proto(wr) for wr in tag.responses]
        t = cls(config, tag.writable, responses)
        return t
    
    @classmethod
    def from_json5(cls, json: Any):
        if not isinstance(json, dict):
            raise ValueError(f"invalid tag, tag must be a dict")
        
        if not("path" in json and "type" in json):
            raise LookupError(f"tag must include both a path and a type: {json}")
        config = DataModelItemConfig.from_json5(json)
        writable = json.get("writable", False)
        responses = []
        for response in json.get("responses", []):
            r = TagWriteResponseConfig.from_json5(response)
            responses.append(r)

        return cls(config, writable, responses)
    
    def writable(self, write_handler: TagWriteHandler, responses: list[tuple[int, dict[str, Any]]] = []):
        self._writable = True
        self.write_handler = write_handler
        for tup in responses:
            self.add_write_response(tup[0], Props.from_value(tup[1]))
        return self
    
    def is_writable(self):
        return self._writable
    
    def add_write_response(self, code: int, props: Props = Props.empty()):
        response = TagWriteResponseConfig(code, props)
        if len([x for x in self.responses if response.code == x.code]) > 0:
            raise ValueError(f"Tag write responses must have unique codes, and code {response.code} is not unique")
        self.responses.append(response)
    
    def add_write_handler(self, handler: TagWriteHandler):
        self.write_handler = handler
    
    def add_props(self, p: dict[str, Any]):
        for name, value in p.items():
            self.add_prop(name, value)
    
    def add_prop(self, key: str, value: Any):
        self.config.config.props.add_prop(key, value)
