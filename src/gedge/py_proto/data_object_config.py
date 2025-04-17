from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Self, TYPE_CHECKING

from gedge import proto
from gedge.node.data_type import DataType
from gedge.py_proto.base_type import BaseType
from gedge.py_proto.config import Config
from gedge.py_proto.data_model_type import DataModelType
from gedge.py_proto.props import Props

if TYPE_CHECKING:
    from gedge.py_proto.data_model_config import DataModelConfig

@dataclass
class DataObjectConfig:
    config: Config
    props: Props

    def to_proto(self) -> proto.DataObjectConfig:
        props = self.props.to_proto()
        config = self.config.to_proto()
        return proto.DataObjectConfig(config=config, props=props)
    
    @classmethod
    def from_proto(cls, proto: proto.DataObjectConfig) -> Self:
        config = Config.from_proto(proto.config)
        props = Props.from_proto(proto.props)
        return cls(config, props)
