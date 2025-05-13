from .comm.mock_comm import MockComm
from .node.node import NodeConfig, NodeSession
from .node.query import MethodQuery
from .node.method import MethodResponse
from .node.data_type import DataType
from .node.method_reply import MethodReply
from .node.tag_write_query import TagWriteQuery
from .node.tag_write_reply import TagWriteReply
from .node.test_node import TestNodeSession
from .node.subnode import SubnodeSession

import logging
import os

level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=level)

ZENOH_PORT = 7447
def connect(config: NodeConfig, *connections: str) -> NodeSession:
    conns = list(connections)
    if len(conns) == 0:
        raise ValueError("Must provide at least one connection point")
    
    # allow for the user to pass in just an IP, we complete the rest
    for i in range(len(conns)):
        if not (conns[i].startswith("tcp/") and conns[i].endswith(f":{ZENOH_PORT}")):
            conns[i] = f"tcp/{conns[i]}:{ZENOH_PORT}"

    return config._connect(conns)

def mock_connect(config: NodeConfig, network: MockComm = None) -> TestNodeSession:
    if network is None:
        session = TestNodeSession(config, MockComm())
    else:    
        session = TestNodeSession(config, network)
    return session
