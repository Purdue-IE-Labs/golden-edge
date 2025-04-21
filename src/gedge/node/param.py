from __future__ import annotations

from dataclasses import dataclass
from gedge.node.data_type import DataType
from gedge.py_proto.base_data import BaseData
from gedge.py_proto.params_config import ParamsConfig
from gedge.py_proto.props import Props
from gedge import proto

from typing import Any, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from gedge.node.gtypes import TagBaseValue

def params_proto_to_py(proto: dict[str, proto.DataObject], params_config: ParamsConfig) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for key, value in proto.items():
        config = params_config[key].config
        t = config.get_base_type()
        if not t:
            return {}
        params[key] = BaseData.proto_to_py(value.base_data, t)
    return params