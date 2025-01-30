import base64
from contextlib import contextmanager
from gedge.comm import Comm
from gedge.proto import State, Meta, TagData
from typing import Callable, List, Tuple, TypeAlias, TypeVar, Any
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
LivelinessCallback: TypeAlias = Callable[[bool, str], None]
Callbacks: TypeAlias = Tuple[StateCallback, MetaCallback, TagDataCallback]
class AppSession:
    def __init__(self, config: AppConfig, comm: Comm):
        self._comm = comm
        self.config = config
        self.nodes: dict[str, List[zenoh.Subscriber]] = {}

    def print_nodes_on_network(self, print_meta: bool = False):
        print("Nodes on network")
        messages = self.pull_meta_messages()
        for name, meta in messages.items():
            is_online = self._comm.is_online(name)
            print(f"\t{name}, {"online" if is_online else "offline"}")
            if print_meta:
                print(f"\t{meta}")

    def print_nodes_connected_to_app(self, print_meta: bool = False):
        print("Nodes connected to application")
        for name in self.nodes:
            print(name)

    def pull_meta_messages(self) -> dict[str, Meta]:
        messages = self._comm.pull_meta_messages()
        return messages
    
    def _on_state_default(self):
        pass

    def _on_meta_default(self):
        pass

    def _on_tag_data_default(self):
        pass

    def _on_liveliness_default(self):
        pass

    def connect_to_node(self, name: str, on_state: StateCallback = None, on_meta: MetaCallback = None, on_liveliness_change: LivelinessCallback = None, tag_data_callbacks: dict[str, TagDataCallback] = {}):
        print(f"connecting to node {name}")
        handlers = []
        def _on_state(sample: zenoh.Sample):
            payload = base64.b64decode(sample.payload.to_bytes())
            state = State()
            state.ParseFromString(payload)
            on_state(state)
            if not state.online:
                self.disconnect_from_node(name)

        def _on_meta(sample: zenoh.Sample):
            payload = base64.b64decode(sample.payload.to_bytes())
            meta = Meta()
            meta.ParseFromString(payload)
            on_meta(meta)

        def _on_liveliness(sample: zenoh.Sample):
            if sample.kind == zenoh.SampleKind.PUT:
                print(f"node {sample.key_expr} online")
            elif sample.kind == zenoh.SampleKind.DELETE:
                print(f"node {sample.key_expr} went offline")
            is_online = sample.kind == zenoh.SampleKind.PUT
            on_liveliness_change(is_online, name)
            if not is_online:
                self.disconnect_from_node(name)
        
        for tag_key_prefix in tag_data_callbacks:
            subscriber = self.add_tag_data_callback(name, tag_key_prefix, tag_data_callbacks[tag_key_prefix])
            handlers.append(subscriber)

        if on_state:
            key_expr = self._comm.state_key_prefix(self.config.key_prefix, name)
            subscriber = self._comm.session.declare_subscriber(key_expr, _on_state)
            handlers.append(subscriber)
        if on_meta:
            key_expr = self._comm.meta_key_prefix(self.config.key_prefix, name)
            subscriber = self._comm.session.declare_subscriber(key_expr, _on_meta)
            handlers.append(subscriber)
        if on_liveliness_change:
            key_expr = self._comm.liveliness_key_prefix(self.config.key_prefix, name)
            subscriber = self._comm.declare_liveliness_subscriber(_on_liveliness)
            handlers.append(subscriber)
        self.nodes[name] = handlers

    def disconnect_from_node(self, name: str):
        if name not in self.nodes:
            raise IndexError(f"{name} not connected")
        handlers = self.nodes[name]
        for h in handlers:
            h.undeclare()
        del self.nodes[name]
    
    def add_tag_data_callback(self, name: str, tag_key_prefix: str, on_tag_data: TagDataCallback) -> zenoh.Subscriber:
        def _on_tag_data(sample: zenoh.Sample):
            payload = base64.b64decode(sample.payload.to_bytes())
            tag_data = TagData()
            tag_data.ParseFromString(payload)
            on_tag_data(tag_data)
        key_expr = self._comm.tag_data_key_expr(self.config.key_prefix, self.config.name, tag_key_prefix)
        subscriber = self._comm.session.declare_subscriber(key_expr, _on_tag_data)
        return subscriber

    def close(self):
        self._comm.session.close()
