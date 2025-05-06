from typing import Callable, Any
import zenoh
from gedge import proto
from gedge.node.query import MethodQuery, TagWriteQuery
from gedge.node.reply import Response
# from gedge.py_proto.data_model import DataObject

# a node defines this on its own config for its writable tags
TagBaseValue = int | float | bool | str | list[int] | list[float] | list[bool] | list[str]
# dict is the representation of a DataModel
TagValue = TagBaseValue | dict[str, Any]

TagWriteHandler = Callable[[TagWriteQuery], None]
MethodHandler = Callable[[MethodQuery], None]
MethodReplyCallback = Callable[[Response], None]

KeyExpr = str
StateCallback = Callable[[KeyExpr, proto.State], None]
MetaCallback = Callable[[KeyExpr, proto.Meta], None]
# TagDataCallback = Callable[[KeyExpr, TagBaseValue | DataObject], None]
TagDataCallback = Callable[[KeyExpr, TagValue], None]
LivelinessCallback = Callable[[KeyExpr, bool], None]
ZenohCallback = Callable[[zenoh.Sample], None]
ZenohQueryCallback = Callable[[zenoh.Query], None]
ZenohReplyCallback = Callable[[zenoh.Reply], None]

def is_base_value(value: TagValue) -> bool:
    return not isinstance(value, dict)

def is_model_value(value: TagValue) -> bool:
    return isinstance(value, dict)