from __future__ import annotations
from typing import Any, Callable, Self
import uuid

from gedge import proto
from gedge.comm.comm import Comm
from gedge.comm.keys import NodeKeySpace, SubnodeKeySpace
from gedge.node.method import MethodConfig
from gedge.node.method_response import ResponseConfig
from gedge.node.node import NodeConfig, NodeSession
from gedge.node.remote import RemoteConnection
from gedge.node.tag_bind import TagBind
from gedge.py_proto.tag_config import Tag, TagConfig

import logging

logger = logging.getLogger(__file__)

# inherit at some point but not now?
class SubnodeConfig(NodeConfig):
    def __init__(self, name: str, parent: NodeKeySpace, tag_config: TagConfig, methods: dict[str, MethodConfig], subnodes: dict[str, SubnodeConfig]):
        self.name = name
        self.tag_config = tag_config
        self.methods = methods
        self.subnodes = subnodes
        self.ks = SubnodeKeySpace(parent, name)

    '''
    we must pass the parent ks into this because 
    we need to know the placement of the subnode
    '''
    @classmethod
    def from_json5(cls, json: Any, parent: NodeKeySpace):
        if not isinstance(json, dict):
            raise ValueError(f"subnode must be dict, got {json}")
        if "name" not in json:
            raise ValueError(f"subnode must have 'name'")
        
        name = json["name"]
        if "/" in name:
            raise ValueError(f"subnode name cannot have '/' but subnode '{name}' found in json config")

        tags = dict()
        methods = dict()
        subnodes = dict()
        tag_config = TagConfig.from_json5(json.get("tags", []), json.get("writable_config", []), json.get("group_config", []))
        tags = tag_config
        for method_json in json.get("methods", []):
            method = MethodConfig.from_json5(method_json)
            methods[method.path] = method
        for subnode_json in json.get("subnodes", []):
            ks = SubnodeKeySpace(parent, name)
            subnode = SubnodeConfig.from_json5(subnode_json, ks)
            subnodes[subnode.name] = subnode
        return cls(name, parent, tags, methods, subnodes)

    def to_proto(self) -> proto.SubnodeConfig:
        tags = self.tag_config.to_proto()
        methods = [m.to_proto() for m in self.methods.values()]
        subnodes = [s.to_proto() for s in self.subnodes.values()]
        return proto.SubnodeConfig(name=self.name, tags=tags, methods=methods, subnodes=subnodes)
    
    @classmethod
    def from_proto(cls, proto: proto.SubnodeConfig, parent: NodeKeySpace) -> Self:
        name = proto.name
        tags = TagConfig.from_proto(proto.tags)
        methods = {m.path: m for m in [MethodConfig.from_proto(m) for m in proto.methods]}
        ks = SubnodeKeySpace(parent, proto.name)
        subnodes = {s.name: s for s in [SubnodeConfig.from_proto(s, ks) for s in proto.subnodes]}
        return cls(name, parent, tags, methods, subnodes)


class SubnodeSession(NodeSession):
    def __init__(self, config: SubnodeConfig, comm: Comm):
        self.config = config
        self._comm = comm
        self.ks = config.ks
        self.id = str(uuid.uuid4())

        # parent node already connected, don't call comm.connect here

        self.tag_config = self.config.tag_config
        self.methods: dict[str, MethodConfig] = self.config.methods
        self.method_responses: dict[str, dict[int, ResponseConfig]] = {key:{r.code:r for r in value.responses} for key, value in self.methods.items()}
        self.subnodes: dict[str, SubnodeConfig] = self.config.subnodes
        self.binds: dict[str, TagBind] = {}
    
    def subnode(self, name: str) -> SubnodeSession:
        session = SubnodeSession(self.subnodes[name], self._comm)
        return session
    
    def close(self):
        self.update_state(False)

class RemoteSubConnection(RemoteConnection):
    def __init__(self, name: str, ks: SubnodeKeySpace, subnode_config: SubnodeConfig, comm: Comm, node_id: str, on_close: Callable[[str], None] | None = None):
        self._comm = comm 
        self.key = name
        self.ks = ks
        self.on_close = on_close

        self.node_id = node_id

        '''
        TODO: perhaps we should subscribe to this node's meta message, in which case all the following utility variables (self.tags, self.methods, self.responses) 
        would need to react to that (i.e. be properties)
        '''
        self.meta = subnode_config
        self.tag_config = self.meta.tag_config
        self.methods = self.meta.methods
        self.responses: dict[str, dict[int, ResponseConfig]] = {key:{r.code:r for r in value.responses} for key, value in self.methods.items()}
        self.subnodes: dict[str, SubnodeConfig] = self.meta.subnodes
    
    # TODO: this function is repeated 4 times, we need to refactor desperately
    def subnode(self, name: str) -> RemoteSubConnection:
        def on_close(key):
            pass
        if "/" in name:
            curr_node = self
            subnodes = name.split("/")
            for s in subnodes:
                if s not in curr_node.subnodes:
                    raise ValueError(f"No subnode {s} when trying to find subnode {name}")
                curr_node = curr_node.subnodes[s]
            # we inherit comm
            # different uuid or same?
            assert isinstance(curr_node, SubnodeConfig)
            r = RemoteSubConnection(name, curr_node.ks, curr_node, self._comm, self.node_id, on_close)
            return r

        if name not in self.subnodes:
            raise ValueError(f"No subnode {name} in config for {self.key}") 
        curr_node = self.subnodes[name]
        r = RemoteSubConnection(name, curr_node.ks, curr_node, self._comm, self.node_id, on_close)
        return r
    
    def close(self):
        logger.warning("Cannot close a remote subnode connection. Close the root remote connection instead.")