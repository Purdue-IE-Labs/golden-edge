from .edge.edge import EdgeNodeConfig, EdgeNodeSession
from .app.app import AppConfig, AppSession 

def connect(config: AppConfig | EdgeNodeConfig) -> AppSession | EdgeNodeSession:
    return config.connect()
