from .node.node import NodeConfig, NodeSession
from .node.query import Query
from .node.method import Response
from .edge.data_type import DataType

import logging
import os

level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=level)

def connect(config: NodeConfig) -> NodeSession:
    return config.connect()
