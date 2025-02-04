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
ZenohCallback = Callable[[zenoh.Sample], None]
class AppSession:
    def __init__(self, config: AppConfig, comm: Comm):
        self._comm = comm
        self.config = config
        # key str is the key_expr where this node lives: <key_prefix>/NODE/<node_name>
        self.nodes: dict[str, List[zenoh.Subscriber]] = defaultdict(list) 
    
    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        self._comm.__exit__(*exc)

    def nodes_on_network(self, key_prefix: str, only_online: bool = False) -> list[Meta]:
        return self.pull_meta_messages(key_prefix, only_online)

    def print_nodes_on_network(self, key_prefix: str, only_online: bool = False):
        messages = self.pull_meta_messages(key_prefix, only_online=only_online)
        if len(messages) == 0:
            print("No Nodes on Network!")
            return
        print("Nodes on Network:")
        i = 1
        for meta in messages:
            print(f"{i}. {meta.name}: {"online" if self._comm.is_online(key_prefix, meta.name) else "offline"}")
            print(f"{meta}\n")
            i += 1

    def pull_meta_messages(self, key_prefix: str, only_online: bool) -> list[Meta]:
        return self._comm.pull_meta_messages(key_prefix, only_online)

    def _add_subscriber_to_node(self, key_prefix: str, name: str, *subscriber: zenoh.Subscriber):
        node_key_expr = keys.node_key_prefix(key_prefix, name)
        self.nodes[node_key_expr] += list(subscriber)
    
    def _on_state_default(self):
        pass

    def _on_meta_default(self):
        pass

    def _on_tag_data_default(self):
        pass

    def _on_liveliness_default(self):
        pass

    def _on_node_meta(self, sample: zenoh.Sample):
        print("got node meta")

    def _on_tag_data(self, key_prefix: str, name: str, meta: Meta, on_tag_data: TagDataCallback) -> ZenohCallback:
        def _on_tag_data(sample: zenoh.Sample):
            payload = base64.b64decode(sample.payload.to_bytes())
            tag_data = TagData()
            tag_data.ParseFromString(payload)

            tag_config = [x for x in meta.tags if str(sample.key_expr).endswith(x.key)]
            if len(tag_config) == 0:
                raise LookupError(f"no tag found at key expression {sample.key_expr}")
            tag_config = tag_config[0]
            value = Tag.from_tag_data(tag_data, tag_config.type)
            on_tag_data(name, key_prefix, value)
        return _on_tag_data

    def _on_state(self, key_prefix: str, name: str, on_state: StateCallback) -> ZenohCallback:
        state_key_expr = keys.state_key_prefix(key_prefix, name)
        def _on_state(sample: zenoh.Sample):
            payload = base64.b64decode(sample.payload.to_bytes())
            state = State()
            state.ParseFromString(payload)
            on_state(name, state_key_expr, state)
        return _on_state

    def _on_meta(self, key_prefix: str, name: str, on_meta: MetaCallback) -> ZenohCallback:
        meta_key_expr = keys.meta_key_prefix(key_prefix, name)
        def _on_meta(sample: zenoh.Sample):
            payload = base64.b64decode(sample.payload.to_bytes())
            meta = Meta()
            meta.ParseFromString(payload)
            on_meta(name, meta_key_expr, meta)
        return _on_meta
    
    def _on_liveliness(self, name: str, on_liveliness_change: LivelinessCallback) -> ZenohCallback:
        def _on_liveliness(sample: zenoh.Sample):
            if sample.kind == zenoh.SampleKind.PUT:
                print(f"node {sample.key_expr} online")
            elif sample.kind == zenoh.SampleKind.DELETE:
                print(f"node {sample.key_expr} went offline")
            is_online = sample.kind == zenoh.SampleKind.PUT
            on_liveliness_change(name, is_online)
        return _on_liveliness

    def connect_to_node(self, key_prefix: str, name: str, on_state: StateCallback = None, on_meta: MetaCallback = None, on_liveliness_change: LivelinessCallback = None, tag_data_callbacks: dict[str, TagDataCallback] = {}):
        handlers = []

        print(f"connecting to node {name}")
        meta = self._comm.pull_meta_message(key_prefix, name)
        # TODO: what if already connected?
        meta_key_expr = keys.meta_key_prefix(key_prefix, name)
        subscriber = self._comm.session.declare_subscriber(meta_key_expr, self._on_node_meta)
        handlers.append(subscriber)

        for key in tag_data_callbacks:
            # The reason we don't use function self.add_tag_data_callback(...) here is that
            # the functionality is slightly different. Most importantly, here, we just 
            # skip those callbacks that don't match a tag, while in the function we 
            # throw an exception. Additionally, with this approach, we can pull the 
            # meta only once instead of pulling it with each new function call
            if len([tag for tag in meta.tags if tag.key == key]) == 0:
                print(f"WARNING: no tag found at key {key}")
                continue
            key_expr = keys.tag_data_key(key_prefix, name, key)
            _on_tag_data = self._on_tag_data(key_prefix, name, meta, tag_data_callbacks[key])
            print(f"tag data key expr: {key_expr}")
            subscriber = self._comm.session.declare_subscriber(key_expr, _on_tag_data)
            handlers.append(subscriber)

        if on_state:
            self.add_state_callback(key_prefix, name, on_state)
        if on_meta:
            self.add_meta_callback(key_prefix, name, on_meta)
        if on_liveliness_change:
            self.add_liveliness_callback(key_prefix, name, on_liveliness_change)

        self._add_subscriber_to_node(key_prefix, name, *handlers)

    def disconnect_from_node(self, node_key_expr: str):
        if node_key_expr not in self.nodes:
            raise KeyError(f"{node_key_expr} not connected")
        handlers = self.nodes[node_key_expr]
        for h in handlers:
            h.undeclare()
        del self.nodes[node_key_expr]
    
    def add_tag_data_callback(self, key_prefix: str, node_name: str, key: str, on_tag_data: TagDataCallback) -> None:
        meta = self._comm.pull_meta_message(key_prefix, node_name)

        if len([tag for tag in meta.tags if tag.key == key]) == 0:
            raise LookupError(f"no tag found at key {key}")

        key_expr = keys.tag_data_key(key_prefix, node_name, key)
        print(f"tag data key expr: {key_expr}")
        subscriber = self._comm.session.declare_subscriber(key_expr, self._on_tag_data(key_prefix, node_name, meta, on_tag_data))
        self._add_subscriber_to_node(key_prefix, node_name, subscriber)

    def add_state_callback(self, key_prefix: str, node_name: str, on_state: StateCallback) -> None:
        state_key_expr = keys.state_key_prefix(key_prefix, node_name)
        _on_state = self._on_state(key_prefix, node_name, on_state)
        print(f"state key expr: {state_key_expr}")
        subscriber = self._comm.session.declare_subscriber(state_key_expr, _on_state)
        self._add_subscriber_to_node(key_prefix, node_name, subscriber)

    def add_meta_callback(self, key_prefix: str, node_name: str, on_meta: MetaCallback) -> None:
        meta_key_expr = keys.meta_key_prefix(key_prefix, node_name)
        _on_meta = self._on_meta(key_prefix, node_name, on_meta)
        print(f"meta key expr: {meta_key_expr}")
        subscriber = self._comm.session.declare_subscriber(meta_key_expr, _on_meta)
        self._add_subscriber_to_node(key_prefix, node_name, subscriber)

    def add_liveliness_callback(self, key_prefix: str, node_name: str, on_liveliness_change: LivelinessCallback) -> None:
        key_expr = keys.liveliness_key_prefix(key_prefix, node_name)
        _on_liveliness = self._on_liveliness(node_name, on_liveliness_change)
        print(f"liveliness key expr: {key_expr}")
        subscriber = self._comm.declare_liveliness_subscriber(key_expr, _on_liveliness)
        self._add_subscriber_to_node(key_prefix, node_name, subscriber)

    def close(self):
        for node in self.nodes:
            self.disconnect_from_node(node)
        self._comm.session.close()
