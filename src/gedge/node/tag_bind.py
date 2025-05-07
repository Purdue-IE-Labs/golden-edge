from gedge.comm.comm import Comm
from gedge.comm.keys import NodeKeySpace
from gedge import proto
from typing import Any, Callable
from datetime import datetime
import zenoh

from gedge.node.reply import Response
from gedge.py_proto.base_data import BaseData
from gedge.py_proto.data_model import DataItem
from gedge.py_proto.tag_config import Tag

class TagBind:
    def __init__(self, ks: NodeKeySpace, comm: Comm, tag: Tag, value: Any | None, on_set: Callable[[str, Any, Tag], Any]):
        self.path = tag.path
        self._on_set = on_set # what function should we run before we set the value? (i.e. a write_tag or update_tag, for example)
        if value:
            self._on_set(self.path, value, tag)
        self._value = value
        self.last_received: datetime = datetime.now()
        self.is_valid: bool = True
        self._tag = tag
        self._comm = comm
        self._subscriber = comm.session.declare_subscriber(ks.tag_data_path(self.path), self._on_value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        response = self._on_set(self.path, value, self._tag)
        if response is not None:
            response: Response
            if response.is_err():
                raise ValueError(f"could not update tag using tag bind with value {value}")
        self._value = value

    def _on_value(self, sample: zenoh.Sample):
        tag_data = self._comm.deserialize(proto.BaseData(), sample.payload.to_bytes())
        value = BaseData.proto_to_py(tag_data, self._tag.get_config(self.path).get_base_type()) # type: ignore
        self.last_received = datetime.now()
        self.value = value

    def close(self):
        self.is_valid = False
        self._subscriber.undeclare()