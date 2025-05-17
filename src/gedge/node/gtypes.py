from typing import Callable, Any
import zenoh
from gedge import proto
from gedge.node.query import MethodQuery, TagWriteQuery
from gedge.node.reply import Response
from gedge.py_proto.meta import Meta
from gedge.py_proto.state import State
# from gedge.py_proto.data_model import DataObject

# a node defines this on its own config for its writable tags
TagBaseValue = int | float | bool | str | list[int] | list[float] | list[bool] | list[str]

# dict is the representation of a DataModel and a TagGroup
TagGroupValue = dict[str, TagBaseValue]

TagValue = TagBaseValue | TagGroupValue

ProtoMessage = proto.Meta | proto.DataItem | proto.Response | proto.State | proto.MethodCall | proto.DataModelConfig | proto.BaseData | proto.TagGroup

TagWriteHandler = Callable[[TagWriteQuery], None]
MethodHandler = Callable[[MethodQuery], None]
MethodReplyCallback = Callable[[Response], None]

KeyExpr = str
StateCallback = Callable[[KeyExpr, State], None]
MetaCallback = Callable[[KeyExpr, Meta], None]
TagDataCallback = Callable[[KeyExpr, TagBaseValue], None]
TagGroupDataCallback = Callable[[KeyExpr, TagGroupValue], None]
LivelinessCallback = Callable[[KeyExpr, bool], None]
ZenohCallback = Callable[[zenoh.Sample], None]
ZenohQueryCallback = Callable[[zenoh.Query], None]
ZenohReplyCallback = Callable[[zenoh.Reply], None]

def is_base_value(value: TagValue) -> bool:
    return not isinstance(value, dict)

def is_model_value(value: TagValue) -> bool:
    return isinstance(value, dict)