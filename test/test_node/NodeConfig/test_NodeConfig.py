import gedge
import pytest

from gedge.node.node import NodeConfig, NodeSession, Tag, Method
from gedge.node.subnode import SubnodeConfig
from gedge.node.data_type import DataType
from gedge.node.prop import Props
from gedge.node.tag import WriteResponse
from gedge.node.error import MethodLookupError, TagLookupError
from gedge.proto import Meta
from gedge import proto
from gedge.comm.comm import Comm

import pathlib
import logging

@pytest.fixture
def tag_handler():
    print("Yeah dawg")

@pytest.fixture
def method_handler():
    print("Yeah! Testing!!!")

class TestSanity:
    def test_from_json5(self):
        here = pathlib.Path(__file__).parent
        config = NodeConfig.from_json5(str(here / "normal.json5"))

        assert config.key == "test/tag/writes/writee"
        
        # Tag Assetions
        assert len(config.tags) == 1
        assert config.tags.get("tag/write").type == DataType.INT
        assert config.tags.get("tag/write").is_writable() == True
        assert config.tags.get("tag/write").props.to_value().get("desc") == "testing a tag write"

        # Response Assertions
        assert len(config.tags.get("tag/write").responses) == 2
        assert config.tags.get("tag/write").responses[0].code == 200
        assert config.tags.get("tag/write").responses[0].props.to_value().get("desc") == "tag updated with value"
        assert config.tags.get("tag/write").responses[1].code == 400
        assert config.tags.get("tag/write").responses[1].props.to_value().get("desc") == "invalid value (>10)"
        

    def test_from_json5_str(self):
        json_str1 = '''
            {
                "key": "test/tag/writes/writee",
                "tags": [
                    {
                        "path": "tag/write",
                        "type": "int",
                        "writable": true,
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
                    },
                ],
            }
            '''
        config = NodeConfig.from_json5_str(json_str1)

        assert config.key == "test/tag/writes/writee"
        
        # Tag Assetions
        assert len(config.tags) == 1
        assert config.tags.get("tag/write").type == DataType.INT
        assert config.tags.get("tag/write").is_writable() == True
        assert config.tags.get("tag/write").props.to_value().get("desc") == "testing a tag write"

        # Response Assertions
        assert len(config.tags.get("tag/write").responses) == 2
        assert config.tags.get("tag/write").responses[0].code == 200
        assert config.tags.get("tag/write").responses[0].props.to_value().get("desc") == "tag updated with value"
        assert config.tags.get("tag/write").responses[1].code == 400
        assert config.tags.get("tag/write").responses[1].props.to_value().get("desc") == "invalid value (>10)"

    def test_get_key(self):
        here = pathlib.Path(__file__).parent
        config = NodeConfig.from_json5(str(here / "normal.json5"))

        assert config.key == config._user_key

    def test_set_key(self):
        here = pathlib.Path(__file__).parent
        config = NodeConfig.from_json5(str(here / "normal.json5"))

        prevKey = config._user_key
        prevKs = config.ks

        config.key = "new/NODE/key"

        assert config._user_key != prevKey
        assert config.ks != prevKs

    def test_warn_duplicate_tag(self, caplog):
        instance_str = "instance/str"
        nodeConfig_instance = NodeConfig(instance_str)

        assert nodeConfig_instance.tags == {}

        properties = {
            'tag1': 'int',
            'tag2': 'float',
            'tag3': 'str',
        }

        NodeConfig.add_tag(nodeConfig_instance, "test_path", int, properties)
    
        # Add the same tag again to trigger the warning
        with caplog.at_level(logging.WARNING):  # Captures the logger output
            NodeConfig.add_tag(nodeConfig_instance, "test_path", int, properties)

        assert len(caplog.records) > 0  # At least one log record should exist
    
        # Optionally, check the level of the logged message
        assert caplog.records[0].levelname == "WARNING"  # Ensure the log level is WARNING

    def test_add_tag(self):
        instance_str = "instance/str"
        nodeConfig_instance = NodeConfig(instance_str)

        assert nodeConfig_instance.tags == {}

        properties = {
            'tag1': 'int',
            'tag2': 'float',
            'tag3': 'str',
        }

        NodeConfig.add_tag(nodeConfig_instance, "test_path", int, properties)
    
        expected_tag = Tag("test_path", DataType.INT, Props.from_value(properties), False, [], None)

        assert nodeConfig_instance.tags['test_path'].path == expected_tag.path
        assert nodeConfig_instance.tags['test_path'].type == expected_tag.type
        assert nodeConfig_instance.tags['test_path'].props.to_value() == expected_tag.props.to_value()
        assert nodeConfig_instance.tags['test_path']._writable == expected_tag._writable
        assert nodeConfig_instance.tags['test_path'].write_handler == expected_tag.write_handler

    def test_add_props(self):
        instance_str = "instance/str"
        nodeConfig_instance = NodeConfig(instance_str)

        properties = {
            'method1': 'int',
            'method2': 'float',
            'method3': 'str'
        }

        nodeConfig_instance.add_tag("test_path", int, {})

        expected_tag = Tag("test_path", int, Props.from_value(properties), False, [], None)

        assert nodeConfig_instance.tags['test_path'].props != expected_tag.props

        nodeConfig_instance.add_props("test_path", properties)

        assert nodeConfig_instance.tags['test_path'].props.to_value() == expected_tag.props.to_value()

    # Note: Maybe some more in-depth testing of delete tag would be good
    # Example Cases:
    #   1) First Tag
    #   2) Middle Tag
    #   3) Last Tag

    def test_delete_tag(self):
        instance_str = "instance/str"
        nodeConfig_instance = NodeConfig(instance_str)

        properties = {
            'tag1': 'int',
            'tag2': 'float',
            'tag3': 'str'
        }

        nodeConfig_instance.add_tag("test_path", int, properties)

        assert nodeConfig_instance.tags['test_path'] != None

        nodeConfig_instance.delete_tag("test_path")

        assert nodeConfig_instance.tags == {}

    def test_add_method(self):
        nodeConfig_instance = NodeConfig("instance/str")

        properties = {
            'method1': 'int',
            'method2': 'float',
            'method3': 'str'
        }

        assert nodeConfig_instance.methods == {}

        nodeConfig_instance.add_method("test_path", method_handler, properties)

        assert len(nodeConfig_instance.methods) == 1

        expected_method = Method("test_path", method_handler, Props.from_value(properties), {}, [])

        assert nodeConfig_instance.methods['test_path'].props.to_value() == expected_method.props.to_value()
        assert nodeConfig_instance.methods['test_path'].params == expected_method.params
        assert nodeConfig_instance.methods['test_path'].responses == expected_method.responses

    def test_delete_method(self):
        nodeConfig_instance = NodeConfig("instance/str")

        properties = {
            'method1': 'int',
            'method2': 'float',
            'method3': 'str'
        }

        nodeConfig_instance.add_method("test_path", method_handler, properties)

        expected_method = Method("test_path", method_handler, Props.from_value(properties), {}, [])

        assert nodeConfig_instance.methods != {}

        nodeConfig_instance.delete_method("test_path")

        assert nodeConfig_instance.methods == {}

    def test_build_meta(self):
    
        nodeConfig_instance = NodeConfig("instance/str")

        nodeConfig_instance.subnodes['subnode0'] = SubnodeConfig("subnode0", nodeConfig_instance.ks, {}, {}, {})

        nodeConfig_instance.add_tag("tag/path", int, {'tag1': 'int', 'tag2': 'float'})

        nodeConfig_instance.add_method("method/path", method_handler, {'method1': 'int', 'method2': 'float'})

        meta_tags: list[proto.Tag] = [t.to_proto() for t in nodeConfig_instance.tags.values()]
        meta_methods: list[proto.Method] = [m.to_proto() for m in nodeConfig_instance.methods.values()]
        meta_subnodes: list[proto.Subnode] = [s.to_proto() for s in nodeConfig_instance.subnodes.values()]

        expected_meta = Meta(tracking=False, key=nodeConfig_instance.key, tags=meta_tags, methods=meta_methods, subnodes=meta_subnodes)

        assert expected_meta == nodeConfig_instance.build_meta()

    def test_connect(self):

        '''
        config_instance = NodeConfig("instance/str")
        connections = [
            "connection0",
            "connection1"
        ]
        session_instance = NodeSession(config_instance, Comm(connections))

        '''
    
        #TODO
        pytest.fail("Go to the Github and Look at test/test_test_methods for examples of MockComm")

    class TestWriteResponses:

        def test_add_write_response(self, tag_handler):

            instance_str = "instance/str"
            nodeConfig_instance = NodeConfig(instance_str)

            properties = {
                'tag1': 'int',
                'tag2': 'float',
                'tag3': 'str'
            }

            responses = [
                (200, {"status": "success", "message": "Request was successful"}),
                (404, {"status": "error", "message": "Not Found"}),
                (500, {"status": "error", "message": "Internal Server Error"}),
            ]

            nodeConfig_instance.add_writable_tag("test_path", int, tag_handler, responses, properties)

            expected_tag = Tag("test_path", DataType.INT, Props.from_value(properties), False, [], None)

            expected_tag.writable(tag_handler, responses)

            additional_response = {
                "message": "Request was successful"
            }

            assert nodeConfig_instance.tags['test_path'].props.to_value() == expected_tag.props.to_value()

            nodeConfig_instance.add_write_response("test_path", 300, additional_response)

            expected_tag.add_write_response(300, Props.from_value(additional_response))

            assert nodeConfig_instance.tags['test_path'].props.to_value() == expected_tag.props.to_value()
    
        def test_add_write_response_no_tag(self):
            instance_str = "instance/str"
            nodeConfig_instance = NodeConfig(instance_str)

            additional_response = {
                "message": "Request was successful"
            }

            with pytest.raises(TagLookupError, match="Tag test_path not found on node str"):
                nodeConfig_instance.add_write_response("test_path", 300, additional_response)
        
        def test_add_write_responses(self, tag_handler):
            instance_str = "instance/str"
            nodeConfig_instance = NodeConfig(instance_str)

            properties = {
                'tag1': 'int',
                'tag2': 'float',
                'tag3': 'str'
            }

            responses = [
                (200, {"status": "success", "message": "Request was successful"}),
                (404, {"status": "error", "message": "Not Found"}),
                (500, {"status": "error", "message": "Internal Server Error"}),
            ]

            nodeConfig_instance.add_writable_tag("test_path", int, tag_handler, responses, properties)

            expected_tag = Tag("test_path", DataType.INT, Props.from_value(properties), False, [], None)

            expected_tag.writable(tag_handler, responses)

            additional_responses = [
                (300, {"status": "Success", "message": "Request was also successful"}),
                (600, {"status": "error", "message": "uh oh"})
            ]

            assert str(nodeConfig_instance.tags['test_path'].responses) == str(expected_tag.responses)

            nodeConfig_instance.add_write_responses("test_path", additional_responses)

            expected_tag.add_write_response(300, Props.from_value({"status": "Success", "message": "Request was also successful"}))
            expected_tag.add_write_response(600, Props.from_value({"status": "error", "message": "uh oh"}))

            assert str(nodeConfig_instance.tags['test_path'].responses) == str(expected_tag.responses)
    
        def test_add_write_responses_no_tag(self):
            instance_str = "instance/str"
            nodeConfig_instance = NodeConfig(instance_str)

            additional_responses = [
                (300, {"message": "Request was successful"}),
                (400, {"message": "Request was not successful"})
            ]

            with pytest.raises(TagLookupError, match="Tag test_path not found on node str"):
                nodeConfig_instance.add_write_responses("test_path", additional_responses)

        def test_add_tag_write_handler(self, tag_handler):
        
            instance_str = "instance/str"
            nodeConfig_instance = NodeConfig(instance_str)

            properties = {
                'tag1': 'int',
                'tag2': 'float',
                'tag3': 'str'
            }

            responses = [
                (200, {"status": "success", "message": "Request was successful"}),
                (404, {"status": "error", "message": "Not Found"}),
                (500, {"status": "error", "message": "Internal Server Error"}),
            ]

            nodeConfig_instance.add_tag("test_path", int, properties)

            expected_tag = Tag("test_path", int, Props.from_value(properties), False, [], None)

            assert str(nodeConfig_instance.tags['test_path'].write_handler) == str(expected_tag.write_handler)

            expected_tag.writable(tag_handler, responses)

            nodeConfig_instance.add_tag_write_handler("test_path", tag_handler)

            assert nodeConfig_instance.tags['test_path'].write_handler == expected_tag.write_handler

        def test_add_method_handler(self):
            instance_str = "instance/str"
            nodeConfig_instance = NodeConfig(instance_str)

            properties = {
                'method1': 'int',
                'method2': 'float',
                'method3': 'str'
            }

            nodeConfig_instance.add_method("test_path", None, properties)

            expected_method = Method("test_path", method_handler, Props.from_value(properties), None, None)

            assert nodeConfig_instance.methods["test_path"].handler != expected_method.handler

            nodeConfig_instance.add_method_handler("test_path", method_handler)

            assert nodeConfig_instance.methods["test_path"].handler == expected_method.handler

class TestEmpty:

    def test_add_tag_write_handler_no_tag(self, tag_handler):
        instance_str = "instance/str"
        nodeConfig_instance = NodeConfig(instance_str)
    
        with pytest.raises(TagLookupError, match="Tag test_path not found on node str"):
            nodeConfig_instance.add_tag_write_handler("test_path", tag_handler)

    def test_add_method_handler_no_tag(self):
        instance_str = "instance/str"
        nodeConfig_instance = NodeConfig(instance_str)

        with pytest.raises(MethodLookupError, match="Method test_path not found on node str"):
            nodeConfig_instance.add_method_handler("test_path", method_handler)


    def test_add_props_no_tag(self):
        instance_str = "instance/str"
        nodeConfig_instance = NodeConfig(instance_str)

        properties = {
            'method1': 'int',
            'method2': 'float',
            'method3': 'str'
        }

        with pytest.raises(TagLookupError, match="Tag test_path not found on node str"):
            nodeConfig_instance.add_props("test_path", properties)

    def test_delete_tag_no_tag(self):
        instance_str = "instance/str"
        nodeConfig_instance = NodeConfig(instance_str)

        with pytest.raises(TagLookupError, match="Tag test_path not found on node str"):
            nodeConfig_instance.delete_tag("test_path")

    def test_delete_method_no_method(self):
        nodeConfig_instance = NodeConfig("instance/str")

        with pytest.raises(MethodLookupError, match="Method test_path not found on node str"):
            nodeConfig_instance.delete_method("test_path")

    def test_verify_tags_no_handler(self):
        nodeConfig_instance = NodeConfig("instance/str")

        properties = {
            'tag1': 'int',
            'tag2': 'float',
            'tag3': 'str'
        }

        nodeConfig_instance.add_tag("test_path", int, properties)

        nodeConfig_instance.tags['test_path']._writable = True

        with pytest.raises(AssertionError, match="Tag test_path declared as writable but no write handler was provided"):
            nodeConfig_instance._verify_tags()

    def test_verify_tags_no_responses(self, tag_handler):
        nodeConfig_instance = NodeConfig("instance/str")

        properties = {
            'tag1': 'int',
            'tag2': 'float',
            'tag3': 'str'
        }

        print(tag_handler)

        nodeConfig_instance.add_writable_tag("test_path", int, write_handler=tag_handler, responses=[], props=properties)

        with pytest.raises(AssertionError, match="Tag test_path declared as writable but no responses registered for write handler"):
            nodeConfig_instance._verify_tags()

    def test_verify_methods_no_handler(self):
        nodeConfig_instance = NodeConfig("instance/str")

        properties = {
            'tag1': 'int',
            'tag2': 'float',
            'tag3': 'str'
        }

        nodeConfig_instance.add_method("test_path", None, properties)

        with pytest.raises(AssertionError, match="Method test_path has no handler"):
            nodeConfig_instance._verify_methods()

    def test_build_meta_fail_tag_verify(self):
        nodeConfig_instance = NodeConfig("instance/str")

        nodeConfig_instance.add_tag("tag/path", int, {'tag1': 'int', 'tag2': 'float'})

        nodeConfig_instance.tags['tag/path']._writable = True

        with pytest.raises(AssertionError, match="Tag tag/path declared as writable but no write handler was provided"):
            nodeConfig_instance.build_meta()

    def test_build_meta_fail_method_verify(self):
        nodeConfig_instance = NodeConfig("instance/str")

        nodeConfig_instance.add_method("method/path", None, {})

        with pytest.raises(AssertionError, match="Method method/path has no handler"):
            nodeConfig_instance.build_meta()

    def test_build_meta_no_tags(self):
        nodeConfig_instance = NodeConfig("instance/str")

        nodeConfig_instance.subnodes['subnode0'] = SubnodeConfig("subnode0", nodeConfig_instance.ks, {}, {}, {})

        nodeConfig_instance.add_method("method/path", method_handler, {'method1': 'int', 'method2': 'float'})

        meta_methods: list[proto.Method] = [m.to_proto() for m in nodeConfig_instance.methods.values()]
        meta_subnodes: list[proto.Subnode] = [s.to_proto() for s in nodeConfig_instance.subnodes.values()]

        expected_meta = Meta(tracking=False, key=nodeConfig_instance.key, tags=None, methods=meta_methods, subnodes=meta_subnodes)

        assert expected_meta == nodeConfig_instance.build_meta()

    def test_build_meta_no_methods(self):   
        nodeConfig_instance = NodeConfig("instance/str")

        nodeConfig_instance.subnodes['subnode0'] = SubnodeConfig("subnode0", nodeConfig_instance.ks, {}, {}, {})

        nodeConfig_instance.add_tag("tag/path", int, {'tag1': 'int', 'tag2': 'float'})

        meta_tags: list[proto.Tag] = [t.to_proto() for t in nodeConfig_instance.tags.values()]
        meta_subnodes: list[proto.Subnode] = [s.to_proto() for s in nodeConfig_instance.subnodes.values()]

        expected_meta = Meta(tracking=False, key=nodeConfig_instance.key, tags=meta_tags, methods=None, subnodes=meta_subnodes)

        assert expected_meta == nodeConfig_instance.build_meta()

    def test_build_meta_no_subnodes(self):
        nodeConfig_instance = NodeConfig("instance/str")

        nodeConfig_instance.add_tag("tag/path", int, {'tag1': 'int', 'tag2': 'float'})

        nodeConfig_instance.add_method("method/path", method_handler, {'method1': 'int', 'method2': 'float'})

        meta_tags: list[proto.Tag] = [t.to_proto() for t in nodeConfig_instance.tags.values()]
        meta_methods: list[proto.Method] = [m.to_proto() for m in nodeConfig_instance.methods.values()]

        expected_meta = Meta(tracking=False, key=nodeConfig_instance.key, tags=meta_tags, methods=meta_methods, subnodes=None)

        assert expected_meta == nodeConfig_instance.build_meta()

    def test_build_meta_no_attributes(self):
        nodeConfig_instance = NodeConfig("instance/str")

        expected_meta = Meta(tracking=False, key=nodeConfig_instance.key, tags=None, methods=None, subnodes=None)

        assert expected_meta == nodeConfig_instance.build_meta()