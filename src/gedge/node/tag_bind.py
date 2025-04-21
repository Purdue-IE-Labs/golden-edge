from gedge.comm.comm import Comm
from gedge.comm.keys import NodeKeySpace
from gedge import proto
from typing import Any, Callable
from datetime import datetime
import zenoh

from gedge.py_proto.data_model import DataObject
from gedge.py_proto.tag_config import TagConfig

class TagBind:
    def __init__(self, ks: NodeKeySpace, comm: Comm, tag: TagConfig, value: Any | None, on_set: Callable[[str, Any], Any]):
        self.path = tag.path
        self._on_set = on_set # what function should we run before we set the value? (i.e. a write_tag or update_tag, for example)
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
        tag_data = self._comm.deserialize(proto.DataObject(), sample.payload.to_bytes())
        value = DataObject.from_proto(tag_data, self.tag.data_object_config)
        self.last_received = datetime.now()
        self.value = value

    def close(self):
        self.is_valid = False
        self._subscriber.undeclare()