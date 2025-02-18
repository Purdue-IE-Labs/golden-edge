from typing import Any
from gedge.edge.data_type import DataType
from gedge.edge.gtypes import TagWriteHandler, Type
from gedge import proto
from gedge.edge.prop import Prop, Props

class WriteResponse:
    def __init__(self, code: int, success: bool, props: Props):
        self.code = code
        self.success = success
        self.props: Props = props
    
    def to_proto(self) -> proto.WriteResponse:
        code = self.code
        success = self.success
        props = self.props.to_proto()
        return proto.WriteResponse(code=code, success=success, props=props)

    @classmethod
    def from_proto(cls, response: proto.WriteResponse):
        code = response.code
        success = response.success
        props = Props.from_proto(response.props)
        return WriteResponse(code, success, props)


class Tag:
    def __init__(self, path: str, type: DataType, props: Props, writable: bool, responses: list[WriteResponse], write_handler: TagWriteHandler):
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
    
    def writable(self, write_handler: TagWriteHandler = None, responses: list[tuple[int, bool, dict[str, Any]]] = []):
        self._writable = True
        self.write_handler = write_handler
        for tup in responses:
            self.add_write_response(tup[0], tup[1], tup[2])
        return self
    
    def add_write_response(self, code: int, success: bool, props: Prop = {}):
        response = WriteResponse(code, success, props)
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

if __name__ == "__main__":
    print("list int")
    t = Tag("my_tag", list[int], props={"joe": "buck"})
    print(t.type)
    print(f"\nDatatype.LIST_BOOL")
    t = Tag("my_tag", proto.DataType.LIST_BOOL, props={"joe": "buck"})
    print(t.type)
    print(f"\nint")
    t = Tag("my_tag", int, props={"joe": "buck"})
    print(t.type)
    t = Tag("my_tag", list[float])
    t = Tag("my_tag", type=list[str])
    t = Tag("my_tag", proto.DataType.LIST_LONG)
    print(t.type)
