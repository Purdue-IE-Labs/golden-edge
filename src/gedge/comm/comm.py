import zenoh
from contextlib import contextmanager
from gedge.edge.tag import Tag
from gedge.proto import Meta, TagData, DataType, State

# handle Zenoh communications
# The user will not interact with this item, so we can assume in all functions that zenoh is connected
# TODO: turn the __init__ into the context manager so we don't have to set the session to null initially
class Comm:
    def __init__(self, key_prefix: str, name: str, config: zenoh.Config = zenoh.Config()):
        self._key_prefix = key_prefix.strip("/")
        self._name = name
        self._set_keys(self._key_prefix)
        self.config = config
        self.session: zenoh.Session = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
        self._set_keys(self.key_prefix)

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
    
    def node_name_from_key_expr(self, key_expr: str):
        components = key_expr.split("/")
        return components[components.index("NODE") + 1]
    
    def declare_liveliness_token(self) -> zenoh.LivelinessToken:
        return self.session.liveliness().declare_token(self._node_key_prefix)

    @contextmanager
    def connect(self):
        with zenoh.open(self.config) as session:
            self.session = session
            yield

    # Edge Node functions
    def send_meta(self, meta: Meta):
        b = meta.SerializeToString()
        print(f"sending meta on key expression: {self._meta_key_prefix}")
        res = self.session.put(self._meta_key_prefix, b)
    
    def send_tag(self, value: TagData, key_expr: str):
        key_expr = self._tag_data_key_prefix + "/" + key_expr.strip("/")
        print(f"sending tag on key expression: {key_expr}")
        res = self.session.put(key_expr, value.SerializeToString())

    def send_state(self, state: State):
        print(f"sending state on key expression: {self._state_key_prefix}")
        res = self.session.put(self._state_key_prefix, state.SerializeToString())

    def pull_meta_messages(self) -> list[Meta]:
        res = self.session.get("**/META/**")