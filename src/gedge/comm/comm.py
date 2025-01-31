import base64
import zenoh
from contextlib import contextmanager
from gedge.edge.tag import Tag
from gedge.proto import Meta, TagData, DataType, State
from typing import Any, Callable, List
from gedge.comm import keys

# handle Zenoh communications
# The user will not interact with this item, so we can assume in all functions that zenoh is connected
# TODO: turn the __init__ into the context manager so we don't have to set the session to null initially
class Comm:
    def __init__(self, config: zenoh.Config = zenoh.Config()):
        self.config = config
        self.session: zenoh.Session = None

    def declare_liveliness_token(self, key_expr: str) -> zenoh.LivelinessToken:
        return self.session.liveliness().declare_token(key_expr)

    def declare_liveliness_subscriber(self, key_expr: str, handler: Callable[[zenoh.Sample], None]) -> zenoh.Subscriber:
        return self.session.liveliness().declare_subscriber(key_expr, handler)

    def query_liveliness(self, key_expr: str) -> zenoh.Reply:
        return self.session.liveliness().get(key_expr).recv()

    @contextmanager
    def connect(self):
        with zenoh.open(self.config) as session:
            self.session = session
            yield

    def _send_protobuf(self, key_expr: str, value: Meta | State | Tag):
        b = value.SerializeToString()
        self._put(key_expr, b)

    def _put(self, key_expr: str, payload: bytes):
        b = base64.b64encode(payload)
        self.session.put(key_expr, b)

    # Edge Node functions
    def send_meta(self, key_prefix: str, name: str, meta: Meta):
        key = keys.meta_key_prefix(key_prefix, name)
        print(f"sending meta on key expression: {key}")
        self._send_protobuf(key, meta)
    
    def send_tag(self, key_prefix: str, name: str, key_expr: str, value: TagData):
        key = keys.tag_data_key_expr(key_prefix, name, key_expr)
        print(f"sending tag on key expression: {key}")
        self._send_protobuf(key, value)

    def send_state(self, key_prefix: str, name: str, state: State):
        key = keys.state_key_prefix(key_prefix, name)
        print(f"sending state on key expression: {key}")
        self._send_protobuf(key, state)

    def pull_meta_messages(self, key_prefix: str, only_online: bool = False) -> list[Meta]:
        res = self.session.get(f"{key_prefix}/NODE/*/META")
        messages: list[Meta] = []
        for r in res:
            r: zenoh.Reply
            if not r.ok:
                continue
            result = r.result

            b = base64.b64decode(result.payload.to_bytes())
            try:
                meta = Meta()
                meta.ParseFromString(b)
                is_online = self.is_online(key_prefix, meta.name)
                if only_online and not is_online:
                    continue
                messages.append(meta)
            except Exception as e:
                print(f"couldn't decode {e}")
                print(b)
        return messages

    def pull_meta_message(self, key_prefix: str, name: str) -> Meta:
        reply = self.session.get(f"{key_prefix}/NODE/{name}/META").recv()
        if not reply.ok:
            raise ValueError(f"no meta message for node {name}")
        
        b = base64.b64decode(reply.result.payload.to_bytes())
        meta = Meta()
        meta.ParseFromString(b)
        return meta
            
    def is_online(self, key_prefix: str, name: str) -> bool:
        # this command will fail is no token is declared for this prefix, meaning offline
        try:
            reply = self.session.liveliness().get(keys.liveliness_key_prefix(key_prefix, name)).recv()
            if not reply.ok:
                return False
            return reply.result.kind == zenoh.SampleKind.PUT
        except:
            return False
