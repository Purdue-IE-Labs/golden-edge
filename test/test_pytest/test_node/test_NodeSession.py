import sys
import gedge
import pytest
import threading
from threading import Thread
import uuid

from gedge.comm.mock_comm import MockComm
from gedge.node.node import NodeConfig, Tag, Method, NodeSession, TagData
from gedge.node.test_node import TestNodeSession
from gedge.node.subnode import SubnodeConfig
from gedge.node.data_type import DataType
from gedge.node.prop import Props
from gedge.node.tag import WriteResponse
from gedge.node.error import MethodLookupError, TagLookupError
from gedge.proto import Meta
from gedge import proto
from gedge.node.remote import RemoteConnection

from typing import Any, TYPE_CHECKING, Callable, List, Optional, Union

import logging
logger = logging.getLogger(__name__)

class TestSanity:
    def test_init(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            config.key = "something/to/do"

    def test_context_manager(self):
        config = NodeConfig("my/node")

        with NodeSession(config, MockComm()) as session:
            assert session.config == config
            session.close()
    
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

class TestSubnode:
    def test_no_subnode(self):
        config = NodeConfig("my/node")
        subnode_name = "subnode0"

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)

            with pytest.raises(ValueError, match="No subnode subnode0"):
                subSession = session.subnode(subnode_name)

    def test_missing_intermediate(self):
        config = NodeConfig("my/node")

        # Create full nested structure
        s0 = SubnodeConfig("subnode0", config.ks, {}, {}, {})
        s1 = SubnodeConfig("subnode1", s0.ks, {}, {}, {})
        s2 = SubnodeConfig("subnode2", s1.ks, {}, {}, {})
        s3 = SubnodeConfig("subnode3", s2.ks, {}, {}, {})

        # Build subnode hierarchy
        s2.subnodes["subnode3"] = s3
        s1.subnodes["subnode2"] = s2
        s0.subnodes["subnode1"] = s1
        config.subnodes["subnode0"] = s0

        # Remove subnode2 to simulate missing intermediate
        del s1.subnodes["subnode2"]

        with gedge.mock_connect(config) as session:
            session.subnodes["subnode0"] = s0

        # This should fail because subnode2 is missing
        with pytest.raises(ValueError, match="No subnode subnode2"):  # or whatever your error type is
            session.subnode("subnode0/subnode1/subnode2/subnode3")

    def test_bad_name(self):
        config = NodeConfig("my/node")

        s0 = SubnodeConfig("/subnode0", config.ks, {}, {}, {})

        config.subnodes[s0.name] = s0

        with gedge.mock_connect(config) as session:
            session.subnodes[s0.name] = s0

            #Do we want it to just return a value error?
            with pytest.raises(ValueError, match="No subnode "):
                session.subnode(s0.name)

    def test_deep_nested_resolution(self):
        config = NodeConfig("my/node")

        s0 = SubnodeConfig("subnode0", config.ks, {}, {}, {})
        s1 = SubnodeConfig("subnode1", s0.ks, {}, {}, {})
        s2 = SubnodeConfig("subnode2", s1.ks, {}, {}, {})
        s3 = SubnodeConfig("subnode3", s2.ks, {}, {}, {})
        s4 = SubnodeConfig("subnode4", s3.ks, {}, {}, {})

        config.subnodes[s0.name] = s0
        s0.subnodes[s1.name] = s1
        s1.subnodes[s2.name] = s2
        s2.subnodes[s3.name] = s3
        s3.subnodes[s4.name] = s4

        with gedge.mock_connect(config) as session:
            session.subnodes = config.subnodes

            subSession = session.subnode(s0.name)

            subSubSession = subSession.subnode(s1.name)

            subSubSubSession = subSubSession.subnode(s2.name)

            subSubSubSubSession = subSubSubSession.subnode(s3.name)

            subSubSubSubSubSession = subSubSubSubSession.subnode(s4.name)

            assert subSubSubSubSubSession.ks == s4.ks

class TestConnection:
    def test_close_connect(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)

            session.close()

            session.connect_to_remote(config.key)

    def test_double_close(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:

            session.close()

            session.close()

    def test_double_connect(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)

            session.connect_to_remote(config.key)

            assert len(session.connections) == 1

    def test_empty_nodes_on_network(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)

            metas = session.nodes_on_network()

            session.disconnect_from_remote(config.key)
            
            newMetas = session.nodes_on_network()

            assert metas != newMetas
            assert newMetas == []

    def test_empty_print_nodes_on_network(self, capsys):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            
            session.connect_to_remote(config.key)

            session.print_nodes_on_network()

            session.disconnect_from_remote(config.key)
            
            session.print_nodes_on_network()

            captured = capsys.readouterr()
            assert "No Nodes on Network!" in captured.out

    def test_offline_nodes_on_network(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)

            metas = session.nodes_on_network(True)

            commSession = session._comm.session

            commSession._liveliness_tokens[config.key] = False
            
            newMetas = session.nodes_on_network(True)

            assert metas != newMetas
            assert newMetas == []
    
    def test_disconnect_does_not_exist(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)

            with pytest.raises(ValueError, match="Node not/my/node not connected to my/node"):
                session.disconnect_from_remote("not/my/node")

class TestTagBinds:
    def test_no_tag(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            with pytest.raises(TagLookupError, match="Tag no/path not found on node node"):
                tagBind = session.tag_bind("no/path")

    def test_empty_list(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            tagBinds = session.tag_binds([])

            assert tagBinds == []

    def test_different_types(self):
        config = NodeConfig("my/node")
        tag = config.add_tag("tag/path", int)

        with gedge.mock_connect(config) as session:
            tagBind = session.tag_bind(tag.path, 3.5)

            assert tagBind.value == int(3.5)

            print(tagBind.value)
            print(tagBind.tag.type)

class TestState:
    def test_rapid_flip(self):

        def flip(session: TestNodeSession, state: bool):
            state = not state
            session.update_state(state)
            return state
        
        def flip_loop(session: TestNodeSession, state: bool):
            for i in range(0, 100):
                state = flip(session, state)
                
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            a = Thread(target=flip_loop, args=[session, True])
            a.start()
            b = Thread(target=flip_loop, args=[session, False])
            b.start()

            a.join()
            b.join()

            assert session.is_online(session.ks.user_key) == False