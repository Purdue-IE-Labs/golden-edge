import gedge
import pytest

import uuid

from gedge.comm.mock_comm import MockComm
from gedge.node.node import NodeConfig, Tag, Method, NodeSession
from gedge.node.subnode import SubnodeConfig
from gedge.node.data_type import DataType
from gedge.node.prop import Props
from gedge.node.tag import WriteResponse
from gedge.node.error import MethodLookupError, TagLookupError
from gedge.proto import Meta
from gedge import proto
from gedge.node.remote import RemoteConnection

class TestSanity:
    def test_init(self, capsys):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            config.key = "something/to/do"
    
    def test_close(self, capsys):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.close()
            captured = capsys.readouterr()
            assert "Closing session" in captured.out

    def test_on_remote_close(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)
            
            assert len(session.connections) != 0
            
            session._on_remote_close(config.key)

            assert len(session.connections) == 0

    @pytest.mark.skip
    def test_is_online(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)
            
            assert session.is_online(config.key) == True

    def test_node_on_network(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)

            meta = session.node_on_network(config.key)

            assert isinstance(meta, Meta)
            assert meta.key == config.key

    # If we want to implement this we need to be able to use a Zenoh like way of retrieving nodes with wildcarding
    @pytest.mark.skip
    def test_nodes_on_network(self):
        config = NodeConfig("my/node")

        with gedge.mock_connect(config) as session:
            session.connect_to_remote(config.key)

            metas = session.nodes_on_network(only_online=False)

            assert isinstance(metas, list)
            assert len(metas) > 0
            assert isinstance(metas[0], Meta)
            assert metas[0].key == config.key

    # Same issue as nodes_on_network
    @pytest.mark.skip
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

            print(session.connections)

            session.disconnect_from_remote(config.key)

            assert len(session.connections) == 0


            

            

