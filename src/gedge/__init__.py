from .node.node import NodeConfig, NodeSession

def connect(config: NodeConfig) -> NodeSession:
    return config.connect()
