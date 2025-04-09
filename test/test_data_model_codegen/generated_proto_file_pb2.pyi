from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class my_model(_message.Message):
    __slots__ = ("root_object", "tag1", "tag2")
    class root_object_message(_message.Message):
        __slots__ = ("tag4", "inner")
        class inner_message(_message.Message):
            __slots__ = ("tag3",)
            TAG3_FIELD_NUMBER: _ClassVar[int]
            tag3: str
            def __init__(self, tag3: _Optional[str] = ...) -> None: ...
        TAG4_FIELD_NUMBER: _ClassVar[int]
        INNER_FIELD_NUMBER: _ClassVar[int]
        tag4: bool
        inner: my_model.root_object_message.inner_message
        def __init__(self, tag4: bool = ..., inner: _Optional[_Union[my_model.root_object_message.inner_message, _Mapping]] = ...) -> None: ...
    ROOT_OBJECT_FIELD_NUMBER: _ClassVar[int]
    TAG1_FIELD_NUMBER: _ClassVar[int]
    TAG2_FIELD_NUMBER: _ClassVar[int]
    root_object: my_model.root_object_message
    tag1: float
    tag2: int
    def __init__(self, root_object: _Optional[_Union[my_model.root_object_message, _Mapping]] = ..., tag1: _Optional[float] = ..., tag2: _Optional[int] = ...) -> None: ...
