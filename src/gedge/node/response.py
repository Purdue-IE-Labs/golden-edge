from gedge.edge.data_type import DataType
from gedge.edge.prop import Prop, Props
from gedge import proto
from typing import Any, Callable, Self
from gedge.edge.types import Type


class Response:
    def __init__(self, code: int, success: bool, props: dict[str, Any], body: dict[str, Type], final: bool):
        self.code = code
        self.success = success
        self.props = Props.from_value(props)
        self.body = {key:DataType(value) for key, value in body.items()}
        self.final = final
    
    def to_proto(self) -> proto.Response:
        body = {key:value.to_proto() for key, value in self.body.items()}
        return proto.Response(code=self.code, success=self.success, props=self.props.to_proto(), body=body, final=self.final)

    @classmethod
    def from_proto(self, proto: proto.Response) -> Self:
        '''
        TODO: There is a recurring problem here. For the props field, the proto message variant of the field is of type dict[str, proto.Prop]
        Ideally, we could just call Props.from_proto() to get that to be of type dict[str, Prop]. However, this class 
        accepts a dict[str, Any] and then coerces that into a dict[str, Prop]. Thus, there is no clean and easy way 
        to go straight from dict[str, proto.Prop] to dict[str, Any], and even if there was, this would be unproductive 
        because the constructor of this class already converts from dict[str, Any] to dict[str, Prop]

        Solution:
            1. This class could accept either a dict[str, Any] or a dict[str, Prop] (which is the same as Props), so that in Response.from_proto() we could 
            just call Props.from_proto() and pass that into the constructor of Response.
            2. Only add from_proto() to classes as needed. We may never need it in this function because this is part of the META message 
            which is just going into the historian 

        I don't like the idea of the user interacting directly with the Protobuf message class because it's a little messy
        '''
        return Response(proto.code, proto.success, proto.props)
    
    def add_prop(self, key: str, value: Any):
        self.props.add_prop(key, value)
    
    def add_body_item(self, key: str, value: Type):
        self.body[key] = DataType(value)