import pytest

import gedge

from gedge.node.node import NodeConfig
from gedge.node.subnode import SubnodeConfig, SubnodeSession, RemoteSubConnection
from gedge.node.tag import Tag
from gedge.node.data_type import DataType
from gedge.node.prop import Props
from gedge.comm.mock_comm import MockComm

# Note: This class contains all of the subnode test functions

class TestSubnodeConfig:
    class TestSanity:
        def test_init(self):
            parent = NodeConfig("my/node")
            subnode = SubnodeConfig("subnode", parent.ks, {}, {}, {})

            assert subnode.name == "subnode"
            assert str(subnode.ks) == "my/NODE/node/SUBNODES/subnode"
            assert subnode.tags == {}
            assert subnode.methods == {}
            assert subnode.subnodes == {}

        def test_from_json5(self):
            json = {
                "name": "subnode0",
                "tags": [
                    {
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
                ]
            }

            parent = NodeConfig("my/node")
            subnode = SubnodeConfig.from_json5(json, parent.ks)

            assert subnode.name == "subnode0"
            assert len(subnode.tags) == 1
            assert subnode.tags.get("tag/write").is_writable() == True

        def test_from_json5_subnodes(self):
            json = {
                "name": "subnode0",
                "tags": [
                    {
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
                ],
                "subnodes": [
                    {
                        "name": "subnode1"
                    }

                ]
            }

            parent = NodeConfig("my/node")
            subnode = SubnodeConfig.from_json5(json, parent.ks)

            assert subnode.name == "subnode0"
            assert len(subnode.tags) == 1
            assert subnode.tags.get("tag/write").is_writable() == True

    class TestEmpty:
        def test_from_json5_wrong_type(self):
            parent = NodeConfig("my/node")
            with pytest.raises(ValueError, match="subnode must be dict: None"):
                subnode = SubnodeConfig.from_json5(None, parent.ks)

        def test_from_json5_no_name(self):
            parent = NodeConfig("my/node")
            json = {
                "tags": [
                    {
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
                ]
            }

            with pytest.raises(ValueError, match="subnode must have name"):
                subnode = SubnodeConfig.from_json5(json, parent.ks)

        def test_from_json5_slash(self):
            parent = NodeConfig("my/node")
            json = {
                "name": "subnode/0",
                "tags": [
                    {
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
                ]
            }
        
            with pytest.raises(ValueError, match="subnode name cannot have '/' but subnode 'subnode/0' found in json config"):
                subnode = SubnodeConfig.from_json5(json, parent.ks)

class TestSubnodeSession:
    class TestSanity:
        def test_init(self):
            parent = NodeConfig("my/name")
            subnode = SubnodeConfig("subnode", parent.ks, {}, {}, {})

            subnodeSession = SubnodeSession(subnode, MockComm())
            
            assert subnodeSession.config == subnode
            assert subnodeSession.ks == subnode.ks
            assert subnodeSession.tags == subnode.tags
            assert subnodeSession.methods == subnode.methods
            assert subnodeSession.subnodes == subnode.subnodes

        def test_subnode(self):
            parent = NodeConfig("my/name")
            subnode = SubnodeConfig("subnode", parent.ks, {}, {}, {})
            subSubnode = SubnodeConfig("subSubnode", subnode.ks, {}, {}, {})

            subnode.subnodes.update({subSubnode.name: subSubnode})

            subnodeSession = SubnodeSession(subnode, MockComm())

            assert len(subnodeSession.subnodes) != 0

            subnodeSession.subnode()
            


