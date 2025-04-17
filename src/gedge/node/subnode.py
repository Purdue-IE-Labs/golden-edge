from __future__ import annotations
from typing import Any, Callable, Self
import uuid

from gedge import proto
from gedge.comm.comm import Comm
from gedge.comm.keys import NodeKeySpace, SubnodeKeySpace
from gedge.node.method import Method
from gedge.node.method_response import MethodResponse
from gedge.node.node import NodeConfig, NodeSession
from gedge.node.remote import RemoteConnection
from gedge.py_proto.tag_config import TagConfig, TagWriteResponseConfig

import logging

logger = logging.getLogger(__file__)

# inherit at some point but not now?
class SubnodeConfig(NodeConfig):
    def __init__(self, name: str, parent: NodeKeySpace, tags: dict[str, TagConfig], methods: dict[str, Method], subnodes: dict[str, SubnodeConfig]):
        self.name = name
        self.tags = tags
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
            raise ValueError(f"subnode must be dict: {json}")
        if "name" not in json:
            raise ValueError(f"subnode must have name")
        
        name = json["name"]
        if "/" in name:
            raise ValueError(f"subnode name cannot have '/' but subnode '{name}' found in json config")

        tags = dict()
        methods = dict()
        subnodes = dict()
        for tag_json in json.get("tags", []):
            tag = TagConfig.from_json5(tag_json)
            tags[tag.path] = tag
        for method_json in json.get("methods", []):
            method = Method.from_json5(method_json)
            methods[method.path] = method
        for subnode_json in json.get("subnodes", []):
            ks = SubnodeKeySpace(parent, name)
            subnode = SubnodeConfig.from_json5(subnode_json, ks)
            subnodes[subnode.name] = subnode
        return cls(name, parent, tags, methods, subnodes)

    def to_proto(self) -> proto.SubnodeConfig:
        tags = [t.to_proto() for t in self.tags.values()]
        methods = [m.to_proto() for m in self.methods.values()]
        subnodes = [s.to_proto() for s in self.subnodes.values()]
        return proto.SubnodeConfig(name=self.name, tags=tags, methods=methods, subnodes=subnodes)
    
    @classmethod
    def from_proto(cls, proto: proto.SubnodeConfig, parent: NodeKeySpace) -> Self:
        name = proto.name
        tags = {t.path: t for t in [TagConfig.from_proto(t) for t in proto.tags]}
        methods = {m.path: m for m in [Method.from_proto(m) for m in proto.methods]}
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

        self.tags: dict[str, TagConfig] = self.config.tags
        self.tag_write_responses: dict[str, dict[int, TagWriteResponseConfig]] = {key:{r.code:r for r in value.responses} for key, value in self.tags.items()}
        self.methods: dict[str, Method] = self.config.methods
        self.method_responses: dict[str, dict[int, MethodResponse]] = {key:{r.code:r for r in value.responses} for key, value in self.methods.items()}
        self.subnodes: dict[str, SubnodeConfig] = self.config.subnodes
    
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
        self.tags = self.meta.tags
        self.methods = self.meta.methods
        self.responses: dict[str, dict[int, MethodResponse]] = {key:{r.code:r for r in value.responses} for key, value in self.methods.items()}
        self.subnodes: dict[str, SubnodeConfig] = self.meta.subnodes
    
    def subnode(self, name: str) -> RemoteSubConnection:
        def on_close(key):
            pass
        if "/" in name:
            curr_node = self
            subnodes = name.split("/")
            for s in subnodes:
                if s not in curr_node.subnodes:
                    raise ValueError(f"No subnode {s}")
                curr_node = curr_node.subnodes[s]
            # we inherit comm
            # different uuid or same?
            assert isinstance(curr_node, SubnodeConfig)
            r = RemoteSubConnection(name, curr_node.ks, curr_node, self._comm, self.node_id, on_close)
            return r

        if name not in self.subnodes:
            raise ValueError(f"No subnode {name}") 
        curr_node = self.subnodes[name]
        r = RemoteSubConnection(name, curr_node.ks, curr_node, self._comm, self.node_id, on_close)
        return r
    
    def close(self):
        logger.warning("Cannot close a remote subnode connection. Close the root remote connection instead.")