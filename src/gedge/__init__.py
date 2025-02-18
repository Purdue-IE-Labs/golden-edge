from .node.node import NodeConfig, NodeSession
from .node.query import Query
from .node.method import Response
from .edge.data_type import DataType

def connect(config: NodeConfig) -> NodeSession:
    return config.connect()
