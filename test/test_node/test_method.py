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

        @pytest.mark.skip
        def test_from_json5(self):
            pytest.fail("I don't know how do to this")

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

        def test_from_json5_int(self):
            methodResponse = MethodResponse.from_json5(20)

            assert methodResponse.code == 20
            assert methodResponse.props.to_value() == {}
            assert methodResponse.body == {}

        def test_from_json5_fail(self):
            with pytest.raises(ValueError, match="Invalid method repsonse type, Yeah dawg"):
                methodResponse = MethodResponse.from_json5("Yeah dawg")

        