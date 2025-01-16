from tag import Tag
from typing import Any, List, Set
from proto.tag_data_pb2 import TagData
from proto.meta_pb2 import Meta
from error import TagIncorrectDataType, TagNotFound, TagDuplicateName
from contextlib import contextmanager
from comm import Comm

class EdgeNode:
    def __init__(self, key_prefix: str, name: str):
        self.key_prefix = key_prefix
        self.name = name
        self.connected = False
        self.tags: Set[Tag] = set()
        self._comm: Comm = Comm()
    
    # TODO: should external API use a protobuf definition
    def add_tag(self, name: str, type: TagData.DataType, properties: dict = {}):
        if len([t for t in self.tags if t.name == name]) >= 1:
            # for now, we disallow tags with duplicate names
            raise TagDuplicateName
        tag = Tag(name, type, properties)
        self.tags.add(tag)

    def write_tag(self, name: str, value: Any):
        tag = [tag for tag in self.tags if tag.name == name]
        if len(tag) == 0:
            raise KeyError
        tag = tag[0]
        # zenoh write
        # TODO
    
    def delete_tag(self, name: str):
        # TODO
        pass
    
    @contextmanager
    def connect(self):
        meta: Meta = self._build_meta()
        # Send STATE message
        with self._comm.connect() as session:
            try:
                self._comm.send_meta(meta)
                yield session
            finally:
                pass

    def _build_meta(self) -> Meta:
        meta = Meta(tags=[Meta.Tag(name=t.name, type=t.type, properties=t.properties) for t in self.tags])
        return meta
    
class EdgeNodeSession:
    def __init__(self):
        pass

    