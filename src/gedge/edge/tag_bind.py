from gedge.comm.comm import Comm
from gedge.comm.keys import NodeKeySpace
from gedge.edge.tag import Tag
from gedge import proto
from typing import Any, Callable
from datetime import datetime
import zenoh

from gedge.edge.tag_data import TagData

class TagBind:
    def __init__(self, ks: NodeKeySpace, comm: Comm, tag: Tag, value: Any | None, on_set: Callable[[str, Any], tuple[int, str]]):
        self.path = tag.path
        self._on_set = on_set
        if value:
            self._on_set(self.path, value)
        self._value = value
        self.last_received: datetime = datetime.now()
        self.is_valid: bool = True
        self.tag = tag
        self._comm = comm
        self._subscriber = comm.session.declare_subscriber(ks.tag_data_path(self.path), self._on_value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._on_set(self.path, value)
        self._value = value

    def _on_value(self, sample: zenoh.Sample):
        tag_data = self._comm.deserialize(proto.TagData(), sample.payload.to_bytes())
        value = TagData.from_proto(tag_data, self.tag.type).to_py()
        self.last_received = datetime.now()
        self.value = value

    def close(self):
        self.is_valid = False
        self._subscriber.undeclare()