from . import data_model_session_pb2 as _data_model_session_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Response(_message.Message):
    __slots__ = ("code", "body")
    class BodyEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _data_model_session_pb2.DataItem
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_data_model_session_pb2.DataItem, _Mapping]] = ...) -> None: ...
    CODE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    code: int
    body: _containers.MessageMap[str, _data_model_session_pb2.DataItem]
    def __init__(self, code: _Optional[int] = ..., body: _Optional[_Mapping[str, _data_model_session_pb2.DataItem]] = ...) -> None: ...
