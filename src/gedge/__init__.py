from .node.node import NodeConfig, NodeSession
from .node.query import Query
from .node.method import Response

def connect(config: NodeConfig) -> NodeSession:
    return config.connect()
