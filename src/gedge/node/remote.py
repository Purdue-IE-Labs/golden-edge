from typing import Any, Set, TypeAlias, Callable
from gedge.proto import TagData, Meta, DataType, State, Property
from gedge.edge.error import SessionError, ConfigError, TagLookupError
from gedge.comm.comm import Comm
from gedge.edge.tag import Tag
from gedge.edge.tag_bind import TagBind
from gedge.comm.keys import *
from collections import defaultdict
import zenoh
import base64

StateCallback: TypeAlias = Callable[[str, State], None]
MetaCallback: TypeAlias = Callable[[str, Meta], None]
TagDataCallback: TypeAlias = Callable[[str, Any], None]
LivelinessCallback: TypeAlias = Callable[[str, bool], None]
Callbacks: TypeAlias = tuple[StateCallback, MetaCallback, TagDataCallback]
ZenohCallback = Callable[[zenoh.Sample], None]

class RemoteConfig:
    def __init__(self, key: str, read_tags: list[str] = [], read_write_tags: list[str] = [], method_calls: list[str] = []):
        self.key = key
        self.read_tags = read_tags
        self.read_write_tags = read_write_tags
        self.method_calls = method_calls

class RemoteConnection:
    def __init__(self, config: RemoteConfig, comm: Comm, on_close: Callable[[str], None] = None):
        self.config = config
        self._comm = comm 
        self._subscriptions: list[zenoh.Subscriber] = []
        self.key = self.config.key
        self.ks = NodeKeySpace.from_user_key(self.key)
        self.on_close = on_close
        self.meta = self._comm.pull_meta_message(self.ks)
        print(f"connecting to node {self.ks.name}")

    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        self.close()
        self._comm.__exit__(*exc)

    def _on_tag_data(self, meta: Meta, on_tag_data: TagDataCallback) -> ZenohCallback:
        def _on_tag_data(sample: zenoh.Sample):
            payload = base64.b64decode(sample.payload.to_bytes())
            tag_data = TagData()
            tag_data.ParseFromString(payload)

            tag_config = [x for x in meta.tags if str(sample.key_expr).endswith(x.path)]
            if len(tag_config) == 0:
                path, node = NodeKeySpace.tag_path_from_key(str(sample.key_expr)), NodeKeySpace.name_from_key(str(sample.key_expr))
                raise TagLookupError(path, node)
            tag_config = tag_config[0]
            value = Tag.from_tag_data(tag_data, tag_config.type)
            on_tag_data(str(sample.key_expr), value)
        return _on_tag_data

    def _on_state(self, on_state: StateCallback) -> ZenohCallback:
        def _on_state(sample: zenoh.Sample):
            payload = base64.b64decode(sample.payload.to_bytes())
            state = State()
            state.ParseFromString(payload)
            on_state(str(sample.key_expr), state)
        return _on_state

    def _on_meta(self, on_meta: MetaCallback) -> ZenohCallback:
        def _on_meta(sample: zenoh.Sample):
            payload = base64.b64decode(sample.payload.to_bytes())
            meta = Meta()
            meta.ParseFromString(payload)
            on_meta(sample.key_expr, meta)
        return _on_meta
    
    def _on_liveliness(self, on_liveliness_change: LivelinessCallback) -> ZenohCallback:
        def _on_liveliness(sample: zenoh.Sample):
            if sample.kind == zenoh.SampleKind.PUT:
                print(f"node {sample.key_expr} online")
            elif sample.kind == zenoh.SampleKind.DELETE:
                print(f"node {sample.key_expr} went offline")
            is_online = sample.kind == zenoh.SampleKind.PUT
            on_liveliness_change(sample.key_expr, is_online)
        return _on_liveliness

    def close(self):
        for sub in self._subscriptions:
            sub.undeclare()        
        if self.on_close is not None:
            self.on_close(self.key)
    
    def add_tag_data_callback(self, path: str, on_tag_data: TagDataCallback) -> None:
        if len([tag for tag in self.meta.tags if tag.path == path]) == 0:
            raise TagLookupError(path, self.ks.name)

        self.config.read_write_tags.append(path)
        key_expr = self.ks.tag_path(path)
        print(f"tag data key expr: {key_expr}")
        subscriber = self._comm.subscriber(key_expr, self._on_tag_data(self.meta, on_tag_data))
        self._subscriptions.append(subscriber)

    def add_state_callback(self, on_state: StateCallback) -> None:
        _on_state = self._on_state(on_state)
        print(f"state key expr: {self.ks.state_key_prefix}")
        subscriber = self._comm.subscriber(self.ks.state_key_prefix, _on_state)
        self._subscriptions.append(subscriber)

    def add_meta_callback(self, on_meta: MetaCallback) -> None:
        _on_meta = self._on_meta(on_meta)
        print(f"meta key expr: {self.ks.meta_key_prefix}")
        subscriber = self._comm.subscriber(self.ks.meta_key_prefix, _on_meta)
        self._subscriptions.append(subscriber)

    def add_liveliness_callback(self, on_liveliness_change: LivelinessCallback) -> None:
        _on_liveliness = self._on_liveliness(on_liveliness_change)
        print(f"liveliness key expr: {self.ks.liveliness_key_prefix}")
        subscriber = self._comm.liveliness_subscriber(self.ks.liveliness_key_prefix, _on_liveliness)
        self._subscriptions.append(subscriber)

    def tag_binds(self, paths: list[str]) -> list[TagBind]:
        return [self.tag_bind(path) for path in paths]

    def tag_bind(self, path: str, value: Any = None) -> TagBind:
        tags = [t for t in self.meta.tags if t.path == path]
        if len(tags) == 0:
            raise TagLookupError(path, self.ks.name)
        tag = tags[0]
        bind = TagBind(self.ks, self._comm, Tag.from_proto_tag(tag), value, self.write_tag)
        return bind

    def write_tag(self, path: str, value: Any):
        tag = [tag for tag in self.meta.tags if tag.path == path]
        if len(tag) == 0:
            raise TagLookupError(path, self.ks.name)
        tag = Tag.from_proto_tag(tag[0])
        # TODO: writes will be a little more involved than this but for now we just write to /TAG/WRITES
        self._comm.write_tag(self.ks, tag.path, tag.convert(value))
