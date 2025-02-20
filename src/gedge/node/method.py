from gedge.edge.data_type import DataType
from gedge.edge.gtypes import TagValue, Type
from gedge.edge.prop import Props
from gedge.node.query import Query
from gedge import proto
from typing import Self, Callable
from gedge.node.response import Response

MethodType = Callable[[Query], None]

class Method:
    def __init__(self, path: str, handler: MethodType, props: Props, parameters: dict[str, DataType], responses: list[Response]):
        self.path = path
        self.handler = handler
        self.props = props
        self.parameters = parameters
        self.responses = responses
    
    def to_proto(self) -> proto.Method:
        params = {key:value.to_proto() for key, value in self.parameters.items()}
        responses = [r.to_proto() for r in self.responses]
        props = self.props.to_proto()
        return proto.Method(path=self.path, props=props, parameters=params, responses=responses)

    @classmethod
    def from_proto(cls, proto: proto.Method) -> Self:
        props = Props.from_proto(proto.props)
        parameters = {key:DataType.from_proto(value) for key, value in proto.parameters.items()}
        responses = [Response.from_proto(r) for r in proto.responses]
        return Method(proto.path, None, props, parameters, responses)

    def add_params(self, **kwargs: Type):
        for key, value in kwargs.items():
            self.parameters[key] = DataType.from_type(value)

    def add_response(self, code: int, success: bool, props: dict[str, TagValue] = {}, body: dict[str, Type] = {}, final: bool = False): 
        props = Props.from_value(props)
        body = {key:DataType.from_type(value) for key, value in body.items()}
        response = Response(code, success, props, body, final)
        self.responses.append(response)
        return response

    def __repr__(self):
        return f"Method(path={self.path}, props={self.props}, parameters={self.parameters}, responses={self.responses})"
