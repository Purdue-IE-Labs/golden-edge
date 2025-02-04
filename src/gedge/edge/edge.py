from typing import Any, Set
from gedge.proto import TagData, Meta, DataType, State, Property
from gedge.edge.error import SessionError, ConfigError
from contextlib import contextmanager
from gedge.comm.comm import Comm
from gedge.edge.tag import Tag
from gedge.comm import keys


class EdgeNodeConfig:
    def __init__(self, key_prefix: str, name: str, tags: Set[Tag] = set()):
        self.key_prefix = key_prefix.strip("/")
        self.name = name
        self.tags: Set[Tag] = tags

    def add_tag(self, path: str, type: int | type, properties: dict[str, Any] = {}):
        tag = Tag(path, type, properties)
        matching = [t for t in self.tags if t.path == path]
        if len(matching) == 1:
            print(f"Warning: tag {path} already exists in edge node {self.name}, updating...")
            self.tags.remove(matching[0])
        print(f"adding tag on key: {path}")
        self.tags.add(tag)

    def delete_tag(self, path: str):
        tags = [t for t in self.tags if t.path == path]
        if len(tags) == 1:
            self.tags.remove(tags[0])
        else:
            raise KeyError(f"tag {path} not found in edge node {self.name}")

    def connect(self):
        comm = Comm()
        return EdgeNodeSession(config=self, comm=comm)
    
    def build_meta(self) -> Meta:
        print(f"building meta for {self.name}")
        tags = []
        for t in self.tags:
            tag = Meta.Tag(key=t.path, type=t.type, properties=t.properties)
            tags.append(tag)
        meta = Meta(name=self.name, key_prefix=keys.node_key_prefix(self.key_prefix, self.name), tags=tags)
        return meta

class EdgeNodeSession:
    def __init__(self, config: EdgeNodeConfig, comm: Comm):
        self._comm = comm 
        self.config = config
        self.startup()

    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        self.send_state(False)
        self._comm.__exit__(*exc)

    def close(self):
        self.send_state(False)
        self._comm.session.close()

    def startup(self):
        key_prefix = self.config.key_prefix
        name = self.config.name
        meta: Meta = self.config.build_meta()
        self._comm.send_meta(key_prefix, name, meta)
        state: State = State(online=True)
        self._comm.send_state(key_prefix, name, state)
        self.node_liveliness = self._comm.liveliness_token(keys.liveliness_key_prefix(key_prefix, name))
    
    def update_tag(self, path: str, value: Any):
        key_prefix = self.config.key_prefix
        node_name = self.config.name
        tag = [tag for tag in self.config.tags if tag.path == path]
        if len(tag) == 0:
            raise LookupError(f"tag {path} does not exist on node {self.config.name}")
        tag = tag[0]
        self._comm.send_tag(key_prefix, node_name, tag.path, tag.convert(value))
    
    def send_state(self, online: bool):
        self._comm.send_state(self.config.key_prefix, self.config.name, State(online=online))
