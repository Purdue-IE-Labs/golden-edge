import gedge
import pytest
from gedge.node.body import Body
from gedge.node.data_type import DataType

class TestSanity:
    def test_to_proto(self):
        # Create a body
        json = {
            "type": "int",
            "props": {
                "desc": "name of the body"
            }
        }
        
        body = Body.from_json5(json)

        protoBody = body.to_proto()

        assert protoBody.type == body.type.to_proto()

    def test_from_proto(self):
        json = {
            "type": "int",
            "props": {
                "desc": "name of the body"
            }
        }

        body = Body.from_json5(json)

        protoBody = body.to_proto()

        newBody = Body.from_proto(protoBody)

        assert newBody.type == body.type
        assert newBody.props.to_value() == body.props.to_value()

    def test_from_json5(self):
        json = {
            "type": "int",
            "props": {
                "desc": "name of the body"
            }
        }
        
        body = Body.from_json5(json)

        assert body.type == DataType.INT
        assert body.props.to_value() == {"desc": "name of the body"}

class TestEmpty:
    def test_json5_wrong_type(self):
        json = 5

        with pytest.raises(ValueError, match="invalid body 5"):
            body = Body.from_json5(json)

    def test_json5_no_type(self):
        json = {
            "props": {
                "desc": "name of the body"
            }
        }

        with pytest.raises(ValueError, match="body {'props': {'desc': 'name of the body'}} must have type"):
            body = Body.from_json5(json)