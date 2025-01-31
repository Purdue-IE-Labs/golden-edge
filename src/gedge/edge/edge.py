from typing import Any, Set
from gedge.proto import TagData, Meta, DataType, State, Property
from gedge.edge.error import TagIncorrectDataType, TagNotFound, TagDuplicateName
from contextlib import contextmanager
from gedge.comm.comm import Comm
from gedge.edge.tag import Tag
from gedge.comm import keys


class EdgeNodeConfig:
    def __init__(self, key_prefix: str, name: str, tags: Set[Tag] = set()):
        self.key_prefix = key_prefix.strip("/")
        self.name = name
        self.tags: Set[Tag] = tags

    def add_tag(self, name: str, type: int | type, key_expr: str, properties: dict[str, Any] = {}):
        if len([t for t in self.tags if t.name == name]) >= 1:
            # for now, we disallow tags with duplicate names
            raise TagDuplicateName
        print(f"adding tag on prefix: {key_expr}")
        tag = Tag(name, type, key_expr, properties)
        self.tags.add(tag)

    def delete_tag(self, name: str):
        self.tags.remove(name)

    @contextmanager
    def connect(self):
        comm = Comm()
        with comm.connect():
            yield EdgeNodeSession(config=self, comm=comm)
    
    def build_meta(self) -> Meta:
        print(f"building meta for {self.name}")
        tags = []
        for t in self.tags:
            tag = Meta.Tag(name=t.name, type=t.type, key_expr=t.key_expr, properties=t.properties)
            tags.append(tag)
        meta = Meta(name=self.name, key_expr=keys.node_key_prefix(self.key_prefix, self.name), tags=tags)
        return meta

class EdgeNodeSession:
    def __init__(self, config: EdgeNodeConfig, comm: Comm):
        self._comm = comm 
        self.config = config
        self.startup()

    def startup(self):
        key_prefix = self.config.key_prefix
        name = self.config.name
        meta: Meta = self.config.build_meta()
        self._comm.send_meta(key_prefix, name, meta)
        state: State = State(online=True)
        self._comm.send_state(key_prefix, name, state)
        self.node_liveliness = self._comm.declare_liveliness_token(keys.liveliness_key_prefix(key_prefix, name))
    
    def update_tag(self, name: str, value: Any):
        key_prefix = self.config.key_prefix
        node_name = self.config.name
        tag = [tag for tag in self.config.tags if tag.name == name]
        if len(tag) == 0:
            raise KeyError
        tag = tag[0]
        self._comm.send_tag(key_prefix, node_name, tag.key_expr, tag.convert(value))
    
    def send_state(self, online: bool):
        self._comm.send_state(self.config.key_prefix, self.config.name, State(online=online))

    def close(self):
        self.send_state(False)
        self._comm.session.close()
