import zenoh
from contextlib import contextmanager
from gedge.edge.tag import Tag
from gedge.proto import Meta, TagData, DataType

# handle Zenoh communications
# The user will not interact with this item, so we can assume in all functions that it is connected
class Comm:
    def __init__(self, key_prefix: str, name: str, config: zenoh.Config = zenoh.Config()):
        self._meta_key = ""
        self._key_prefix = key_prefix.strip("/")
        self.name = name
        self._set_keys(self._key_prefix)
        self.config = config
        self.session = None

    @property
    def key_prefix(self):
        return self._key_prefix
    
    @key_prefix.setter
    def key_prefix(self, value: str):
        value = value.strip("/")
        self._key_prefix = value
        self._set_keys(value)

    def _set_keys(self, prefix: str):
        self._node_key = prefix + f"/NODE/{self.name}"
        self._meta_key = self._node_key + "/META"
        self._tag_key_prefix = self._node_key + "/TAGS"
        self._tag_data_key_prefix = self._tag_key_prefix + "/DATA"
        self._tag_write_key_prefix = self._tag_key_prefix + "/WRITES"
        self._state_key = self._node_key + "/STATE"

    @contextmanager
    def connect(self):
        session = zenoh.open(self.config)    
        self.session = session
        yield session
        session.close()

    def send_meta(self, meta: Meta):
        res = self.session.put(self._meta_key, meta.SerializeToString())
        print(res)
    
    def send_tag(self, tag: Tag, value: TagData, key: str):
        res = self.session.put(self._tag_key_prefix + "/" + key.strip("/"), value.SerializeToString())
        print(res)

    def send_state(self):
        pass

    