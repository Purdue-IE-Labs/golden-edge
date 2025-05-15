import gedge
from gedge.node.tag import WriteResponse, Tag
from gedge.node.prop import Props
from gedge.node.tag_data import TagData
from gedge.node.data_type import DataType
from gedge.node.tag_bind import TagBind
from gedge.node.node import NodeConfig
from gedge.comm.mock_comm import MockComm
import math

import pytest


json_complete = {
    "code": 200, 
    "props": {
        "desc": "tag updated with value"
    }
}

json_no_code = {
    "props": {
        "desc": "tag updated with value"
    }
}

json_no_props = {
    "code": 200, 
}


class TestWriteResponse:
    class TestSanity:
        @pytest.mark.parametrize("json, code, prop", [
                (json_complete, 200, TagData.from_value("tag updated with value", DataType.STRING)),
                (json_no_code, None, TagData.from_value("tag updated with value", DataType.STRING)),
                (json_no_props, 200, TagData.from_value("", DataType.STRING))
            ], ids=["Normal", "No Code", "No Props"])
        def test_to_proto(self, json: dict, code: int, prop: TagData):
            if code is None:
                with pytest.raises(LookupError, match="Tag write response must include code"):
                    response = WriteResponse.from_json5(json)
                return
            else:
                response = WriteResponse.from_json5(json)

            proto = response.to_proto()

            assert proto.code == code

            assert proto.props["desc"].value.string_data == prop.value

        @pytest.mark.parametrize("json, code", [
                (json_complete, 200),
                (json_no_code, None),
                (json_no_props, 200)
            ], ids=["Normal", "No Code", "No Props"])
        def test_from_proto(self, json: dict, code: int):
            if code is None:
                with pytest.raises(LookupError, match="Tag write response must include code"):
                    response = WriteResponse.from_json5(json)
                return
            else:
                response = WriteResponse.from_json5(json)

            proto = response.to_proto()

            otherResponse = WriteResponse.from_proto(proto)

            assert otherResponse.code == response.code
            assert otherResponse.props.to_value() == response.props.to_value()

        @pytest.mark.parametrize("json, code, prop", [
                (json_complete, 200, {"desc": "tag updated with value"}),
                (json_no_code, None, {"desc": "tag updated with value"}),
                (json_no_props, 200, {}),
                (200, 200, {})
            ], ids=["Normal", "No Code", "No Props", "Int Init"])
        def test_from_json5(self, json, code: int, prop: TagData):
            if code is None:
                with pytest.raises(LookupError, match="Tag write response must include code"):
                    response = WriteResponse.from_json5(json)
                return
            else:
                response = WriteResponse.from_json5(json)

                assert response.code == code
                assert response.props.to_value() == prop
    
    class TestEmpty:
        def test_json_wrong_type(self):
            with pytest.raises(ValueError, match="invalid write response Hello world"):
                response = WriteResponse.from_json5("Hello world")


class TestTag:
    class TestSanity:
        def test_init(self):
            tag = Tag("my/tag", DataType.INT, Props.from_value({"desc": "Test tag"}), False, [], None)

            assert tag.path == "my/tag"
            assert tag.type == DataType.INT
            assert tag.props.to_value() == {"desc": "Test tag"}
            assert tag._writable == False
            assert tag.responses == []
            assert tag.write_handler == None

        def test_to_proto(self):
            tag = Tag("my/tag", DataType.INT, Props.from_value({"desc": "Test tag"}), False, [], None)

            protoTag = tag.to_proto()

            assert protoTag.path == tag.path
            assert protoTag.type == tag.type.to_proto()
            assert protoTag.writable == tag._writable
            assert protoTag.responses == tag.responses

        def test_from_proto(self):
            tag = Tag("my/tag", DataType.INT, Props.from_value({"desc": "Test tag"}), False, [], None)

            protoTag = tag.to_proto()

            otherTag = Tag.from_proto(protoTag)

            assert otherTag.path == tag.path
            assert otherTag.type == tag.type
            assert otherTag.props.to_value() == tag.props.to_value()
            assert otherTag._writable == tag._writable
            assert otherTag.responses == tag.responses
            assert otherTag.write_handler == tag.write_handler

        json_complete = {
            "path": "tag/write",
            "type": "int",
            "writable": True,
            "props": {
                "desc": "testing a tag write",
            },
            "responses": [
                {
                    "code": 200, 
                    "props": {
                        "desc": "tag updated with value"
                    }
                },
                {
                    "code": 400,
                    "props": {
                        "desc": "invalid value (>10)"
                    }
                }
            ]
        }

        json_no_path = {
            "type": "int",
            "writable": True,
            "props": {
                "desc": "testing a tag write",
            },
            "responses": [
                {
                    "code": 200, 
                    "props": {
                        "desc": "tag updated with value"
                    }
                },
                {
                    "code": 400,
                    "props": {
                        "desc": "invalid value (>10)"
                    }
                }
            ]
        }

        json_no_type = {
            "path": "tag/write",
            "writable": True,
            "props": {
                "desc": "testing a tag write",
            },
            "responses": [
                {
                    "code": 200, 
                    "props": {
                        "desc": "tag updated with value"
                    }
                },
                {
                    "code": 400,
                    "props": {
                        "desc": "invalid value (>10)"
                    }
                }
            ]
        }

        json_no_path_and_type = {
            "writable": True,
            "props": {
                "desc": "testing a tag write",
            },
            "responses": [
                {
                    "code": 200, 
                    "props": {
                        "desc": "tag updated with value"
                    }
                },
                {
                    "code": 400,
                    "props": {
                        "desc": "invalid value (>10)"
                    }
                }
            ]
        }

        json_no_props = {
            "path": "tag/write",
            "type": "int",
            "writable": True,
            "responses": [
                {
                    "code": 200, 
                    "props": {
                        "desc": "tag updated with value"
                    }
                },
                {
                    "code": 400,
                    "props": {
                        "desc": "invalid value (>10)"
                    }
                }
            ]
        }

        json_writable_but_no_responses = {
            "path": "tag/write",
            "type": "int",
            "writable": True,
            "props": {
                "desc": "testing a tag write",
            },
        }

        json_responses_but_no_writable = {
            "path": "tag/write",
            "type": "int",
            "writable": False,
            "props": {
                "desc": "testing a tag write",
            },
        }

        json_not_writable = {
            "path": "tag/write",
            "type": "int",
            "writable": False,
            "props": {
                "desc": "testing a tag write",
            },
        }

        
        @pytest.mark.parametrize("json, path, type, props, writable, responses", [
                (json_complete, "tag/write", DataType.INT, 
                    {"desc": "testing a tag write"}, 
                    True, 
                    [
                        {"code": 200, "props": {"desc": "tag updated with value"}}, 
                        {"code": 400,"props": {"desc": "invalid value (>10)"}}
                    ]),
                (json_no_path, "", DataType.INT, 
                    {"desc": "testing a tag write"}, 
                    True,
                    [
                        {"code": 200, "props": {"desc": "tag updated with value"}}, 
                        {"code": 400,"props": {"desc": "invalid value (>10)"}}
                    ]),
                (json_no_type, "tag/write", "", 
                    {"desc": "testing a tag write"}, 
                    True,
                    [
                        {"code": 200, "props": {"desc": "tag updated with value"}}, 
                        {"code": 400,"props": {"desc": "invalid value (>10)"}}
                    ]),
                (json_no_path_and_type, "", "", 
                    {"desc": "testing a tag write"}, 
                    True,
                    [
                        {"code": 200, "props": {"desc": "tag updated with value"}}, 
                        {"code": 400,"props": {"desc": "invalid value (>10)"}}
                    ]),
                (json_no_props, "tag/write", DataType.INT, 
                    {}, 
                    True,
                    [
                        {"code": 200, "props": {"desc": "tag updated with value"}}, 
                        {"code": 400,"props": {"desc": "invalid value (>10)"}}
                    ]),
                (json_writable_but_no_responses, "tag/write", DataType.INT, 
                    {"desc": "testing a tag write"}, 
                    True,
                    []),
                (json_responses_but_no_writable, "tag/write", DataType.INT, 
                    {"desc": "testing a tag write"}, 
                    False,
                    [
                        {"code": 200, "props": {"desc": "tag updated with value"}}, 
                        {"code": 400,"props": {"desc": "invalid value (>10)"}}
                    ]),
                (json_not_writable, "tag/write", DataType.INT, 
                    {"desc": "testing a tag write"}, 
                    False,
                    []),
                (5, None, None, None, None, None)
            ], ids=["Normal", 
                    "No Path", 
                    "No Type", 
                    "No Path or Type", 
                    "No Props", 
                    "Writable but No Responses", 
                    "Responses but not Writable", 
                    "Not Writable",
                    "Not a Dict"])
        def test_from_json5(self, json, path, type, props, writable, responses: list[dict]):

            if path == "" or type == "":
                with pytest.raises(LookupError):
                    tag = Tag.from_json5(json)
                return
            
            if not isinstance(json, dict):
                with pytest.raises(ValueError, match="invalid tag, tag must be a dict"):
                    tag = Tag.from_json5(json)
                return
            
            tag = Tag.from_json5(json)

            assert tag.path == path
            assert tag.type == type
            assert tag.props.to_value() == props
            assert tag._writable == writable
            for i in range(0, len(tag.responses)):
                assert tag.responses[i].code == responses[i].get("code")
                assert tag.responses[i].props.to_value() == responses[i].get("props")
            assert tag.write_handler == None

        def test_writable(self):
            tag = Tag("my/tag", DataType.INT, Props.from_value({"desc": "Test tag"}), False, [], None)

            def handler(self):
                print("I'm handling it")

            responses = [
                (200, {"desc": "tag updated with value"}), 
                (400, {"desc": "invalid value (>10)"})
            ]

            newTag = tag.writable(handler, responses)

            assert newTag._writable == True
            assert newTag.write_handler != None
            assert len(newTag.responses) == 2
            for i in range(0, len(newTag.responses)):
                assert newTag.responses[i]

        def test_is_writable(self):
            tag = Tag("my/tag", DataType.INT, Props.from_value({"desc": "Test tag"}), False, [], None)

            assert tag.is_writable() == False

            tag._writable = True

            assert tag.is_writable() == True

        def test_add_write_response(self):
            tag = Tag("my/tag", DataType.INT, Props.from_value({"desc": "Test tag"}), False, [], None)
            
            tag.add_write_response(200)

            assert len(tag.responses) != 0

            assert tag.responses[0].code == 200
            assert tag.responses[0].props.to_value() == {}

            with pytest.raises(ValueError, match="Tag write responses must have unique codes, and code 200 is not unique"):
                tag.add_write_response(200)

class TestTagBind:
    class TestSanity:
        def test_close(self):
            node = NodeConfig("my/node")
            tag = node.add_tag("tag/path", int, {})
            tagBind = TagBind(node.ks, MockComm(), tag, None, None)

            assert tagBind.is_valid == True

            tagBind.close()

            assert tagBind.is_valid == False

class TestTagData:
    class TestSanity:
        def test_to_proto(self):
            tagData = TagData.from_value(5, DataType.INT)

            protoTagData = tagData.to_proto()

            assert protoTagData.int_data == 5

        def test_to_py(self):
            tagData = TagData.from_value(5, DataType.INT)

            pyTagData = tagData.to_py()

            assert pyTagData == 5

        def test_from_proto(self):
            tagData = TagData.from_value(5, DataType.INT)

            protoTagData = tagData.to_proto()

            newTagData = TagData.from_proto(protoTagData, DataType.INT)

            assert newTagData.type == tagData.type
            assert newTagData.value == tagData.value
            assert newTagData.proto == tagData.proto

        @pytest.mark.parametrize("value, type, expected_value", [
        (5, DataType.INT, 5),
        (5, DataType.LONG, 5),
        (1.4, DataType.FLOAT, 1.4),
        ("Hello World", DataType.STRING, "Hello World"),
        (True, DataType.BOOL, True),
        ([1, 2, 3, 4], DataType.LIST_INT, [1, 2, 3, 4]),
        ([1, 2, 3, 4], DataType.LIST_LONG, [1, 2, 3, 4]),
        ([1.1, 2.2, 3.3, 4.4], DataType.LIST_FLOAT, [1.1, 2.2, 3.3, 4.4]),
        (["Hello World", "Hi"], DataType.LIST_STRING, ["Hello World", "Hi"]),
        ([True, False, 1, 0], DataType.LIST_BOOL, [True, False, True, False]),
        ("dict[any]", None, None)
    ])
        def test_py_to_proto(self, value, type, expected_value):
            if type is None:
                with pytest.raises(ValueError, match="Unknown tag type None"):
                    proto = TagData.py_to_proto(value, type)
                return
            
            proto = TagData.py_to_proto(value, type)

            match type:
                case DataType.INT:
                    assert proto.int_data == expected_value
                case DataType.LONG:
                    assert proto.long_data == expected_value
                case DataType.FLOAT:
                    assert math.isclose(proto.float_data, expected_value)
                case DataType.STRING:
                    assert proto.string_data == expected_value
                case DataType.BOOL:
                    assert proto.bool_data == expected_value
                case DataType.LIST_INT:
                    assert proto.list_int_data.list == expected_value
                case DataType.LIST_LONG:
                    assert proto.list_long_data.list == expected_value
                case DataType.LIST_FLOAT:
                    assert proto.list_float_data.list == expected_value
                case DataType.LIST_STRING:
                    assert proto.list_string_data.list == expected_value
                case DataType.LIST_BOOL:
                    assert proto.list_bool_data.list == expected_value
            