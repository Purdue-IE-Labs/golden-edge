from .edge.edge import EdgeNodeConfig, EdgeNodeSession
from .app.app import AppConfig, AppSession 
from .node.node import NodeConfig, NodeSession
from .node.remote import RemoteConfig, RemoteConnection

from typing import overload

@overload
def connect(config: EdgeNodeConfig) -> EdgeNodeSession:
    return config.connect()

@overload
def connect(config: AppConfig) -> AppSession:
    return config.connect()

@overload
def connect(config: NodeConfig) -> NodeSession:
    return config.connect()

def connect(config):
    return config.connect()