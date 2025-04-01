from __future__ import annotations

from re import sub
import uuid
from gedge.node.tag_write_query import TagWriteQuery
from gedge.node.data_type import DataType
from gedge.node.prop import Props
from gedge.node.remote import RemoteConfig, RemoteConnection
from gedge.proto import Meta, State, WriteResponseData, MethodQueryData
from gedge import proto
from gedge.node.error import MethodLookupError, TagLookupError
from gedge.comm.comm import Comm
from gedge.node.tag import Tag, WriteResponse
from gedge.node.tag_bind import TagBind
from gedge.comm.keys import *
from gedge.node.method import Method, MethodResponse
from gedge.node.tag_data import TagData 
import json5

from typing import Self, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from gedge.node.gtypes import LivelinessCallback, MetaCallback, StateCallback, TagDataCallback, TagValue, Type, ZenohQueryCallback, TagWriteHandler, MethodHandler
    from gedge.node.subnode import SubnodeConfig
    from gedge.node.subnode import SubnodeSession

import logging
logger = logging.getLogger(__name__)

class NodeConfig:
    def __init__(self, key: str):
        self._user_key = key
        self.ks = NodeKeySpace.from_user_key(key)
        self.tags: dict[str, Tag] = dict()
        self.methods: dict[str, Method] = dict()
        self.subnodes: dict[str, SubnodeConfig] = dict()

    @classmethod
    def from_json5(cls, path: str):
        with open(path, "r") as f:
            node: dict[str, Any] = json5.load(f)
        return cls._config_from_json5_obj(node)
    
    @classmethod
    def from_json5_str(cls, string: str):
        node: dict[str, Any] = json5.loads(string) # type: ignore
        return cls._config_from_json5_obj(node)

    @staticmethod
    def _config_from_json5_obj(obj: dict[str, Any]):
        if "key" not in obj:
            raise LookupError(f"Node must have a key")
        config = NodeConfig(obj["key"])
        for tag_json in obj.get("tags", []):
            tag = Tag.from_json5(tag_json)
            config.tags[tag.path] = tag
        for method_json in obj.get("methods", []):
            method = Method.from_json5(method_json)
            config.methods[method.path] = method
        from gedge.node.subnode import SubnodeConfig
        for subnode_json in obj.get("subnodes", []):
            subnode = SubnodeConfig.from_json5(subnode_json, config.ks)
            config.subnodes[subnode.name] = subnode
        return config

    @property
    def key(self):
        return self._user_key

    @key.setter
    def key(self, key: str):
        self._user_key = key
        self.ks = NodeKeySpace.from_user_key(key)
    
    @staticmethod
    def warn_duplicate_tag(func):
        def wrapper(self: Self, *args, **kwargs):
            path = args[0]
            if path in self.tags:
                logger.warning(f"Tag with path '{path}' already exists on node '{self.key}', overwriting...")
            result = func(self, *args, **kwargs)
            return result
        return wrapper
    
    @warn_duplicate_tag
    def _add_readable_tag(self, path: str, type: Type, props: dict[str, TagValue] = {}):
        tag = Tag(path, DataType.from_type(type), Props.from_value(props), False, [], None)
        self.tags[path] = tag
        logger.info(f"Adding tag with path '{path}' on node '{self.key}'")
        return tag
    
    def subnode(self, name: str) -> SubnodeConfig:
        if "/" in name:
            curr_node = self
            subnodes = name.split("/")
            for s in subnodes:
                if s not in curr_node.subnodes:
                    raise ValueError(f"No subnode {s}")
                curr_node = curr_node.subnodes[s]
            return curr_node # type: ignore

        if name not in self.subnodes:
            raise ValueError(f"No subnode {name}") 
        return self.subnodes[name]

    def add_tag(self, path: str, type: Type, props: dict[str, Any] = {}) -> Tag:
        return self._add_readable_tag(path, type, props)

    def add_writable_tag(self, path: str, type: Type, write_handler: TagWriteHandler, responses: list[tuple[int, dict[str, Any]]], props: dict[str, Any] = {}) -> Tag:
        tag = self._add_readable_tag(path, type, props)
        return tag.writable(write_handler, responses)
    
    def add_write_responses(self, path: str, responses: list[tuple[int, dict[str, Any]]]):
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        tag = self.tags[path]
        for code, props in responses:
            tag.add_write_response(code, Props.from_value(props))
    
    def add_write_response(self, path: str, code: int, props: dict[str, Any] = {}):
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        self.tags[path].add_write_response(code, Props.from_value(props))
    
    def add_tag_write_handler(self, path: str, handler: TagWriteHandler):
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        self.tags[path].add_write_handler(handler)
    
    def add_method_handler(self, path: str, handler: MethodHandler):
        if path not in self.methods:
            raise MethodLookupError(path, self.ks.name)
        self.methods[path].handler = handler
    
    def add_props(self, path: str, props: dict[str, Any]):
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        self.tags[path].add_props(props)

    def delete_tag(self, path: str):
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        logger.info(f"Deleting tag with path '{path}' on node '{self.key}'")
        del self.tags[path]
    
    def add_method(self, path: str, handler, props: dict[str, Any] = {}):
        method = Method(path, handler, Props.from_value(props), {}, [])
        self.methods[path] = method
        logger.info(f"Adding method with path '{path}' on node '{self.key}'")
        return method
    
    def delete_method(self, path: str):
        if path not in self.methods:
            raise MethodLookupError(path, self.ks.name)
        logger.info(f"Deleting tag with path '{path}' on node '{self.key}'")
        del self.methods[path]
    
    def _verify_tags(self):
        for path in self.tags:
            tag = self.tags[path]
            if tag.is_writable():
                assert tag.write_handler is not None, f"Tag {path} declared as writable but no write handler was provided"
                assert len(tag.responses) > 0, f"Tag {path} declared as writable but no responses registered for write handler"
    
    def _verify_methods(self):
        for path in self.methods:
            method = self.methods[path]
            assert method.handler is not None, f"Method {path} has no handler"

    # essentially to_proto() for the node
    def build_meta(self) -> Meta:
        self._verify_tags()
        tags: list[proto.Tag] = [t.to_proto() for t in self.tags.values()]
        methods: list[proto.Method] = [m.to_proto() for m in self.methods.values()]
        subnodes: list[proto.Subnode] = [s.to_proto() for s in self.subnodes.values()]
        meta = Meta(tracking=False, key=self.key, tags=tags, methods=methods, subnodes=subnodes)
        return meta

    def _connect(self, connections: list[str]):
        logger.info(f"Node {self.key} attempting to connect to network")
        return NodeSession(self, Comm(connections))

class NodeSession:
    def __init__(self, config: NodeConfig, comm: Comm):
        self._comm = comm
        self.config = config
        self.ks = config.ks
        self.connections: dict[str, RemoteConnection] = dict() # user_key -> RemoteConnection
        self.id = str(uuid.uuid4())

        # TODO: subscribe to our own meta to handle changes to config during session?
        self.meta = self.config.build_meta()

        # connect
        self._comm.connect()

        self.startup()
        self.tags: dict[str, Tag] = self.config.tags
        self.tag_write_responses: dict[str, dict[int, WriteResponse]] = {key:{r.code:r for r in value.responses} for key, value in self.tags.items()}
        self.methods: dict[str, Method] = self.config.methods
        self.method_responses: dict[str, dict[int, MethodResponse]] = {key:{r.code:r for r in value.responses} for key, value in self.methods.items()}
        self.subnodes: dict[str, SubnodeConfig] = self.config.subnodes

    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        self.update_state(False)
        self._comm.__exit__(*exc)

    def close(self):
        for key in self.connections:
            self.disconnect_from_remote(key)
        self.update_state(False)
        self._comm.session.close()

    def _on_remote_close(self, key: str):
        del self.connections[key]

    def is_online(self, key: str) -> bool:
        return self._comm.is_online(NodeKeySpace.from_user_key(key))

    def node_on_network(self, key: str) -> Meta:
        ks = NodeKeySpace.from_user_key(key)
        return self._comm.pull_meta_message(ks)
    
    def nodes_on_network(self, only_online: bool = False) -> list[Meta]:
        metas = self._comm.pull_meta_messages(only_online)
        return metas

    def print_nodes_on_network(self, only_online: bool = False):
        metas = self.nodes_on_network(only_online)
        if len(metas) == 0:
            print("No Nodes on Network!")
            return
        print("Nodes on Network:")
        i = 1
        for meta in metas:
            _, _, name = meta.key.rpartition("/")
            online = "online" if self._comm.is_online(NodeKeySpace.from_user_key(meta.key)) else "offline"
            print(f"{i}. {meta.key}: {online}")
            print(f"{meta}\n")
            i += 1

    def connect_to_remote(self, key: str, on_state: StateCallback | None = None, on_meta: MetaCallback | None = None, on_liveliness_change: LivelinessCallback | None = None, tag_data_callbacks: dict[str, TagDataCallback] = {}) -> RemoteConnection:
        logger.info(f"Node {self.config.key} connecting to remote node {key}")
        connection = RemoteConnection(RemoteConfig(key), NodeKeySpace.from_user_key(key), self._comm, self.id, self._on_remote_close)
        if on_state:
            connection.add_state_callback(on_state)
        if on_meta:
            connection.add_meta_callback(on_meta)
        if on_liveliness_change:
            connection.add_liveliness_callback(on_liveliness_change)

        for path in tag_data_callbacks:
            connection.add_tag_data_callback(path, tag_data_callbacks[path])

        self.connections[key] = connection
        
        return connection

    def disconnect_from_remote(self, key: str):
        if key not in self.connections:
            raise ValueError(f"Node {key} not connected to {self.ks.user_key}")
        connection = self.connections[key]
        connection.close()
        del self.connections[key]
    
    def _verify_node_collision(self):
        # verify that key expression with this key prefix and name is not online
        metas = self._comm.pull_meta_messages(only_online=True)
        assert not any([x.key == self.ks.user_key for x in metas]), f"{[x.key for x in metas]} are online, and {self.ks.user_key} match!"

    def startup(self):
        logger.debug(f"Verifying node collisions...")
        self._verify_node_collision()
        logger.info("Publishing node's meta")
        self._comm.send_meta(self.ks, self.meta)
        self.update_state(True)
        self.node_liveliness = self._comm.liveliness_token(self.ks)
        logger.info(f"Registering tags and methods on node {self.config.key}")
        for path in self.config.tags:
            # hook up tag write handlers
            tag = self.config.tags[path]
            if not tag.is_writable():
                continue
            assert tag.write_handler is not None
            self._comm.tag_queryable(self.ks, tag) 
        for path in self.config.methods:
            # hook up method handlers
            method = self.config.methods[path]
            self._comm.method_queryable(self.ks, method) 
        
        def add_subnode_callbacks(config: SubnodeConfig):
            for path in config.tags:
                tag = config.tags[path]
                if not tag.is_writable():
                    continue
                assert tag.write_handler is not None
                self._comm.tag_queryable(config.ks, tag) 
            for path in config.methods:
                method = config.methods[path]
                self._comm.method_queryable(config.ks, method) 
            for name in config.subnodes:
                subnode = config.subnodes[name]
                add_subnode_callbacks(subnode)
        
        for s in self.config.subnodes.values():
            add_subnode_callbacks(s)

    def tag_binds(self, paths: list[str]) -> list[TagBind]:
        return [self.tag_bind(path) for path in paths]

    def tag_bind(self, path: str, value: Any = None) -> TagBind:
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        bind = TagBind(self.ks, self._comm, self.tags[path], value, self.update_tag)
        return bind
    
    def update_tag(self, path: str, value: Any):
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        tag = self.tags[path]
        logger.info(f"Updating tag at path {path} with value {value}")
        self._comm.update_tag(self.ks, tag.path, TagData.py_to_proto(value, tag.type))
    
    def update_state(self, online: bool):
        online_str = "online" if online else "offline"
        logger.info(f"Updating node state: {online_str}")
        self._comm.send_state(self.ks, State(online=online))

    def subnode(self, name: str) -> SubnodeSession:
        from gedge.node.subnode import SubnodeSession
        # need to return a subnode session
        if "/" in name:
            curr_node: NodeConfig | SubnodeConfig = self.config
            subnodes = name.split("/")
            for s in subnodes:
                if s not in curr_node.subnodes:
                    raise ValueError(f"No subnode {s}")
                curr_node = curr_node.subnodes[s]
            session = SubnodeSession(curr_node, self._comm) # type: ignore
            return session

        if name not in self.subnodes:
            raise ValueError(f"No subnode {name}") 
        session = SubnodeSession(self.config.subnodes[name], self._comm)
        return session
