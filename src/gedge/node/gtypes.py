from typing import Callable, Any
import zenoh
from gedge import proto
from gedge.node.query import MethodQuery
from gedge.node.method_reply import MethodReply
from gedge.node.tag_write_query import TagWriteQuery
from gedge.py_proto.base_type import BaseType
# from gedge.py_proto.data_model import DataObject

# specifies that we expect the user to pass a type itself (or a DataType instance)
# example: int
# example: DataType.INT
Type = type | BaseType

# a node defines this on its own config for its writable tags
TagBaseValue = int | float | bool | str | list[int] | list[float] | list[bool] | list[str]
# dict is the representation of a DataModel
TagValue = TagBaseValue | dict[str, Any]

TagWriteHandler = Callable[[TagWriteQuery], None]
MethodHandler = Callable[[MethodQuery], None]
MethodReplyCallback = Callable[[MethodReply], None]

KeyExpr = str
StateCallback = Callable[[KeyExpr, proto.State], None]
MetaCallback = Callable[[KeyExpr, proto.Meta], None]
# TagDataCallback = Callable[[KeyExpr, TagBaseValue | DataObject], None]
TagDataCallback = Callable[[KeyExpr, TagValue], None]
LivelinessCallback = Callable[[KeyExpr, bool], None]
ZenohCallback = Callable[[zenoh.Sample], None]
ZenohQueryCallback = Callable[[zenoh.Query], None]
ZenohReplyCallback = Callable[[zenoh.Reply], None]
