from gedge.py_proto.singleton import Singleton
from .comm.mock_comm import MockComm
from .node.node import NodeConfig, NodeSession
from .node.test_node import TestNodeSession

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

def mock_connect(config: NodeConfig) -> TestNodeSession:
    session = TestNodeSession(config, MockComm())
    return session

def use_models(model_dir: str):
    Singleton().set_model_dir(model_dir)