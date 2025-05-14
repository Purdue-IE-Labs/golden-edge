import pytest
import gedge
from gedge.node.method import Method
from gedge.node.prop import Props
from gedge.node.param import Param
from gedge.node.data_type import DataType
from gedge.node.method_response import MethodResponse
from gedge.node.body import Body

class TestMethod:
    class TestSanity:
        def test_to_proto(self):
            properties = {
                'method0': 'yeah'
            }
            param = Param(DataType.INT, Props.from_value(properties))

            methodResponse = MethodResponse(30, Props.from_value(properties), [])

            method = Method("test/path", None, Props.from_value(properties), {'param0': param}, [])

            protoMethod = method.to_proto()

            assert protoMethod.path == method.path
            assert protoMethod.props == method.props.to_proto()
            # assert protoMethod.params == method.params
            assert protoMethod.responses == method.responses

        def test_from_proto(self):
            properties = {
                'method0': 'yeah'
            }
            param = Param(DataType.INT, Props.from_value(properties))

            methodResponse = MethodResponse(30, Props.from_value(properties), [])

            method = Method("test/path", None, Props.from_value(properties), {'param0': param}, [])

            protoMethod = method.to_proto()

            newMethod = Method.from_proto(protoMethod)

            assert newMethod.props.to_value() == method.props.to_value()
            assert str(newMethod.params) == str(method.params)
            assert newMethod.responses == method.responses

        def test_from_json5(self):
            json = {
                "path": "call/method",
                "type": "int",
                "params": {
                    "name": {
                        "type": "string",
                        "props": {
                        "desc": "name of the project"
                        }
                    },
                    "speed": "int",
                },
                "responses": [
                    {
                        "code": 200,
                        "body": {
                            "res1": {
                                "type": "int",
                                "props": {
                                    "desc": "a body item named res1"
                                }
                            }
                        },
                        "props": {
                            "desc": "successfully executed method"
                        }
                    },
                    {
                        "code": 400,
                        "body": {
                            "res1": "int",
                        },
                        "props": {
                            "desc": "speed must be in range [0, 100]"
                        }
                    },
                    {
                        "code": 401,
                        "props": {
                            "desc": "name cannot be longer than 30 characters"
                        }
                    }
                ],
                "props": {
                    "desc": "testing method calls"
                },
            }

            method = Method.from_json5(json)

            assert method.path == "call/method"
            assert len(method.responses) == 3

        def test_add_response(self):
            properties = {
                'method0': 'yeah'
            }
            param = Param(DataType.INT, Props.from_value(properties))

            methodResponse = MethodResponse(30, Props.from_value(properties), [])

            method = Method("test/path", None, Props.from_value(properties), {'param0': param}, [])

            assert method.responses == []

            method.add_response(20, properties, None)

            assert method.responses != []

    class TestEmpty:
        def test_to_proto(self):
            method = Method("", None, Props.from_value({}), {}, [])

            methodProto = method.to_proto()

            assert methodProto.props == method.props.to_proto()
            assert methodProto.params == method.params
            assert methodProto.responses == method.responses

        def test_from_proto(self):
            method = Method("", None, Props.from_value({}), {}, [])

            methodProto = method.to_proto()
        
            newMethod = Method.from_proto(methodProto)

            assert newMethod.props.to_value() == method.props.to_value()
            assert newMethod.params == method.params
            assert newMethod.responses == method.responses

        def test_from_json5(self):
            with pytest.raises(ValueError, match="Invalid method None"):
                Method.from_json5(None)

        def test_add_response(self):
            method = Method("", None, Props.from_value({}), {}, [])

            assert method.responses == []
        
            method.add_response(None, {}, {})

            assert str(method.responses) == str([MethodResponse(None, {}, {})])

        def test_json5_wrong_type(self):
            json = 5

            with pytest.raises(ValueError, match="Invalid method 5"):
                method = Method.from_json5(json)

        def test_json5_no_path(self):
            json = {
                "type": "int",
                "params": {
                    "name": {
                        "type": "string",
                        "props": {
                        "desc": "name of the project"
                        }
                    },
                    "speed": "int",
                },
                "responses": [
                    {
                        "code": 200,
                        "body": {
                            "res1": {
                                "type": "int",
                                "props": {
                                    "desc": "a body item named res1"
                                }
                            }
                        },
                        "props": {
                            "desc": "successfully executed method"
                        }
                    },
                    {
                        "code": 400,
                        "body": {
                            "res1": "int",
                        },
                        "props": {
                            "desc": "speed must be in range [0, 100]"
                        }
                    },
                    {
                        "code": 401,
                        "props": {
                            "desc": "name cannot be longer than 30 characters"
                        }
                    }
                ],
                "props": {
                    "desc": "testing method calls"
                },
            }

            with pytest.raises(LookupError):
                method = Method.from_json5(json)

class TestMethodResponse:
    class TestSanity:
        def test_init(self):
            properties = {
                'method0': 'yeah'
            }
            methodResponse = MethodResponse(10, Props.from_value(properties), {'body0': Body(DataType.INT, Props.from_value(properties))})

            assert methodResponse.code == 10
            assert methodResponse.props.to_value() == properties
            assert methodResponse.body.get('body0').to_proto() == Body(DataType.INT, Props.from_value(properties)).to_proto()
        
        def test_to_proto(self):
            properties = {
                'method0': 'yeah'
            }
            methodResponse = MethodResponse(10, Props.from_value(properties), {'body0': Body(DataType.INT, Props.from_value(properties))})

            methodResponseProto = methodResponse.to_proto()

            assert methodResponseProto.code == methodResponse.code
            assert methodResponseProto.props == methodResponse.props.to_proto()
            tempBody = {key:value.to_proto() for key, value in methodResponse.body.items()}
            assert methodResponseProto.body == tempBody
        
        def test_from_proto(self):
            properties = {
                'method0': 'yeah'
            }
            methodResponse = MethodResponse(10, Props.from_value(properties), {'body0': Body(DataType.INT, Props.from_value(properties))})

            methodResponseProto = methodResponse.to_proto()

            newMethodResponse = MethodResponse.from_proto(methodResponseProto)

            assert methodResponse.code == newMethodResponse.code
            assert methodResponse.props.to_value() == newMethodResponse.props.to_value()
            assert methodResponse.body.items() == methodResponse.body.items()

        def test_from_json5(self):
            json5 = {
                'code': 200,
                'body': {
                    'res1': {
                        'type': "int",
                        'props': {
                                    'desc': "a body item named res1"
                        }
                    }
                },
                'props': {
                    'desc': "successfully executed method"
                }
            }

            methodReponse = MethodResponse.from_json5(json5)
            assert methodReponse.props.to_value() == json5.get("props")
            # assert methodReponse.body
            assert methodReponse.code == json5.get("code")

        def test_add_prop(self):
            json5 = {
                'code': 200,
                'body': {
                    'res1': {
                        'type': "int",
                        'props': {
                                    'desc': "a body item named res1"
                        }
                    }
                },
                'props': {
                    'desc': "successfully executed method"
                }
            }

            methodResponse = MethodResponse.from_json5(json5)

            expectedProps = json5.get("props")

            assert methodResponse.props.to_value() == expectedProps

            methodResponse.add_prop('another desc', 10)

            assert str(methodResponse.props.to_value()) == "{'desc': 'successfully executed method', 'another desc': 10}"

    class TestJSON5:
        def test_int(self):
            methodResponse = MethodResponse.from_json5(20)

            assert methodResponse.code == 20
            assert methodResponse.props.to_value() == {}
            assert methodResponse.body == {}

        def test_fail(self):
            with pytest.raises(ValueError, match="Invalid method response type, Yeah dawg"):
                methodResponse = MethodResponse.from_json5("Yeah dawg")

        def test_no_code(self):
            json5 = {
                'body': {
                    'res1': {
                        'type': "int",
                        'props': {
                                    'desc': "a body item named res1"
                        }
                    }
                },
                'props': {
                    'desc': "successfully executed method"
                }
            }
            with pytest.raises(LookupError, match="Method response must include code, {'body': {'res1': {'type': 'int', 'props': {'desc': 'a body item named res1'}}}, 'props': {'desc': 'successfully executed method'}}"):
                methodReponse = MethodResponse.from_json5(json5)

        def test_invalid_body(self):
            json5 = {
                'code': 200,
                'body': 'not a dict',
                'props': {
                    'desc': "successfully executed method"
                }
            }

            with pytest.raises(ValueError, match="The passed body is not a dict object: not a dict"):
                methodResponse = MethodResponse.from_json5(json5)

        def test_invalid_props(self):
            json5 = {
                'code': 200,
                'body': {
                    'res1': {
                        'type': "int",
                        'props': {
                                    'desc': "a body item named res1"
                        }
                    }
                },
                'props': 'not a dict'
            }

            with pytest.raises(ValueError, match="invalid props not a dict"):
                methodResponse = MethodResponse.from_json5(json5)

        @pytest.mark.parametrize("code", {
            (200.0),
            (True),
            ("Hi"),
            (b"123")
        })
        def test_code_not_an_int(self, code):
            json5 = {
                'code': code
            }
            
            if (isinstance(code, str)):
                with pytest.raises(ValueError, match=f"The passed code cannot be converted to an integer: {code}"):
                    MethodResponse.from_json5(json5)
            else:
                methodResponse = MethodResponse.from_json5(json5)

                assert methodResponse.code == int(code)
        
        def test_big_body(self):
            body = {
                'res1': Body(DataType.INT, Props.empty()),
                'res2': Body(DataType.STRING, Props.empty()),
            }
            response = MethodResponse(200, Props.empty(), body)
            proto = response.to_proto()
            assert len(proto.body) == 2

    class TestAddProp:
        def test_overwrite(self):
            methodResponse = MethodResponse.from_json5({'code': 200, 'props': {'test0': 'test desc'}})
            methodResponse.add_prop("test0", "different desc")

            assert str(methodResponse.props.to_value()) == "{'test0': 'different desc'}"
        
        @pytest.mark.parametrize("key, value", [
            ("int_prop", 20),
            ("float_prop", 3.0),
            ("bool_prop", True),
            ("list_prop", [1, 2, 3]),
        ])
        def test_diff_types(self, key, value):
            methodResponse = MethodResponse(200, Props.empty(), {})

            methodResponse.add_prop(key, value)

            props = methodResponse.props.to_value()

            assert props[key] == value
        
        def test_empty_key(self):
            methodResponse = MethodResponse(200, Props.empty(), {})

            methodResponse.add_prop("", 200)

            props = methodResponse.props.to_value()

            assert "" in props
        
        def test_non_str_key(self):
            methodResponse = MethodResponse(200, Props.empty(), {})
            
            methodResponse.add_prop(123, "hi")
            
            assert methodResponse.props.to_value()[123] == "hi"
        
        def test_big_value(self):
            methodResponse = MethodResponse(200, Props.empty(), {})
            
            big_value = "x" * 10_000
            
            methodResponse.add_prop("big", big_value)
            
            assert methodResponse.props.to_value()["big"] == big_value

    class TestToProto:
        def test_empty(self):
            methodResponse = MethodResponse(200, Props.empty(), {})
            proto = methodResponse.to_proto()
            assert proto.body == {}
            assert proto.props == Props.empty().to_proto()
            assert proto.code == 200

        def test_unicode(self):
            props = Props.from_json5({"message": "こんにちは世界"})  # Hello World in Japanese
            body = {}
            methodResponse = MethodResponse(200, props, body)
            proto = methodResponse.to_proto()

            assert proto.props["message"].value.string_data == "こんにちは世界"
        
        def test_multiple_bodies(self):
            body = {
                "int_item": Body(DataType.INT, Props.empty()),
                "str_item": Body(DataType.STRING, Props.empty()),
                "bool_item": Body(DataType.BOOL, Props.empty()),
            }
            methodResponse = MethodResponse(200, Props.empty(), body)
            proto = methodResponse.to_proto()

            assert set(proto.body.keys()) == {"int_item", "str_item", "bool_item"}
        
        def test_code_preserve(self):
            methodResponse = MethodResponse(404, Props.empty(), {})
            proto = methodResponse.to_proto()
            assert proto.code == 404

        
        