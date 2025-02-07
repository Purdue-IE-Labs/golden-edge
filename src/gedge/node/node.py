from typing import Any, Set, TypeAlias, Callable
from gedge.node.remote import RemoteConfig, RemoteConnection
from gedge.proto import TagData, Meta, DataType, State, Property
from gedge.edge.error import SessionError, ConfigError
from gedge.comm.comm import Comm
from gedge.edge.tag import Tag
from gedge.edge.tag_bind import TagBind
from gedge.comm.keys import *
from collections import defaultdict
import zenoh
import base64

StateCallback: TypeAlias = Callable[[str, str, State], None]
MetaCallback: TypeAlias = Callable[[str, str, Meta], None]
TagDataCallback: TypeAlias = Callable[[str, str, Any], None]
LivelinessCallback: TypeAlias = Callable[[str, bool], None]
Callbacks: TypeAlias = tuple[StateCallback, MetaCallback, TagDataCallback]
ZenohCallback = Callable[[zenoh.Sample], None]

class PeerConnection:
    def __init__(self, key: str, read_tags: list[str], read_write_tags: list[str], method_calls: list[str]):
        self.key = key
        self.read_tags = read_tags
        self.read_write_tags = read_write_tags
        self.method_calls = method_calls

    def connect(self):
        pass
    
    def verify(self):
        pass

class NodeConfig:
    def __init__(self, key: str):
        self._user_key = key
        self.ks = NodeKeySpace.from_user_key(key)
        self.tags: set[Tag] = set()
        self.connections: set[PeerConnection] = set()

    @property
    def key(self):
        return self._user_key

    @key.setter
    def key(self, key: str):
        self._user_key = key
        self.ks = NodeKeySpace.from_user_key(key)

    def add_tag(self, path: str, type: int | type, props: dict[str, Any] = {}):
        tag = Tag(path, type, props)
        matching = [t for t in self.tags if t.path == path]
        if len(matching) == 1:
            print(f"Warning: tag {path} already exists in edge node {self.key}, updating...")
            self.tags.remove(matching[0])
        print(f"adding tag on key: {path}")
        self.tags.add(tag)

    def delete_tag(self, path: str):
        tags = [t for t in self.tags if t.path == path]
        if len(tags) != 1:
            raise KeyError(f"tag {path} not found in edge node {self.key}")
        self.tags.remove(tags[0])

    def build_meta(self) -> Meta:
        print(f"building meta for {self.key}")
        tags = []
        for t in self.tags:
            tag = Meta.Tag(path=t.path, type=t.type, properties=t.properties)
            tags.append(tag)
        meta = Meta(key=self.key, tags=tags, methods=[])
        return meta

    def connect(self):
        comm = Comm()
        return NodeSession(config=self, comm=comm)

class NodeSession:
    def __init__(self, config: NodeConfig, comm: Comm):
        self._comm = comm 
        self.config = config
        self.ks = config.ks
        self.connections: list[RemoteConnection] = []
        self.meta = self.startup()

    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        self.update_state(False)
        self._comm.__exit__(*exc)

    def close(self):
        self.update_state(False)
        self._comm.session.close()

    def _on_remote_close(self, key: str):
        connection = [c for c in self.connections if c.key == key][0]
        self.connections.remove(connection)

    def _pull_meta_message(self, key: str) -> Meta:
        ks = NodeKeySpace.from_user_key(key)
        return self._comm.pull_meta_message(ks)

    def _pull_meta_messages(self, key_prefix: str, only_online: bool) -> list[Meta]:
        return self._comm.pull_meta_messages(key_prefix, only_online)

    def is_online(self, key: str) -> bool:
        return self._comm.is_online(NodeKeySpace.from_user_key(key))

    # Currently, node_on_network and nodes_on_network accept different types of keys
    # node_on_network receives <key_prefix>/<node_name>, which gets expanded to 
    # <key_prefix>/NODE/<node_name>/META
    # Meanwhile, nodes_on_network(...) accepts just a <key_prefix>, which gets expanded to
    # <key_prefix>/NODE/*/META
    def node_on_network(self, key: str) -> Meta:
        # TODO: should we return if it's online?
        return self._pull_meta_message(key)
    
    def nodes_on_network(self, key_prefix: str, only_online: bool = False) -> list[Meta]:
        return self._pull_meta_messages(key_prefix, only_online)

    def print_nodes_on_network(self, key_prefix: str, only_online: bool = False):
        messages = self._pull_meta_messages(key_prefix, only_online=only_online)
        if len(messages) == 0:
            print("No Nodes on Network!")
            return
        print("Nodes on Network:")
        i = 1
        for meta in messages:
            _, _, name = meta.key.rpartition("/")
            print(f"{i}. {meta.key}: {"online" if self._comm.is_online(NodeKeySpace.from_user_key(meta.key), name) else "offline"}")
            print(f"{meta}\n")
            i += 1

    def connect_to_remote(self, key: str, on_state: StateCallback = None, on_meta: MetaCallback = None, on_liveliness_change: LivelinessCallback = None, tag_data_callbacks: dict[str, TagDataCallback] = {}) -> RemoteConnection:
        connection = RemoteConnection(RemoteConfig(key), self._comm, self._on_remote_close)
        if on_state:
            connection.add_state_callback(on_state)
        if on_meta:
            connection.add_meta_callback(on_meta)
        if on_liveliness_change:
            connection.add_liveliness_callback(on_liveliness_change)

        for path in tag_data_callbacks:
            connection.add_tag_data_callback(path, tag_data_callbacks[path])

        self.connections.append(connection)
        
        return connection

    def disconnect_from_remote(self, key: str):
        connection = [c for c in self.connections if c.key == key]
        if len(connection) == 0:
            raise KeyError(f"{key} not connected")
        connection = connection[0]
        connection.close()
        self.connections.remove(connection)
    
    def close(self):
        for node in self.connections:
            self.disconnect_from_remote(node.key)
        self._comm.session.close()

    def startup(self):
        prefix, name = self.ks.prefix, self.ks.name
        meta: Meta = self.config.build_meta()
        self._comm.send_meta(prefix, name, meta)
        self.update_state(True)
        self.node_liveliness = self._comm.liveliness_token(self.ks.liveliness_key_prefix)
        return meta

    def tag_binds(self, paths: list[str]) -> list[TagBind]:
        return [self.tag_bind(path) for path in paths]

    # TODO: tag_bind and update_tag use different methods to pull the tags of this node
    def tag_bind(self, path: str, value: Any = None) -> TagBind:
        tags = [t for t in self.meta.tags if t.path == path]
        if len(tags) == 0:
            # TODO: change this error?
            raise LookupError()
        tag = tags[0]
        bind = TagBind(self.ks, self._comm, Tag.from_proto_tag(tag), value, self.update_tag)
        return bind
    
    def update_tag(self, path: str, value: Any):
        prefix = self.ks.prefix
        node_name = self.ks.name
        tag = [tag for tag in self.config.tags if tag.path == path]
        if len(tag) == 0:
            # TODO: we could refactor this to its own error (the error where the given tag is not found on the node)
            raise LookupError(f"tag {path} does not exist on node {self.ks.name}")
        tag = tag[0]
        self._comm.update_tag(prefix, node_name, tag.path, tag.convert(value))
    
    def update_state(self, online: bool):
        self._comm.send_state(self.ks.prefix, self.ks.name, State(online=online))
