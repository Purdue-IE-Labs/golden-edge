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
            json = {
                "type": "int",
                "props": {
                    'desc': "me when param"
                }
            }

            param = Param.from_json5(json)
            assert param.type == DataType.INT

    class TestEmpty:
        def test_from_json5_wrong_type(self):
            json = 5

            with pytest.raises(ValueError, match="invalid param 5"):
                param = Param.from_json5(json)

        def test_from_json5_no_type(self):
            json = {
                "props": {
                    'desc': "me when param"
                }
            }

            with pytest.raises(ValueError, match="param {'props': {'desc': 'me when param'}} must have type"):
                param = Param.from_json5(json)