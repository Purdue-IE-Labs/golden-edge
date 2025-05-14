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
from gedge.comm.mock_comm import MockComm
from gedge.comm.keys import NodeKeySpace

import pathlib
import logging

@pytest.fixture
def tag_handler():
    print("Yeah dawg")

@pytest.fixture
def method_handler():
    print("Yeah! Testing!!!")

class TestSanity:
    def test_init(self):
        config = NodeConfig("my/node")

        assert config.key == "my/node"
        assert str(config.ks) == str(NodeKeySpace.from_user_key(config.key))
        assert config.tags == dict()
        assert config.methods == dict()
        assert config.subnodes == dict()

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

    def test_from_json5_subnodes(self):
        here = pathlib.Path(__file__).parent
        config = NodeConfig.from_json5(str(here / "subnodes.json5"))

        assert config.key == "test/tag/writes/writee"
        assert len(config.subnodes) == 1
        
        #Subnode Assertions
        assert config.subnodes.get("subnode0").name == "subnode0"
        assert len(config.subnodes.get("subnode0").tags) == 1
        assert len(config.subnodes.get("subnode0").tags.get("tag/write").responses) == 2

        

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

    def test_add_readable_tag(self):
        config = NodeConfig("my/node")

        assert config.tags == dict()

        createdTag = config._add_readable_tag("tag/path", int, {'value0': 20})

        # Tag Tests
        assert createdTag.path == "tag/path"
        assert createdTag.type == DataType.INT
        assert createdTag.props.props['value0'].to_value() == 20

        # Tag Added Tests
        assert len(config.tags) == 1
        assert config.tags.get("tag/path") != None

        assert config.tags.get("tag/path").path == createdTag.path
        assert config.tags.get("tag/path").type == createdTag.type
        assert config.tags.get("tag/path").props.props.items() == createdTag.props.props.items()

    def test_subnode(self):
        config = NodeConfig("my/node")

        manSubnode = SubnodeConfig("my/subnode", config.ks, {}, {}, {})

        config.subnodes.update({'subnode0': manSubnode})

        createdSubnode = config.subnode("subnode0")

        assert createdSubnode.ks == manSubnode.ks
        assert createdSubnode.name == manSubnode.name
        assert createdSubnode.methods == manSubnode.methods
        assert createdSubnode.subnodes == manSubnode.subnodes
        assert createdSubnode.tags == manSubnode.tags

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

    def test_add_writable_tag(self):
        config = NodeConfig("my/node")

        assert config.tags == dict()

        def handler(query: gedge.TagWriteQuery) -> None:
            if query.value > 10:
                query.reply(400)
                return
            query.reply(200)

        createdTag = config.add_writable_tag(path="my/tag", type=int, write_handler=handler, responses=[
            [10, {
                'desc': 'response 0'
            }],
            [20, {
                'desc': 'other response'
            }]
        ], props={})

        # Tag Tests
        assert createdTag.path == "my/tag"
        assert createdTag.type == DataType.INT
        assert createdTag.write_handler == handler

        response0 = WriteResponse(10, Props.from_value({'desc': 'response 0'}))
        assert str(createdTag.responses[0]) == str(response0)

        response1 = WriteResponse(20, Props.from_value({'desc': 'other response'}))
        assert str(createdTag.responses[1]) == str(response1)

        assert createdTag.props.props == {}
        assert createdTag.is_writable() == True

        # Node Tests
        assert config.tags.get("my/tag").path == createdTag.path
        assert config.tags.get("my/tag").type == createdTag.type
        assert config.tags.get("my/tag").write_handler == createdTag.write_handler
        assert config.tags.get("my/tag").responses == createdTag.responses
        assert config.tags.get("my/tag").props.to_value() == createdTag.props.to_value()
        assert config.tags.get("my/tag").is_writable() == createdTag.is_writable()

    def test_add_write_responses(self):
        config = NodeConfig("my/node")

        config.add_tag("my/tag", int, {})

        assert config.tags.get("my/tag").responses == []

        config.add_write_responses("my/tag", [
            (10, {
                'desc': 'response 0'
            }),
            (20, {
                'desc': 'response 1'
            })
        ])

        assert len(config.tags.get("my/tag").responses) == 2

        response0 = WriteResponse(10, Props.from_value({'desc': 'response 0'}))
        assert str(config.tags.get("my/tag").responses[0]) == str(response0)

        response1 = WriteResponse(20, Props.from_value({'desc': 'response 1'}))
        assert str(config.tags.get("my/tag").responses[1]) == str(response1)

    def test_add_write_response(self):
        config = NodeConfig("my/node")

        tag = config.add_tag("my/tag", int, {})

        assert config.tags.get("my/tag").responses == []

        config.add_write_response(tag.path, 10, {'desc': 'response 0'})

        assert len(config.tags.get("my/tag").responses) == 1

        response0 = WriteResponse(10, Props.from_value({'desc': 'response 0'}))
        assert str(config.tags.get("my/tag").responses[0]) == str(response0)

    def test_add_tag_write_handler(self):
        config = NodeConfig("my/node")

        def handler(query: gedge.TagWriteQuery) -> None:
            if query.value > 10:
                query.reply(400)
                return
            query.reply(200)

        config.add_tag("my/tag", int, {})

        assert config.tags.get("my/tag").write_handler == None

        config.add_tag_write_handler("my/tag", handler)

        assert config.tags.get("my/tag").write_handler == handler

    def test_add_method_handler(self):
        config = NodeConfig("my/node")

        def handler(query: gedge.MethodQuery):
            name = query.params["name"]
            speed = query.params["speed"]
            if len(name) > 30:
                query.reply(401)
                return
            if speed < 0 or speed > 100:
                query.reply(400, body={"res1": speed})
                return
            query.reply(200, body={"res1": speed})

        config.add_method("my/method", None, {})

        assert config.methods.get("my/method").handler == None

        config.add_method_handler("my/method", handler)

        assert config.methods.get("my/method").handler == handler

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

    class TestTagDelete:
        @pytest.fixture
        def create_node(self) -> NodeConfig:
            config = NodeConfig("my/node")

            for i in range(0, 3):
                config.add_tag(f"my/tag{i}", int, {})

            return config
        
        def test_first(self, create_node: NodeConfig):
            tagDict = {'my/tag1': create_node.tags.get("my/tag1"), 'my/tag2': create_node.tags.get("my/tag2")}
            
            create_node.delete_tag("my/tag0")

            assert create_node.tags == tagDict
        
        def test_middle(self, create_node: NodeConfig):
            tagDict = {'my/tag0': create_node.tags.get("my/tag0"), 'my/tag2': create_node.tags.get("my/tag2")}
            
            create_node.delete_tag("my/tag1")

            assert create_node.tags == tagDict

        def test_last(self, create_node: NodeConfig):
            tagDict = {'my/tag0': create_node.tags.get("my/tag0"), 'my/tag1': create_node.tags.get("my/tag1")}
            
            create_node.delete_tag("my/tag2")

            assert create_node.tags == tagDict

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

    class TestMethodDelete:
        @pytest.fixture
        def create_node(self) -> NodeConfig:
            config = NodeConfig("my/node")

            for i in range(0, 3):
                config.add_method(f"my/method{i}", None, {})

            return config
        
        def test_first(self, create_node: NodeConfig):
            methodDict = {'my/method1': create_node.methods.get("my/method1"), 'my/method2': create_node.methods.get("my/method2")}
            
            create_node.delete_method("my/method0")

            assert create_node.methods == methodDict
        
        def test_middle(self, create_node: NodeConfig):
            methodDict = {'my/method0': create_node.methods.get("my/method0"), 'my/method2': create_node.methods.get("my/method2")}
            
            create_node.delete_method("my/method1")

            assert create_node.methods == methodDict

        def test_last(self, create_node: NodeConfig):
            methodDict = {'my/method0': create_node.methods.get("my/method0"), 'my/method1': create_node.methods.get("my/method1")}
            
            create_node.delete_method("my/method2")

            assert create_node.methods == methodDict

    def test_verify_tags(self):
        config = NodeConfig("my/node")

        def handler(query: gedge.TagWriteQuery) -> None:
            if query.value > 10:
                query.reply(400)
                return
            query.reply(200)

        config.add_tag("my/tag0", int, {})

        config.add_writable_tag("my/tag1", int, handler, [
            (10, {
                'desc': 'response 0'
            })
        ], {})

        config._verify_tags()

    def test_verify_methods(self):
        config = NodeConfig("my/node")

        def handler(query: gedge.MethodQuery):
            name = query.params["name"]
            speed = query.params["speed"]
            if len(name) > 30:
                query.reply(401)
                return
            if speed < 0 or speed > 100:
                query.reply(400, body={"res1": speed})
                return
            query.reply(200, body={"res1": speed})

        config.add_method("my/method", handler, {})

        config._verify_methods()

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

    '''
    def test_connect(self):
        config = NodeConfig("my/node")
        connections = [
            "tcp/127.0.0.1:7447"
        ]

        session = config._connect(connections)
    '''

    class TestWriteResponses:
    
        def test_add_write_response_no_tag(self):
            instance_str = "instance/str"
            nodeConfig_instance = NodeConfig(instance_str)

            additional_response = {
                "message": "Request was successful"
            }

            with pytest.raises(TagLookupError, match="Tag test_path not found on node str"):
                nodeConfig_instance.add_write_response("test_path", 300, additional_response)
    
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

    def test_verify_tags_no_responses(self):
        nodeConfig_instance = NodeConfig("instance/str")

        properties = {
            'tag1': 'int',
            'tag2': 'float',
            'tag3': 'str'
        }

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

    def test_from_json5_no_key(self):
        here = pathlib.Path(__file__).parent
       
        with pytest.raises(LookupError, match="Node must have a key"):
            config = NodeConfig.from_json5(str(here / "no_key.json5"))

       