from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from gedge import proto
from gedge.py_proto.data_model import DataItem
from gedge.py_proto.data_model_config import DataItemConfig
from gedge.py_proto.props import Prop

if TYPE_CHECKING:
    from gedge.node.gtypes import TagValue


def list_to_proto(l: list[Any]) -> list[Any]:
    return [p.to_proto() for p in l]

def list_from_proto(type: Any, l: Any) -> list[Any]:
    return [type.from_proto(p) for p in l]

def list_to_json5(l: list[Any]) -> list[Any]:
    return [j.to_json5() for j in l]

# generics?!
T = TypeVar('T') 
def list_from_json5(type: type[T], l: list) -> list[T]:
    return [type.from_json5(j) for j in l] # type: ignore

def props_from_json5(j: dict[str, Any]) -> list[Prop]:
    return [Prop.from_json5(key, p) for key, p in j.items()]

def props_to_json5(props: list[Prop]) -> dict[str, Any]:
    j = {}
    for p in props:
        j.update(p.to_json5())
    return j

def dict_proto_to_value(proto: dict[str, proto.DataItem], config: list[DataItemConfig]) -> dict[str, TagValue]:
    c: dict[str, DataItemConfig] = {i.path: i for i in config}
    value_dict: dict[str, TagValue] = {k: DataItem.from_proto(v, c[k]).to_value() for k, v in proto.items()}
    return value_dict

def dict_value_to_proto(value: dict[str, TagValue], config: list[DataItemConfig]) -> dict[str, proto.DataItem]:
    c: dict[str, DataItemConfig] = {i.path: i for i in config}
    proto = {k: DataItem.from_value(v, c[k]).to_proto() for k, v in value.items()}
    return proto