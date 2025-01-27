from contextlib import contextmanager
from gedge.comm import Comm
from gedge.proto import State, Meta, TagData
from typing import Callable, List, Tuple, TypeAlias, TypeVar
import zenoh

class AppConfig:
    def __init__(self, key_prefix: str, name: str):
        self.key_prefix = key_prefix
        self.name = name

    @contextmanager
    def connect(self):
        comm = Comm(self.key_prefix, self.name)
        with comm.connect():
            yield AppSession(config=self, comm=comm)

StateCallback: TypeAlias = Callable[[State], None]
MetaCallback: TypeAlias = Callable[[Meta], None]
TagDataCallback: TypeAlias = Callable[[TagData], None]
Callbacks: TypeAlias = Tuple[StateCallback, MetaCallback, TagDataCallback]
class AppSession:
    def __init__(self, config: AppConfig, comm: Comm):
        self._comm = comm
        self.config = config

    def print_nodes_on_network(self):
        pass

    def pull_meta_messages(self):
        # if node not in self.nodes:
        #     raise ValueError("invalid node")
        res = self._comm.session.get(self.config.key_prefix + f"/NODE/**/META")
        # print(f"meta messages: {len(res)}")
        for r in res:
            r: zenoh.Reply
            b = r.result.payload.to_bytes().replace(b"\r", b"")
            node_name = self._comm.node_name_from_key_expr(str(r.result.key_expr))
            try:
                meta = Meta()
                meta.ParseFromString(b)
                print(node_name, meta)
            except Exception as e:
                print(f"couldn't decode {e}")
    
    def _on_state_default(self):
        pass

    def _on_meta_default(self):
        pass

    def _on_tag_data_default(self):
        pass

    def connect_to_node(self, name: str, on_state: StateCallback, on_meta: MetaCallback, tag_data_callbacks: dict[str, TagDataCallback]):
        self._comm.name = name
        def _on_state(sample: zenoh.Sample):
            payload = sample.payload.to_bytes().replace(b"\r", b"")
            state = State()
            state.ParseFromString(payload)
            on_state(state)

        def _on_meta(sample: zenoh.Sample):
            payload = sample.payload.to_bytes().replace(b"\r", b"")
            meta = Meta()
            meta.ParseFromString(payload)
            on_meta(meta)
        
        for tag_key_prefix in tag_data_callbacks:
            self.add_tag_data_callback(name, tag_key_prefix, tag_data_callbacks[tag_key_prefix])

        # self._comm.session.declare_subscriber(self.config.key_prefix + f"/NODE/{name}/STATE", _on_state)
        # self._comm.session.declare_subscriber(self.config.key_prefix + f"/NODE/{name}/META", _on_meta)
        self._comm.session.declare_subscriber(self._comm._state_key_prefix, _on_state)
        self._comm.session.declare_subscriber(self._comm._meta_key_prefix, _on_meta)
        self._comm.name = self.config.name
    
    def add_tag_data_callback(self, name: str, tag_key_prefix: str, on_tag_data: TagDataCallback):
        # key_expr = self.config.key_prefix + f"/NODE/{name}/TAGS/DATA/{tag_key_prefix}"
        def _on_tag_data(sample: zenoh.Sample):
            payload = sample.payload.to_bytes().replace(b"\r", b"")
            tag_data = TagData()
            tag_data.ParseFromString(payload)
            on_tag_data(tag_data)
        self._comm.session.declare_subscriber(self._comm._tag_data_key_prefix + f"/{tag_key_prefix}", _on_tag_data)
