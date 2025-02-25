from gedge.edge.data_type import DataType
from gedge.edge.prop import Props
from gedge import proto
from typing import Any, Self
from gedge.edge.gtypes import Type


class Response:
    def __init__(self, code: int, props: Props, body: dict[str, DataType]):
        self.code = code
        self.props = props
        self.body = body
    
    def to_proto(self) -> proto.Response:
        props = self.props.to_proto()
        body = {key:value.to_proto() for key, value in self.body.items()}
        return proto.Response(code=self.code, props=props, body=body)

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
        Current solution is for this class to only accept a Prop
        '''
        props = Props.from_proto(proto.props)
        body = {key:DataType.from_proto(value) for key, value in proto.body.items()}
        return Response(proto.code, props, body)
    
    def add_prop(self, key: str, value: Any):
        self.props.add_prop(key, value)
    
    def add_body(self, **kwargs: Type):
        for key, value in kwargs.items():
            self.body[key] = DataType.from_type(value)
    
    def __repr__(self):
        return f"Response(code={self.code}, body={self.body})"
    