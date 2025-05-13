from __future__ import annotations
from dataclasses import dataclass

from gedge.node.data_type import DataType
from gedge import proto
from gedge.node.prop import Props

from typing import Any, Self, TYPE_CHECKING
if TYPE_CHECKING: # pragma: no cover
    from gedge.node.gtypes import TagWriteHandler

@dataclass
class WriteResponse:
    code: int
    props: Props
    
    def to_proto(self) -> proto.WriteResponse:
        code = self.code
        props = self.props.to_proto()
        return proto.WriteResponse(code=code, props=props)

    @classmethod
    def from_proto(cls, response: proto.WriteResponse) -> Self:
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
    

class Tag:
    def __init__(self, path: str, type: DataType, props: Props, writable: bool, responses: list[WriteResponse], write_handler: TagWriteHandler | None):
        self.path = path
        self.type = type
        self.props = props
        self._writable = writable
        self.responses = responses
        self.write_handler = write_handler
    
    def to_proto(self) -> proto.Tag:
        type = self.type.to_proto()
        props = self.props.to_proto()
        responses = [r.to_proto() for r in self.responses]
        return proto.Tag(path=self.path, type=type, props=props, writable=self._writable, responses=responses)

    @classmethod
    def from_proto(cls, tag: proto.Tag):
        type = DataType.from_proto(tag.type)
        props = Props.from_proto(tag.props)
        responses = [WriteResponse.from_proto(wr) for wr in tag.responses]
        t = Tag(tag.path, type, props, tag.writable, responses, None)
        return t
    
    @classmethod
    def from_json5(cls, json: Any):
        if not isinstance(json, dict):
            raise ValueError(f"invalid tag, tag must be a dict")
        
        if not("path" in json and "type" in json):
            raise LookupError(f"tag must include both a path and a type: {json}")
        path = json["path"]
        type = DataType.from_json5(json["type"])
        props = Props.from_json5(json.get("props", {}))
        writable = json.get("writable", False)
        responses = []
        for response in json.get("responses", []):
            r = WriteResponse.from_json5(response)
            responses.append(r)

        return cls(path, type, props, writable, responses, write_handler=None)
    
    def writable(self, write_handler: TagWriteHandler, responses: list[tuple[int, dict[str, Any]]] = []):
        self._writable = True
        self.write_handler = write_handler
        for tup in responses:
            self.add_write_response(tup[0], Props.from_value(tup[1]))
        return self
    
    def is_writable(self):
        return self._writable
    
    def add_write_response(self, code: int, props: Props = Props.empty()):
        response = WriteResponse(code, props)
        if len([x for x in self.responses if response.code == x.code]) > 0:
            raise ValueError(f"Tag write responses must have unique codes, and code {response.code} is not unique")
        self.responses.append(response)
    
    def add_write_handler(self, handler: TagWriteHandler):
        self.write_handler = handler
    
    def add_props(self, p: dict[str, Any]):
        for name, value in p.items():
            self.add_prop(name, value)
    
    def add_prop(self, key: str, value: Any):
        self.props.add_prop(key, value)
    
    def __repr__(self) -> str:
        res = f"Tag(path={self.path}, type={self.type}, props={self.props}, writable={self._writable}"
        if self._writable:
            res = f"{res}, {self.responses}"
        return f"{res})"
