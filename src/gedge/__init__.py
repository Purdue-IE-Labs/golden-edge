import pathlib
from gedge.node.codes import OK, ERR, CALLBACK_ERR
from gedge.node.gtypes import TagGroupValue, TagBaseValue
from gedge.node.method_response import ResponseConfig, ResponseType
from gedge.node.query import MethodQuery, TagWriteQuery
from gedge.node.reply import Response
from gedge.py_proto.singleton import Singleton
from gedge.py_proto.state import State
from gedge.py_proto.meta import Meta
from .comm.mock_comm import MockComm
from .node.node import NodeConfig, NodeSession
from .node.test_node import TestNodeSession

import logging
import os

level = os.environ.get("LOG_LEVEL", "INFO").upper()
try:
    logging.basicConfig(level=level)
except:
    logging.basicConfig(level="NOTSET")

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
    if not pathlib.Path(model_dir).exists():
        raise ValueError(f"model directory {model_dir} does not exist")
    Singleton().set_model_dir(model_dir)