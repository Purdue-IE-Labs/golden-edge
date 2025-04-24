import gedge
import pytest

from gedge.comm.mock_comm import MockComm
from gedge.node.node import NodeConfig, Tag, Method, NodeSession
from gedge.node.subnode import SubnodeConfig
from gedge.node.data_type import DataType
from gedge.node.prop import Props
from gedge.node.tag import WriteResponse
from gedge.node.error import MethodLookupError, TagLookupError
from gedge.proto import Meta
from gedge import proto

class TestSanity:
    def test_init(self):
        instance_str = "instance/str"
        nodeConfig_instance = NodeConfig(instance_str)
        nodeSession = NodeSession(nodeConfig_instance, comm=MockComm())



def test_close():
    #TODO
    pytest.fail("Test has not been created")

def test_on_remote_close():
    #TODO
    pytest.fail("Test has not been created")

def test_is_online():
    #TODO
    pytest.fail("Test has not been created")

def test_node_on_network():
    #TODO
    pytest.fail("Test has not been created")

def test_nodes_on_network():
    #TODO
    pytest.fail("Test has not been created")

def test_print_nodes_on_network():
    #TODO
    pytest.fail("Test has not been created")

def test_connect_to_remote():
    #TODO
    pytest.fail("Test has not been created")

def test_disconnect_from_remote():
    #TODO
    pytest.fail("Test has not been created")

def test_verify_node_collision():
    #TODO
    pytest.fail("Test has not been created")

def test_startup():
    #TODO
    pytest.fail("Test has not been created")

def test_tag_bind():
    #TODO
    pytest.fail("Test has not been created")

def test_tag_binds():
    #TODO
    pytest.fail("Test has not been created")

def test_update_tag():
    #TODO
    pytest.fail("Test has not been created")

def test_update_state():
    #TODO
    pytest.fail("Test has not been created")

def test_subnode():
    #TODO
    pytest.fail("Test has not been created")