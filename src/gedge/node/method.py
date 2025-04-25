from __future__ import annotations
from dataclasses import dataclass

from gedge.node.body import Body
from gedge.node.data_type import DataType
from gedge.node.param import Param
from gedge.node.prop import Props
from gedge import proto
from gedge.node.method_response import MethodResponse

from typing import Any, Self, TYPE_CHECKING
if TYPE_CHECKING:
    from gedge.node.gtypes import TagValue, Type, MethodHandler

@dataclass
class Method:
    path: str
    handler: MethodHandler | None
    props: Props
    params: dict[str, Param]
    responses: list[MethodResponse]

    def to_proto(self) -> proto.Method:
        '''
        Creates a proto object of the current Method object

        Args:
            None: None

        Returns:
            proto.Method: The newly created Proto object

        **Example**::

            properties = {
                'method0': 'yeah'
            }
            param = Param(DataType.INT, Props.from_value(properties))

            methodResponse = MethodResponse(30, Props.from_value(properties), [])

            method = Method("test/path", None, Props.from_value(properties), {'param0': param}, [])

            protoMethod = method.to_proto()
        '''
        params = {key:value.to_proto() for key, value in self.params.items()}
        responses = [r.to_proto() for r in self.responses]
        props = self.props.to_proto()
        return proto.Method(path=self.path, props=props, params=params, responses=responses)

    @classmethod
    def from_proto(cls, proto: proto.Method) -> Self:
        '''
        Creates a Method object from the passed proto.Method

        Args:
            proto (proto.Method): The proto object that the Method is being created from

        Returns:
            Method: The created Method object

        **Example**::

            properties = {
                'method0': 'yeah'
            }
            param = Param(DataType.INT, Props.from_value(properties))

            methodResponse = MethodResponse(30, Props.from_value(properties), [])

            method = Method("test/path", None, Props.from_value(properties), {'param0': param}, [])

            protoMethod = method.to_proto()

            newMethod = Method.from_proto(protoMethod)
        '''
        props = Props.from_proto(proto.props)
        params = {key:Param.from_proto(value) for key, value in proto.params.items()}
        responses = [MethodResponse.from_proto(r) for r in proto.responses]
        return cls(proto.path, None, props, params, responses)
    
    @classmethod
    def from_json5(cls, json: Any) -> Self:
        '''
        Creates a Method object from the passed json5 

        Args:
            json (Any): The json5 beig used to create the Method object

        Returns:
            Method: The created Method object
        '''
        if not isinstance(json, dict):
            raise ValueError(f"Invalid method {json}")
        
        if "path" not in json:
            raise LookupError(f"Method must have path, {json}")
        path = json["path"]
        props = Props.from_json5(json.get("props", {}))

        params = {}
        if "params" in json and isinstance(json["params"], dict):
            params = {key:Param.from_json5(value) for key, value in json["params"].items()}
        
        responses = []
        if "responses" in json:
            for response in json["responses"]:
                r = MethodResponse.from_json5(response)
                responses.append(r)

        return cls(path, None, props, params, responses)

    def add_response(self, code: int, props: dict[str, TagValue] = {}, body: dict[str, Body] = {}):
        '''
        Adds a new response to the current Method

        Args:
            code (int): The code of the response
            props (dict[str, TagValue]): *Optional* Properties of the new response
            body (dict[str, body]): *Optional* Body of the new response

        Returns:
            MethodResponse: The newly created response

        **Example**::

            properties = {
                'method0': 'yeah'
            }
            
            param = Param(DataType.INT, Props.from_value(properties))

            methodResponse = MethodResponse(30, Props.from_value(properties), [])

            method = Method("test/path", None, Props.from_value(properties), {'param0': param}, [])

            assert method.responses == []

            method.add_response(20, properties, (...)))
        '''
        props_ = Props.from_value(props)
        body_ = body
        response = MethodResponse(code, props_, body_)
        self.responses.append(response)
        return response
