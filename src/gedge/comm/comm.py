import zenoh
from contextlib import contextmanager
from gedge.edge.tag import Tag
from gedge.proto import Meta, TagData, DataType, State
from typing import Callable

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
        self._set_keys()

    @property
    def key_prefix(self):
        return self._key_prefix
    
    @key_prefix.setter
    def key_prefix(self, value: str):
        value = value.strip("/")
        self._key_prefix = value
        self._set_keys()

    def _set_keys(self):
        self._node_key_prefix = self.node_key_prefix(self.key_prefix, self.name)
        self._meta_key_prefix = self.meta_key_prefix(self.key_prefix, self.name)
        self._tag_data_key_prefix = self.tag_data_key_prefix(self.key_prefix, self.name)
        self._tag_write_key_prefix = self.tag_write_key_prefix(self.key_prefix, self.name)
        self._state_key_prefix = self.state_key_prefix(self.key_prefix, self.name)

    def node_key_prefix(self, prefix: str, name: str):
        node_key_prefix = prefix + f"/NODE/{name}"
        return node_key_prefix

    def meta_key_prefix(self, prefix: str, name: str):
        meta_key_prefix = prefix + f"/NODE/{name}/META"
        return meta_key_prefix

    def tag_data_key_prefix(self, prefix: str, name: str):
        return self.node_key_prefix(prefix, name) + "/TAGS/DATA"
    
    def tag_write_key_prefix(self, prefix: str, name: str):
        return self.node_key_prefix(prefix, name) + "/TAGS/WRITE"
    
    def state_key_prefix(self, prefix: str, name: str):
        return self.node_key_prefix(prefix, name) + "/STATE"

    def liveliness_key_prefix(self, prefix: str, name: str):
        return self.node_key_prefix(prefix, name)
    
    def node_name_from_key_expr(self, key_expr: str | zenoh.KeyExpr):
        components = str(key_expr).split("/")
        return components[components.index("NODE") + 1]
    
    def declare_liveliness_token(self) -> zenoh.LivelinessToken:
        print(f"declaring liveliness token on {self._node_key_prefix}")
        return self.session.liveliness().declare_token(self._node_key_prefix)

    def declare_liveliness_subscriber(self, handler: Callable[[zenoh.Sample], None]) -> zenoh.Subscriber:
        print(f"declaring subscriber of liveliness of {self._node_key_prefix}")
        return self.session.liveliness().declare_subscriber(self._node_key_prefix, handler)

    def query_liveliness(self, key_expr: str) -> zenoh.Reply:
        return self.session.liveliness().get(key_expr).recv()

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

    def pull_meta_messages(self, only_online: bool = False) -> dict[str, Meta]:
        res = self.session.get(f"{self.key_prefix}/NODE/*/META")
        messages = {}
        for r in res:
            r: zenoh.Reply
            if not r.ok:
                continue
            result = r.result

            b = result.payload.to_bytes().replace(b"\r", b"")
            node_name = self.node_name_from_key_expr(result.key_expr)
            try:
                meta = Meta()
                meta.ParseFromString(b)
                messages[node_name] = meta
            except Exception as e:
                print(f"couldn't decode {e}")
        return messages
            
    def is_online(self, name: str) -> bool:
        # this command will fail is no token is declared for this prefix, meaning offline
        try:
            reply = self.session.liveliness().get(self.node_key_prefix(self.key_prefix, name)).recv()
            if not reply.ok:
                return False
            return reply.result.kind == zenoh.SampleKind.PUT
        except:
            return False
