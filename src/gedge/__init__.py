from .node.node import NodeConfig, NodeSession
from .node.query import MethodQuery
from .node.method import MethodResponse
from .node.data_type import DataType
from .node.method_reply import MethodReply
from .node.tag_write_query import TagWriteQuery
from .node.tag_write_reply import TagWriteReply

import logging
import os

level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=level)

def connect(config: NodeConfig, *connections: str) -> NodeSession:
    conns = list(connections)
    if len(conns) == 0:
        raise ValueError("Must provide at least one connection point")
    return config._connect(conns)
