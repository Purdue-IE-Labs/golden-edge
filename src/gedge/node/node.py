from __future__ import annotations

import pathlib
from re import sub
import uuid
from gedge.node.method import MethodConfig
from gedge.node.method_response import MethodResponseConfig
from gedge.node.tag_write_query import TagWriteQuery
from gedge.py_proto.base_type import BaseType
from gedge.py_proto.config import Config
from gedge.py_proto.data_model import DataObject
from gedge.py_proto.data_model_config import DataModelConfig, DataModelItemConfig
from gedge.py_proto.data_model_object_config import DataModelObjectConfig, find_latest_version, load, load_from_file
from gedge.py_proto.data_object_config import DataObjectConfig
from gedge.py_proto.params_config import ParamsConfig
from gedge.py_proto.props import Props
from gedge.node.remote import RemoteConnection
from gedge.proto import Meta, State, MethodResponse, MethodCall
from gedge import proto
from gedge.node.error import MethodLookupError, TagLookupError
from gedge.comm.comm import Comm
from gedge.py_proto.singleton import Singleton
from gedge.py_proto.tag_config import TagConfig, TagWriteResponseConfig
from gedge import py_proto
from gedge.node.tag_bind import TagBind
from gedge.comm.keys import *
import json5

from typing import Self, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from gedge.node.gtypes import LivelinessCallback, MetaCallback, StateCallback, TagDataCallback, TagBaseValue, Type, ZenohQueryCallback, TagWriteHandler, MethodHandler
    from gedge.node.subnode import SubnodeConfig
    from gedge.node.subnode import SubnodeSession

import logging
logger = logging.getLogger(__name__)

class NodeConfig:
    def __init__(self, key: str):
        self._user_key = key
        self.ks = NodeKeySpace.from_user_key(key)
        self.tags: dict[str, TagConfig] = dict()
        self.methods: dict[str, MethodConfig] = dict()
        self.subnodes: dict[str, SubnodeConfig] = dict()
        self.models: dict[str, DataModelConfig] = dict()

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
            tag = TagConfig.from_json5(tag_json)
            config.tags[tag.path] = tag

        for method_json in obj.get("methods", []):
            method = MethodConfig.from_json5(method_json)
            config.methods[method.path] = method

        from gedge.node.subnode import SubnodeConfig
        for subnode_json in obj.get("subnodes", []):
            subnode = SubnodeConfig.from_json5(subnode_json, config.ks)
            config.subnodes[subnode.name] = subnode
        
        return config
    
    def get_models_and_condense_to_paths(self) -> list[DataModelConfig]:
        models = []
        for tag in self.tags.values():
            if tag.is_base_type():
                continue
            m = tag.data_object_config.get_model_and_to_path()
            if m:
                models.append(m)
        for method in self.methods.values():
            for p in method.params.params:
                c = method.params.params[p]
                m = c.get_model_and_to_path()
                if m:
                    models.append(m)
            for r in method.responses:
                for b in r.body.body:
                    c = r.body.body[b]
                    m = c.get_model_and_to_path()
                    if m:
                        models.append(m)
        for subnode in self.subnodes.values():
            models += subnode.get_models_and_condense_to_paths()
        return models

    @property
    def key(self):
        return self._user_key

    @key.setter
    def key(self, key: str):
        self._user_key = key
        self.ks = NodeKeySpace.from_user_key(key)
    
    # experimenting with a decorator
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
    def _add_readable_tag(self, path: str, type: Type, props: dict[str, TagBaseValue] = {}):
        config = DataModelItemConfig(path, DataObjectConfig(Config(BaseType.from_py_type(type)), Props.from_value(props)))
        tag = TagConfig(config, False, [], None)
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

    def add_tag(self, path: str, type: Type, props: dict[str, Any] = {}) -> TagConfig:
        return self._add_readable_tag(path, type, props)
    
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
        method = MethodConfig(path, handler, Props.from_value(props), ParamsConfig.empty(), [])
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
        tags: list[proto.TagConfig] = [t.to_proto() for t in self.tags.values()]
        methods: list[proto.MethodConfig] = [m.to_proto() for m in self.methods.values()]
        subnodes: list[proto.SubnodeConfig] = [s.to_proto() for s in self.subnodes.values()]
        ms: list[proto.DataModelConfig] = [m.to_proto() for m in self.models.values()]
        meta = Meta(tracking=False, key=self.key, tags=tags, methods=methods, subnodes=subnodes, models=ms)
        print(f"Bytes of meta message: {len(meta.SerializeToString())}")
        return meta

    def _connect(self, connections: list[str]):
        logger.info(f"Node {self.key} attempting to connect to network")
        models = self.get_models_and_condense_to_paths()
        print('CONNECTING')
        print(self.methods)
        print(self.tags)
        print(self.subnodes)
        self.models = {m.full_path: m for m in models}
        return NodeSession(self, Comm(connections))

class NodeSession:
    def __init__(self, config: NodeConfig, comm: Comm):
        self._comm = comm
        self.config = config
        self.ks = config.ks
        self.connections: dict[str, RemoteConnection] = dict() # user_key -> RemoteConnection
        self.id = str(uuid.uuid4())
        self.tags: dict[str, TagConfig] = self.config.tags
        print(self.tags)
        self.tag_write_responses: dict[str, dict[int, TagWriteResponseConfig]] = {key:{r.code:r for r in value.responses} for key, value in self.tags.items()}
        self.methods: dict[str, MethodConfig] = self.config.methods
        self.method_responses: dict[str, dict[int, MethodResponseConfig]] = {key:{r.code:r for r in value.responses} for key, value in self.methods.items()}
        self.subnodes: dict[str, SubnodeConfig] = self.config.subnodes
        self.models: dict[str, DataModelConfig] = self.config.models
        print(self.models.keys())

        # connect
        self._comm.connect()
        self.add_parent_tags()

        # TODO: subscribe to our own meta to handle changes to config during session?
        self.meta = self.config.build_meta()

        # order here is important, we build the meta with the models having just their path in the tags, methods, subnodes, but embedded in the models
        # however, for simplicity of coding afterward, we embed the models
        self.fetch_models()
        logger.debug(f"Built meta: {self.meta}")

        self._startup()
        print(f"models: {self.models}")

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

        connection = RemoteConnection(NodeKeySpace.from_user_key(key), self._comm, self.id, self._on_remote_close)
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

    def _startup(self):
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
    
    def fetch_models(self):
        # fetch all things for now
        for path in self.tags:
            c = self.get_tag_config(path)
            self.tags[path].config.config = c

        for path in self.methods:
            for key in self.methods[path].params.params:
                # TODO: why do I write lines of code like this
                config = self.methods[path].params.params[key]
                c = self.get_data_object_config(config)
                self.methods[path].params.params[key] = c
            for response in self.methods[path].responses:
                for body in response.body.body:
                    config = response.body.body[body]
                    c = self.get_data_object_config(config)
                    response.body.body[body] = c

    def add_parent_tags(self):
        for model in self.models.values():
            model.add_parent_tags()

    def tag_binds(self, paths: list[str]) -> list[TagBind]:
        return [self.tag_bind(path) for path in paths]

    def tag_bind(self, path: str, value: Any = None) -> TagBind:
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        bind = TagBind(self.ks, self._comm, self.tags[path], value, self.update_tag)
        return bind
    
    def update_tag(self, path: str, value: Any | dict):
        tag = self.tags[path]
        logger.debug(f"Putting tag value {value} on path {path}")

        config = self.get_tag_config(path)
        res = DataObject.from_value(value, config)
        self._comm.update_tag(self.ks, tag.config.path, res.to_proto())
    
    def get_tag_config(self, path: str) -> DataObjectConfig:
        """
        we should just be able to do tag.config.config.
        However, we do not embed the models in tags or methods, only in the models part of meta,
        so if it is a model path, we must look it up
        """
        tag = self.tags[path]
        if tag.is_base_type():
            return tag.data_object_config
        else:
            c = tag.get_model_config()
            if c:
                return tag.data_object_config
            p = tag.get_model_path()
            assert p is not None
            return DataObjectConfig.from_model_config(self.models[p.full_path], tag.data_object_config.props)

    def get_data_object_config(self, config: DataObjectConfig) -> DataObjectConfig:
        if config.is_base_type():
            return config
        else:
            c = config.get_model_config()
            if c:
                return config
            p = config.get_model_path()
            assert p is not None
            print(self.models.keys())
            return DataObjectConfig.from_model_config(self.models[p.full_path], config.props)
            
    def get_model_from_meta(self, config: DataModelObjectConfig) -> DataModelConfig:
        c = config.get_embedded()
        if not c:
            p = config.get_path()
            assert p is not None
            if self.models.get(p.full_path) is None:
                raise LookupError(f"No model with path {p} in meta")
            return self.models[p.full_path]
        return c
    
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
