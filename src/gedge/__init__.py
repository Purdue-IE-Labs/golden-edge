from .edge.edge import EdgeNodeConfig, EdgeNodeSession
from .app.app import AppConfig, AppSession 
from contextlib import contextmanager
from typing import Generator

@contextmanager
def connect(config: AppConfig | EdgeNodeConfig) -> Generator[AppSession | EdgeNodeSession, None, None]:
    with config.connect() as session:
        yield session