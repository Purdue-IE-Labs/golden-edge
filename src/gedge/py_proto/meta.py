
from dataclasses import dataclass

from gedge import proto
from gedge.comm.keys import NodeKeySpace
from gedge.node.method import MethodConfig
from gedge.node.subnode import SubnodeConfig
from gedge.py_proto.data_model_config import DataModelConfig
from gedge.py_proto.data_model_ref import DataModelRef
from gedge.py_proto.props import Prop
from gedge.py_proto.tag_config import TagConfig


@dataclass
class Meta:
    key: str
    tags: TagConfig
    methods: dict[str, MethodConfig]
    subnodes: dict[str, SubnodeConfig]
    models: dict[str, DataModelConfig]
    props: dict[str, Prop]

    @classmethod
    def from_proto(cls, proto: proto.Meta):
        key = proto.key
        ks = NodeKeySpace.from_user_key(key)
        tag_config = TagConfig.from_proto(proto.tags)
        methods: dict[str, MethodConfig] = {m.path: MethodConfig.from_proto(m) for m in proto.methods}
        models: dict[str, DataModelConfig] = {DataModelRef(m.path, m.version).full_path: DataModelConfig.from_proto(m) for m in proto.models}
        subnodes: dict[str, SubnodeConfig] = {s.name: SubnodeConfig.from_proto(s, ks) for s in proto.subnodes}
        props: dict[str, Prop] = {p.key: Prop.from_proto(p) for p in proto.props}
        return cls(key, tag_config, methods, subnodes, models, props)

    def to_proto(self) -> proto.Meta:
        tags = self.tags.to_proto()
        methods: list[proto.MethodConfig] = [m.to_proto() for m in self.methods.values()]
        subnodes: list[proto.SubnodeConfig] = [s.to_proto() for s in self.subnodes.values()]
        models: list[proto.DataModelConfig] = [m.to_proto() for m in self.models.values()]
        props: list[proto.Prop] = [p.to_proto() for p in self.props.values()]
        meta = proto.Meta(key=self.key, tags=tags, methods=methods, subnodes=subnodes, models=models, props=props)
        return meta
    
