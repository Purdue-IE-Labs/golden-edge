import zenoh
from contextlib import contextmanager
from proto.meta_pb2 import Meta

# handle Zenoh communications
# The user will not interact with this item, so we can assume in all functions that it is connected
class Comm:
    def __init__(self, key_prefix: str, config: zenoh.Config = zenoh.Config()):
        self._meta_key = ""
        self._key_prefix = key_prefix
        self.config = config
        self.session = None

    @property
    def key_prefix(self):
        return self._key_prefix
    
    @key_prefix.setter
    def key_prefix(self, value):
        self.key_prefix = value
        self._meta_key = value + "/" + "META"

    @contextmanager
    def connect(self):
        session = zenoh.open(self.config)    
        self.session = session
        yield session
        session.close()

    def send_meta(self, meta: Meta):
        res = self.session.put(self._meta_key, meta.SerializeToString())
        print(res)
    
    def send_tag(self):
        pass

    def send_state(self):
        pass

    