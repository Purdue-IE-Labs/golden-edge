import sys
import gedge
import pytest

import uuid

from gedge.comm.mock_comm import MockComm
from gedge.node.node import NodeConfig, Tag, Method, NodeSession, TagData
from gedge.node.subnode import SubnodeConfig
from gedge.node.data_type import DataType
from gedge.node.prop import Props
from gedge.node.tag import WriteResponse
from gedge.node.error import MethodLookupError, TagLookupError
from gedge.proto import Meta
from gedge import proto
from gedge.node.remote import RemoteConnection

import logging
logger = logging.getLogger(__name__)

class TestSanity:
    def test_init(self, capsys):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            config.key = "something/to/do"
    
    def test_close(self, capsys):
        config = NodeConfig("my/node")

         # Attach a stdout handler to the logger temporarily
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)

        logger = logging.getLogger()  # or the specific logger you use
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        try:
            with gedge.mock_connect(config) as session:
                session.close()
                captured = capsys.readouterr()
                assert "Closing session" in captured.out
        finally:
            logger.removeHandler(handler)

    def test_on_remote_close(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)
            
            assert len(session.connections) != 0
            
            session._on_remote_close(config.key)

            assert len(session.connections) == 0

    # @pytest.mark.skip
    def test_is_online(self):
        # pytest.fail("Mock Comm liveliness query hasn't been implemented yet")
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)
            
            assert session.is_online(config.key) == True

    def test_is_offline(self):
        # pytest.fail("Mock Comm liveliness query hasn't been implemented yet")
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)
            
            assert session.is_online(config.key) == True

            session.disconnect_from_remote(config.key)

            assert session.is_online(config.key) == False

    def test_node_on_network(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)

            meta = session.node_on_network(config.key)

            assert isinstance(meta, Meta)
            assert meta.key == config.key

    # If we want to implement this we need to be able to use a Zenoh 
    # like way of retrieving nodes with wildcarding
    # @pytest.mark.skip
    def test_nodes_on_network(self):
        # pytest.fail("Mock Comm.pull_meta_messages isn't implemented")
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)

            metas = session.nodes_on_network(only_online=False)

            assert isinstance(metas, list)
            assert len(metas) > 0
            assert isinstance(metas[0], Meta)
            assert metas[0].key == config.key

    # Same issue as nodes_on_network
    # @pytest.mark.skip
    def test_print_nodes_on_network(self, capsys):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)

            session.print_nodes_on_network()
            captured = capsys.readouterr()
            assert "Nodes on Network:" in captured.out

    def test_connect_to_remote(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            assert len(session.connections) == 0
            
            session.connect_to_remote(config.key)

            assert len(session.connections) == 1
            assert session.connections.get(config.key).key == config.key
            assert str(session.connections.get(config.key).ks) == str(config.ks)

    def test_disconnect_from_remote(self, capsys):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            assert len(session.connections) == 0
            
            session.connect_to_remote(config.key)

            assert len(session.connections) == 1

            session.disconnect_from_remote(config.key)

            assert len(session.connections) == 0

    @pytest.mark.skip
    def test_verify_node_collision(self):
        pytest.fail("Mock Comm.pull_meta_messages isn't implemented")

    @pytest.mark.skip
    def test_startup(self):
        pytest.fail("Dependent on _verify_node_collision")

    def test_tag_binds(self):
        config = NodeConfig("my/node")
        tag = config.add_tag("tag/path", int)
        otherTag = config.add_tag("tag/2nd/path", float)
        
        with gedge.mock_connect(config) as session:
            tagPathList = []
            tagList = []
            
            for key, tag_item in config.tags.items():
                tagPathList.append(tag_item.path)
                tagList.append(tag_item)
            
            tagBinds = session.tag_binds(tagPathList)

            for index in range(0, len(config.tags)):
                assert tagBinds[index].path == tagList[index].path


    def test_tag_bind(self):
        config = NodeConfig("my/node")
        tag = config.add_tag("tag/path", int)
        
        with gedge.mock_connect(config) as session:
            tagBind = session.tag_bind(tag.path)

            newTagBind = session.tag_bind(tagBind.path, 10)

            assert tagBind.value != newTagBind.value
            assert tagBind.path == newTagBind.path

    def test_update_tag(self):
        config = NodeConfig("my/node")
        tag = config.add_tag("tag/path", int)

        with gedge.mock_connect(config) as session:
            commSession = session._comm.session

            tag_key_expr = session.ks.tag_data_path(tag.path)
            
            firstTagGet = commSession.get(tag_key_expr)
            
            session.update_tag(tag.path, 10)
            
            tagGet = commSession.get(tag_key_expr)

            assert firstTagGet != tagGet

    def test_update_state(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)

            assert session.is_online(session.ks.user_key) == True

            session.update_state(False)

            assert session.is_online(session.ks.user_key) == False

            session.update_state(True)

            assert session.is_online(session.ks.user_key) == True

    def test_subnode(self):
        from gedge.node.subnode import SubnodeSession
        config = NodeConfig("my/node")
        subnode_name = "subnode0"
        subnode = SubnodeConfig(subnode_name, config.ks, {}, {}, {})
        config.subnodes[subnode_name] = subnode

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)

            session.subnodes[subnode_name] = subnode

            subSession = session.subnode(subnode_name)

            assert isinstance(subSession, SubnodeSession)
            assert subSession.ks == subnode.ks
            assert subSession._comm is session._comm