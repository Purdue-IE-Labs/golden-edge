import pytest

import gedge

from gedge.node.node import NodeConfig
from gedge.node.subnode import SubnodeConfig, SubnodeSession, RemoteSubConnection
from gedge.node.tag import Tag
from gedge.node.data_type import DataType
from gedge.node.prop import Props
from gedge.comm.mock_comm import MockComm

import logging

logger = logging.getLogger(__file__)

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

            subSubnodeSession = subnodeSession.subnode(subSubnode.name)

            assert subSubnodeSession.config == subSubnode
            assert subSubnodeSession.ks == subSubnode.ks
            assert subSubnodeSession.tags == subSubnode.tags
            assert subSubnodeSession.methods == subSubnode.methods
            assert subSubnodeSession.subnodes == subSubnode.subnodes

        def test_close(self):
            parent = NodeConfig("my/name")
            subnode = SubnodeConfig("subnode", parent.ks, {}, {}, {})

            subnodeSession = SubnodeSession(subnode, MockComm())

            subnodeSession.close()

            assert subnodeSession.nodes_on_network() == []

class TestRemoteSubConnection:
    class TestSanity:
        def test_init(self):
            parent = NodeConfig("my/node")
            subnode = SubnodeConfig("subnode", parent.ks, {}, {}, {})
            parent.subnodes[subnode.name] = subnode
            remote = RemoteSubConnection("connection", subnode.ks, subnode, MockComm(), subnode.name)

            assert remote.key == "connection"
            assert remote.ks == subnode.ks
            assert remote.node_id == subnode.name

        def test_subnode_no_slash(self):
            parent = NodeConfig("my/node")
            subnode = SubnodeConfig("subnode", parent.ks, {}, {}, {})
            parent.subnodes[subnode.name] = subnode
            subnode0 = SubnodeConfig("subnode0", parent.ks, {}, {}, {})
            subnode.subnodes[subnode0.name] = subnode0
            remote = RemoteSubConnection("connection", subnode.ks, subnode, MockComm(), subnode.name)

            remote.subnodes[subnode0.name] = subnode0

            subRemote = remote.subnode(subnode0.name)

            assert subRemote.node_id == remote.node_id
            assert subRemote.key == subnode0.name

        def test_subnode_slash(self):
            parent = NodeConfig("my/node")
            subnode = SubnodeConfig("subnode", parent.ks, {}, {}, {})
            parent.subnodes[subnode.name] = subnode
            subnode0 = SubnodeConfig("subnode0", parent.ks, {}, {}, {})
            subnode.subnodes[subnode0.name] = subnode0
            subnode1 = SubnodeConfig("subnode1", parent.ks, {}, {}, {})
            subnode0.subnodes[subnode1.name] = subnode1
            remote = RemoteSubConnection("connection", subnode.ks, subnode, MockComm(), subnode.name)

            remote.subnodes[subnode0.name] = subnode0

            subRemote = remote.subnode("subnode0/subnode1")

            assert subRemote.key == "subnode0/subnode1"
            assert subRemote.node_id == remote.node_id

        def test_close(self, caplog):
            parent = NodeConfig("my/node")
            subnode = SubnodeConfig("subnode", parent.ks, {}, {}, {})
            parent.subnodes[subnode.name] = subnode
            remote = RemoteSubConnection("connection", subnode.ks, subnode, MockComm(), subnode.name)

            with caplog.at_level(logging.WARNING):
                remote.close()

            assert "Cannot close a remote subnode connection" in caplog.text

    class TestEmpty:
        def test_subnode_slash(self):
            parent = NodeConfig("my/node")
            subnode = SubnodeConfig("subnode", parent.ks, {}, {}, {})
            parent.subnodes[subnode.name] = subnode
            subnode0 = SubnodeConfig("subnode0", parent.ks, {}, {}, {})
            subnode.subnodes[subnode0.name] = subnode0
            
            remote = RemoteSubConnection("connection", subnode.ks, subnode, MockComm(), subnode.name)

            remote.subnodes[subnode0.name] = subnode0

            with pytest.raises(ValueError, match="No subnode "):
                subRemote = remote.subnode("subnode0/")

        def test_subnode_no_slash(self):
            parent = NodeConfig("my/node")
            subnode = SubnodeConfig("subnode", parent.ks, {}, {}, {})
            parent.subnodes[subnode.name] = subnode
            subnode0 = SubnodeConfig("subnode0", parent.ks, {}, {}, {})
            subnode.subnodes[subnode0.name] = subnode0
            remote = RemoteSubConnection("connection", subnode.ks, subnode, MockComm(), subnode.name)

            remote.subnodes[subnode0.name] = subnode0

            with pytest.raises(ValueError, match="No subnode subnode1"):
                subRemote = remote.subnode("subnode1")
            
            
            


