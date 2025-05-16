from gedge.comm.comm import Comm
from gedge.comm.keys import NodeKeySpace
from gedge import proto
from typing import Any, Callable
from datetime import datetime
import zenoh

from gedge.node.reply import Response
from gedge.py_proto.base_data import BaseData
from gedge.py_proto.data_model import DataItem
from gedge.py_proto.tag_config import Tag, TagConfig

class TagBind:
    def __init__(self, ks: NodeKeySpace, path: str, comm: Comm, tag_config: TagConfig, value: Any | None, on_set: Callable[[str, Any, Tag], Any], on_close: Callable[[str], None]):
        self.path = path
        self._on_set = on_set # what function should we run before we set the value? (i.e. a write_tag or update_tag, for example)
        if value:
            self._on_set(self.path, value, tag_config.get_tag(path))
        self._value = value
        self.last_received: datetime = datetime.now()
        self.is_valid: bool = True
        self._tag_config = tag_config
        self._tag = tag_config.get_tag(path)
        self._comm = comm
        self._ks = ks
        self._on_close = on_close

        # if the user updates a tag via "session.update_tag(...)", the bind will reflect it
        # comm.tag_data_subscriber(ks, self.path, self._on_value, tag_config)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        response = self._on_set(self.path, value, self._tag)
        if response is not None:
            response: Response
            if response.is_err():
                raise ValueError(f"could not update tag using tag bind with value {value}, received error code from remote node")
        self.last_received = datetime.now()
        self._value = value

    def _on_value(self, key_expr: str, value: Any):
        self._update_value_externally(value)
    
    def _update_value_externally(self, value: Any):
        self.last_received = datetime.now()
        self._value = value

    def close(self):
        self.is_valid = False
        self._comm.cancel_tag_data_subscription(self._ks, self.path)
        self._on_close(self.path)