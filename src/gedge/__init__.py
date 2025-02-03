from .edge.edge import EdgeNodeConfig, EdgeNodeSession
from .app.app import AppConfig, AppSession 

from typing import overload

@overload
def connect(config: EdgeNodeConfig) -> EdgeNodeSession:
    return config.connect()

@overload
def connect(config: AppConfig) -> AppSession:
    return config.connect()

def connect(config):
    return config.connect()