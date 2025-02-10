import base64
from gedge.comm.comm import Comm
from gedge.comm.keys import NodeKeySpace
from gedge.edge.tag import Tag, TagData
from typing import Any, Callable
from datetime import datetime
import zenoh

class TagBind:
    def __init__(self, ks: NodeKeySpace, comm: Comm, tag: Tag, value: Any | None, on_set: Callable[[str, Any], None]):
        self.path = tag.path
        self._on_set(self.path, value)
        self._value = value
        self.last_received: datetime = datetime.now()
        self.is_valid: bool = True
        self.tag = tag
        self._subscriber = comm.session.declare_subscriber(ks.tag_path(self.path), self._on_value)
        self._on_set = on_set

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._on_set(self.path, value)
        self._value = value

    def _on_value(self, sample: zenoh.Sample):
        payload = base64.b64decode(sample.payload.to_bytes())
        tag_data = TagData()
        tag_data.ParseFromString(payload)
        value = Tag.from_tag_data(tag_data, self.tag.type)
        self.last_received = datetime.now()
        self._value = value

    def close(self):
        self.is_valid = False
        self._subscriber.undeclare()