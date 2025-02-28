from typing import Callable, Any
import zenoh
from gedge import proto
from gedge.edge.data_type import DataType

# specifies that we expect the user to pass a type itself (or a DataType instance)
# example: int
# example: DataType.INT
Type = DataType | type

# a node defines this on its own config for its writable tags
TagValue = int | float | bool | str | list[int] | list[float] | list[bool] | list[str]
TagWriteHandler = Callable[[str, TagValue], int]

# MethodHandler = Callable[[MethodQuery], None]
# TagWriteHandler = Callable[[TagWriteQuery], None]

KeyExpr = str
StateCallback = Callable[[KeyExpr, proto.State], None]
MetaCallback = Callable[[KeyExpr, proto.Meta], None]
TagDataCallback = Callable[[KeyExpr, TagValue], None]
LivelinessCallback = Callable[[KeyExpr, bool], None]
ZenohCallback = Callable[[zenoh.Sample], None]
ZenohQueryCallback = Callable[[zenoh.Query], None]
ZenohReplyCallback = Callable[[zenoh.Reply], None]
