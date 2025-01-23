import zenoh
from gedge.edge import Tag
from typing import Any, Set, Union, Type, Generator
from gedge.proto import TagData, Meta, DataType
from gedge.edge.error import TagIncorrectDataType, TagNotFound, TagDuplicateName
from contextlib import contextmanager
from gedge.comm.comm import Comm


class EdgeNodeConfig:
    def __init__(self, key_prefix: str, name: str, tags: Set[Tag] = set()):
        self.key_prefix = key_prefix
        self.name = name
        self.connected = False
        self.tags: Set[Tag] = tags

    def add_tag(self, name: str, type: Any, key_expr: str, properties: dict = {}):
        if len([t for t in self.tags if t.name == name]) >= 1:
            # for now, we disallow tags with duplicate names
            raise TagDuplicateName
        tag = Tag(name, type, key_expr, properties)
        self.tags.add(tag)

    def delete_tag(self, name: str):
        pass

    @contextmanager
    def connect(self):
        comm: Comm = Comm(self.key_prefix, self.name)
        with comm.connect() as session:
            yield EdgeNodeSession(config=self, z_session=session, comm=comm)
    
    def build_meta(self) -> Meta:
        meta = Meta(tags=[Meta.Tag(name=t.name, type=t.type, properties=t.properties) for t in self.tags])
        return meta

class EdgeNodeSession:
    def __init__(self, config: EdgeNodeConfig, z_session: zenoh.Session, comm: Comm):
        self._z_session = z_session
        self._comm = comm 
        self.config = config

    def startup(self):
        meta: Meta = self.config.build_meta()
        # Send STATE message
        # Receive META messages
        self._comm.send_meta(meta)
    
    def write_tag(self, name: str, value: Any):
        tag = [tag for tag in self.config.tags if tag.name == name]
        if len(tag) == 0:
            raise KeyError
        tag = tag[0]
        self._comm.send_tag(value=tag.convert(value), key_expr=tag.key_expr)

    
@contextmanager
def connect(config: EdgeNodeConfig) -> Generator[EdgeNodeSession, None, None]:
    with config.connect() as session:
        yield session