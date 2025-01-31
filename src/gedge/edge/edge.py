from typing import Any, Set
from gedge.proto import TagData, Meta, DataType, State, Property
from gedge.edge.error import TagIncorrectDataType, TagNotFound, TagDuplicateName
from contextlib import contextmanager
from gedge.comm.comm import Comm
from gedge.edge.tag import Tag


class EdgeNodeConfig:
    def __init__(self, key_prefix: str, name: str, tags: Set[Tag] = set()):
        self.key_prefix = key_prefix.strip("/")
        self.name = name
        self.connected = False
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
        comm = Comm(self.key_prefix, self.name)
        with comm.connect():
            yield EdgeNodeSession(config=self, comm=comm)
    
    def build_meta(self) -> Meta:
        print(f"building meta for {self.name}")
        tags = []
        for t in self.tags:
            tag = Meta.Tag(name=t.name, type=t.type, key_expr=t.key_expr, properties=t.properties)
            tags.append(tag)
        meta = Meta(tags=tags)
        return meta

class EdgeNodeSession:
    def __init__(self, config: EdgeNodeConfig, comm: Comm):
        self._comm = comm 
        self.config = config
        self.startup()

    def startup(self):
        meta: Meta = self.config.build_meta()
        self._comm.send_meta(meta)
        state: State = State(online=True)
        self._comm.send_state(state)
        self.node_liveliness = self._comm.declare_liveliness_token(self._comm.liveliness_key_prefix(self.config.key_prefix, self.config.name))
        messages = self._comm.pull_meta_messages(only_online=True)
        print(messages)
    
    def update_tag(self, name: str, value: Any):
        tag = [tag for tag in self.config.tags if tag.name == name]
        if len(tag) == 0:
            raise KeyError
        tag = tag[0]
        self._comm.send_tag(value=tag.convert(value), key_expr=tag.key_expr)
    
    def send_state(self, online: bool):
        self._comm.send_state(State(online=online))

    def close(self):
        self.send_state(False)
        self._comm.session.close()
