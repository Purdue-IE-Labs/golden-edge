from gedge.edge.data_type import DataType
from gedge.edge.prop import Props
from gedge.node.query import Query
from gedge import proto
from typing import Any, Callable, Self
from gedge.edge.types import Type
from gedge.node.response import Response


class Method:
    def __init__(self, path: str, handler: Callable[[Query], None], props: dict[str, Any] | Props, parameters: dict[str, Type], responses: list[Response]):
        self.path = path
        self.handler = handler
        if not isinstance(props, Props):
            props = Props.from_value(props)
        self.props = props
        self.parameters = {key:DataType(value) for key, value in parameters.items()}
        self.responses = responses
    
    def to_proto(self) -> proto.Method:
        print(self.parameters)
        params = {key:value.to_proto() for key, value in self.parameters.items()}
        print(params)
        responses = [r.to_proto() for r in self.responses]
        return proto.Method(path=self.path, props=self.props.to_proto(), parameters=params, responses=responses)

    @classmethod
    def from_proto(cls, proto: proto.Method) -> Self:
        return Method(proto.path, None, Props.from_proto(proto.props), proto.parameters, proto.responses)

    def add_params(self, **kwargs):
        for key, value in kwargs.items():
            self.parameters[key] = DataType(value)
    
    def add_responses(self, responses: list[Response]):
        for r in responses:
            self.add_response(r)

    def add_response(self, response: Response): 
        self.responses.append(response)

