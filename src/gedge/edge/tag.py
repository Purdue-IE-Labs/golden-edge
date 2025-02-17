from typing import Any, Callable, Dict, Union, TypeAlias
from types import GenericAlias
from gedge.edge.data_type import DataType
from gedge.edge.types import TagWriteHandler
from gedge import proto
from gedge.edge.prop import Prop, Props
from gedge.comm.keys import NodeKeySpace

class WriteResponse:
    def __init__(self, code: int, success: bool, props: dict[str, Any] = {}):
        self.code = code
        self.success = success
        self.props: Props = Props.from_value(props)
    
    def to_proto(self) -> proto.WriteResponse:
        return proto.WriteResponse(code=self.code, success=self.success, props=self.props.to_proto())

    @classmethod
    def from_proto(cls, response: proto.WriteResponse):
        return WriteResponse(response.code, response.success, Props.from_proto(response.props))


class Tag:
    def __init__(self, path: str, type: int | Any, props: dict[str, Any], writable: bool, responses: list[WriteResponse], write_handler: TagWriteHandler):
        self.path = path
        self.type = DataType(type)
        self.props = Props.from_value(props)
        self._writable = writable
        self.responses = responses
        self.write_handler = write_handler
    
    def to_proto(self) -> proto.Tag:
        responses = [r.to_proto() for r in self.responses]
        return proto.Tag(path=self.path, type=self.type.to_proto(), props=self.props.to_proto(), writable=self._writable, responses=responses)

    @classmethod
    def from_proto(cls, tag: proto.Tag):
        t = Tag(tag.path, tag.type, {}, tag.writable, tag.responses, None)
        t.props = dict(tag.props)
        return t
    
    def writable(self, write_handler: TagWriteHandler = None, responses: list[tuple[int, bool, dict[str, Any]]] = []):
        self._writable = True
        self.write_handler = write_handler
        for tup in responses:
            self.add_response_type(tup[0], tup[1], tup[2])
        return self
    
    def add_response_type(self, code: int, success: bool, props: dict[str, Any] = {}):
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

    def convert(self, value: Any, type: int = None) -> proto.TagData:
        if not type:
           type = self.type
        return convert(value, type)

    @staticmethod
    def from_tag_data(tag_data: proto.TagData, type: int) -> Any:
        match type:
            case proto.DataType.INT:
                return int(tag_data.int_data)
            case proto.DataType.LONG:
                return int(tag_data.long_data)
            case proto.DataType.FLOAT:
                return float(tag_data.float_data)
            case proto.DataType.STRING:
                return str(tag_data.string_data)
            case proto.DataType.BOOL:
                return bool(tag_data.bool_data)
            case proto.DataType.LIST_INT:
                return list(tag_data.list_int_data.list)
            case proto.DataType.LIST_LONG:
                return list(tag_data.list_long_data.list)
            case proto.DataType.LIST_FLOAT:
                return list(tag_data.list_float_data.list)
            case proto.DataType.LIST_STRING:
                return list(tag_data.list_string_data.list)
            case proto.DataType.LIST_BOOL:
                return list(tag_data.list_bool_data.list)
        raise ValueError(f"Cannot convert tag to type {type}")

def convert(value: Any, type: int) -> proto.TagData:
    # Use the type of a TagData to convert to a TagData from a python type
    tag_data = proto.TagData()
    match type:
        case proto.DataType.INT:
            tag_data.int_data = int(value)
        case proto.DataType.LONG:
            tag_data.long_data = int(value)
        case proto.DataType.FLOAT:
            tag_data.float_data = float(value)
        case proto.DataType.STRING:
            tag_data.string_data = str(value)
        case proto.DataType.BOOL:
            tag_data.bool_data = bool(value)
        case proto.DataType.LIST_INT:
            tag_data.list_int_data.list.extend(list([int(x) for x in value]))
        case proto.DataType.LIST_LONG:
            tag_data.list_long_data.list.extend(list([int(x) for x in value]))
        case proto.DataType.LIST_FLOAT:
            tag_data.list_float_data.list.extend(list([float(x) for x in value]))
        case proto.DataType.LIST_STRING:
            tag_data.list_string_data.list.extend(list([str(x) for x in value]))
        case proto.DataType.LIST_BOOL:
            tag_data.list_bool_data.list.extend(list([bool(x) for x in value]))
        case _:
            raise ValueError(f"Unknown tag type {type}")
    return tag_data

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
