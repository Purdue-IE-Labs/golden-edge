from contextlib import contextmanager
from gedge.comm import Comm

class AppConfig:
    def __init__(self):
        pass
    
    def print_nodes_on_network(self):
        pass

    def pull_meta_messages(self):
        pass

    def connect_to_edge_node(self):
        pass

    @contextmanager
    def connect(self):
        comm = Comm()
        with comm.connect():
            yield

class AppSession:
    def print_nodes_on_network(self):
        pass

    def pull_meta_messages(self):
        pass

    def connect_to_node(self):
        pass

@contextmanager
def connect(config: AppConfig):
    with config.connect():
        yield