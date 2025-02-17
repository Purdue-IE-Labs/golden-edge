from typing import Any, TypeAlias, Callable
import zenoh
from gedge import proto

# specifies that we expect the user to pass a type itself (or a DataType instance)
# example: int
# example: DataType.INT
Type = int | Any

# a node defines this on its own config for its writable tags
TagValue = Any
TagWriteHandler: TypeAlias = Callable[[TagValue], int]

KeyExpr = str
StateCallback: TypeAlias = Callable[[KeyExpr, proto.State], None]
MetaCallback: TypeAlias = Callable[[KeyExpr, proto.Meta], None]
TagDataCallback: TypeAlias = Callable[[KeyExpr, TagValue], None]
LivelinessCallback: TypeAlias = Callable[[KeyExpr, bool], None]
ZenohCallback = Callable[[zenoh.Sample], None]
ZenohQueryCallback = Callable[[zenoh.Query], None]