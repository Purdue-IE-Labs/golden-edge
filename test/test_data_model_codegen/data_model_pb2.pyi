from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Object(_message.Message):
    __slots__ = ("name", "objects", "bases")
    NAME_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    BASES_FIELD_NUMBER: _ClassVar[int]
    name: str
    objects: _containers.RepeatedCompositeFieldContainer[Object]
    bases: _containers.RepeatedCompositeFieldContainer[Base]
    def __init__(self, name: _Optional[str] = ..., objects: _Optional[_Iterable[_Union[Object, _Mapping]]] = ..., bases: _Optional[_Iterable[_Union[Base, _Mapping]]] = ...) -> None: ...

class Base(_message.Message):
    __slots__ = ("name", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class Model(_message.Message):
    __slots__ = ("name", "objects", "bases")
    NAME_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    BASES_FIELD_NUMBER: _ClassVar[int]
    name: str
    objects: _containers.RepeatedCompositeFieldContainer[Object]
    bases: _containers.RepeatedCompositeFieldContainer[Base]
    def __init__(self, name: _Optional[str] = ..., objects: _Optional[_Iterable[_Union[Object, _Mapping]]] = ..., bases: _Optional[_Iterable[_Union[Base, _Mapping]]] = ...) -> None: ...
