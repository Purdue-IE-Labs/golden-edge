import pytest
import gedge
from gedge.node.param import Param
from gedge.node.data_type import DataType
from gedge.node.prop import Props

class TestParam:
    class TestSanity:
        def test_to_proto(self):
            properties = {
                'prop0': 'property0'
            }
        
            param = Param(DataType.INT, Props.from_value(properties))

            protoParam = param.to_proto()

            assert protoParam.type == param.type.to_proto()
            assert protoParam.props == param.props.to_proto()

        def test_from_proto(self):
            # Create a proto param
            properties = {
                'prop0': 'property0'
            }
        
            param = Param(DataType.INT, Props.from_value(properties))

            protoParam = param.to_proto()

            newParam = Param.from_proto(protoParam)

            assert newParam.type == param.type
            assert newParam.props.to_value() == param.props.to_value()

        def test_from_json5(self):
            pytest.fail("Yeah I don't know")

class TestParamData:
    class TestSanity:
        def test_params_proto_to_py(self):
            pytest.fail("Yeah dawg")