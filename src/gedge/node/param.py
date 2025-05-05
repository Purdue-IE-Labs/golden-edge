from __future__ import annotations

from gedge.py_proto.base_data import BaseData
from gedge import proto

from typing import Any, Self, TYPE_CHECKING

from gedge.py_proto.data_model_config import DataItemConfig

if TYPE_CHECKING:
    from gedge.node.gtypes import TagBaseValue, TagValue

def params_proto_to_py(proto: dict[str, proto.DataItem], params_config: list[DataItemConfig]) -> dict[str, TagValue]:
    config = {i.path: i for i in params_config}
    params: dict[str, Any] = {}
    for key, value in proto.items():
        type = config[key].type
        t = type.get_base_type()
        if not t:
            return {}
        params[key] = BaseData.proto_to_py(value.base_data, t)
    return params