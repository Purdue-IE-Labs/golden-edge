import base64
from contextlib import contextmanager
from gedge.comm import Comm
from gedge.edge.tag import Tag
from gedge.proto import State, Meta, TagData
from typing import Callable, List, Tuple, TypeAlias, TypeVar, Any
import zenoh
from collections import defaultdict
from gedge.comm import keys

class AppConfig:
    def __init__(self, key_prefix: str, name: str):
        self.key_prefix = key_prefix
        self.name = name

    def connect(self):
        comm = Comm()
        return AppSession(config=self, comm=comm)

StateCallback: TypeAlias = Callable[[str, str, State], None]
MetaCallback: TypeAlias = Callable[[str, str, Meta], None]
TagDataCallback: TypeAlias = Callable[[str, str, Any], None]
LivelinessCallback: TypeAlias = Callable[[str, bool], None]
Callbacks: TypeAlias = Tuple[StateCallback, MetaCallback, TagDataCallback]
class AppSession:
    def __init__(self, config: AppConfig, comm: Comm):
        self._comm = comm
        self.config = config
        self.nodes: dict[str, List[zenoh.Subscriber]] = defaultdict(list) 
    
    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        self._comm.__exit__(*exc)

    def nodes_on_network(self, only_online: bool = False) -> list[Meta]:
        return self.pull_meta_messages(only_online)

    def print_nodes_on_network(self, only_online: bool = False):
        messages = self.pull_meta_messages(only_online=only_online)
        if len(messages) == 0:
            print("No Nodes on Network!")
            return
        print("Nodes on Network:")
        i = 1
        for meta in messages:
            print(f"{i}. {meta.name}: {"online" if self._comm.is_online(self.config.key_prefix, meta.name) else "offline"}")
            print(f"{meta}\n")
            i += 1

    def pull_meta_messages(self, only_online: bool) -> list[Meta]:
        return self._comm.pull_meta_messages(self.config.key_prefix, only_online)
    
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
        state_key_expr = keys.state_key_prefix(self.config.key_prefix, name)
        def _on_state(sample: zenoh.Sample):
            payload = base64.b64decode(sample.payload.to_bytes())
            state = State()
            state.ParseFromString(payload)
            on_state(name, state_key_expr, state)
            # if not state.online:
            #     self.disconnect_from_node(name)

        meta_key_expr = keys.meta_key_prefix(self.config.key_prefix, name)
        def _on_meta(sample: zenoh.Sample):
            payload = base64.b64decode(sample.payload.to_bytes())
            meta = Meta()
            meta.ParseFromString(payload)
            on_meta(name, meta_key_expr, meta)

        def _on_liveliness(sample: zenoh.Sample):
            if sample.kind == zenoh.SampleKind.PUT:
                print(f"node {sample.key_expr} online")
            elif sample.kind == zenoh.SampleKind.DELETE:
                print(f"node {sample.key_expr} went offline")
            is_online = sample.kind == zenoh.SampleKind.PUT
            on_liveliness_change(name, is_online)
        
        for tag_key_prefix in tag_data_callbacks:
            self.add_tag_data_callback(name, tag_key_prefix, tag_data_callbacks[tag_key_prefix])

        if on_state:
            print(f"state key expr: {state_key_expr}")
            subscriber = self._comm.session.declare_subscriber(state_key_expr, _on_state)
            handlers.append(subscriber)
        if on_meta:
            print(f"meta key expr: {meta_key_expr}")
            subscriber = self._comm.session.declare_subscriber(meta_key_expr, _on_meta)
            handlers.append(subscriber)
        if on_liveliness_change:
            key_expr = keys.liveliness_key_prefix(self.config.key_prefix, name)
            print(f"liveliness key expr: {key_expr}")
            subscriber = self._comm.declare_liveliness_subscriber(key_expr, _on_liveliness)
            handlers.append(subscriber)
        self.nodes[name] = handlers

    def disconnect_from_node(self, name: str):
        if name not in self.nodes:
            raise IndexError(f"{name} not connected")
        handlers = self.nodes[name]
        for h in handlers:
            h.undeclare()
        del self.nodes[name]
    
    def add_tag_data_callback(self, node_name: str, tag_key_prefix: str, on_tag_data: TagDataCallback) -> None:
        meta = self._comm.pull_meta_message(self.config.key_prefix, node_name)
        key_expr = keys.tag_data_key(self.config.key_prefix, node_name, tag_key_prefix)
        def _on_tag_data(sample: zenoh.Sample):
            payload = base64.b64decode(sample.payload.to_bytes())
            tag_data = TagData()
            tag_data.ParseFromString(payload)

            tag_config = [x for x in meta.tags if str(sample.key_expr).endswith(x.key)]
            if len(tag_config) == 0:
                raise ValueError(f"no tag found at key expression {sample.key_expr}")
            tag_config = tag_config[0]
            value = Tag.from_tag_data(tag_data, tag_config.type)
            on_tag_data(node_name, key_expr, value)
        print(f"tag data key expr: {key_expr}")
        subscriber = self._comm.session.declare_subscriber(key_expr, _on_tag_data)
        self.nodes[node_name].append(subscriber)

    def close(self):
        self._comm.session.close()
