from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class root_object(_message.Message):
    __slots__ = ("inner", "tag4")
    INNER_FIELD_NUMBER: _ClassVar[int]
    TAG4_FIELD_NUMBER: _ClassVar[int]
    inner: inner
    tag4: bool
    def __init__(self, inner: _Optional[_Union[inner, _Mapping]] = ..., tag4: bool = ...) -> None: ...

class inner(_message.Message):
    __slots__ = ("tag3",)
    TAG3_FIELD_NUMBER: _ClassVar[int]
    tag3: str
    def __init__(self, tag3: _Optional[str] = ...) -> None: ...

class my_model(_message.Message):
    __slots__ = ("root_object", "tag1", "tag2")
    ROOT_OBJECT_FIELD_NUMBER: _ClassVar[int]
    TAG1_FIELD_NUMBER: _ClassVar[int]
    TAG2_FIELD_NUMBER: _ClassVar[int]
    root_object: root_object
    tag1: float
    tag2: int
    def __init__(self, root_object: _Optional[_Union[root_object, _Mapping]] = ..., tag1: _Optional[float] = ..., tag2: _Optional[int] = ...) -> None: ...
