import zenoh
from contextlib import contextmanager
from gedge.edge.tag import Tag
from gedge.proto import Meta, TagData, DataType, State

# handle Zenoh communications
# The user will not interact with this item, so we can assume in all functions that zenoh is connected
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
        self._node_key_prefix = prefix + f"/NODE/{self.name}"
        self._meta_key_prefix = self._node_key_prefix + "/META"
        self._tag_key_prefix = self._node_key_prefix + "/TAGS"
        self._tag_data_key_prefix = self._tag_key_prefix + "/DATA"
        self._tag_write_key_prefix = self._tag_key_prefix + "/WRITES"
        self._state_key_prefix = self._node_key_prefix + "/STATE"
    
    def declare_liveliness_token(self) -> zenoh.LivelinessToken:
        return self.session.liveliness().declare_token(self._node_key_prefix)

    @contextmanager
    def connect(self):
        with zenoh.open(self.config) as session:
            self.session = session
            yield

    def send_meta(self, meta: Meta):
        res = self.session.put(self._meta_key_prefix, meta.SerializeToString())
        print(res)
    
    def send_tag(self, value: TagData, key_expr: str):
        res = self.session.put(self._tag_data_key_prefix + "/" + key_expr.strip("/"), value.SerializeToString())
        print(res)

    def send_state(self, state: State):
        res = self.session.put(self._state_key_prefix, state.SerializeToString())
        print(res)
    