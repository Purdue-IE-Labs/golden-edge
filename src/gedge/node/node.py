from __future__ import annotations

import pathlib
import uuid
from gedge.node.method import MethodConfig
from gedge.node.method_response import ResponseConfig
from gedge.py_proto.base_data import BaseData
from gedge.py_proto.base_type import BaseType
from gedge.py_proto.conversions import props_from_json5
from gedge.py_proto.data_model import DataItem
from gedge.py_proto.data_model_config import DataModelConfig, DataItemConfig
from gedge.py_proto.data_model_ref import DataModelRef
from gedge.py_proto.props import Prop
from gedge.node.remote import RemoteConnection
from gedge import proto
from gedge.node.error import MethodLookupError, TagLookupError
from gedge.comm.comm import Comm
from gedge.py_proto.singleton import Singleton
from gedge.py_proto.state import State
from gedge.py_proto.tag_config import Tag, TagConfig
from gedge import py_proto
from gedge.node.tag_bind import TagBind
from gedge.comm.keys import *
import json5

from typing import Self, Any, TYPE_CHECKING

from gedge.py_proto.type import Type
if TYPE_CHECKING:
    from gedge.node.gtypes import LivelinessCallback, MetaCallback, StateCallback, TagDataCallback, TagBaseValue, ZenohQueryCallback, TagWriteHandler, MethodHandler
    from gedge.node.subnode import SubnodeConfig
    from gedge.node.subnode import SubnodeSession
    from gedge.py_proto.meta import Meta

import logging
logger = logging.getLogger(__name__)

class NodeConfig:
    def __init__(self, key: str):
        self._user_key = key
        self.ks = NodeKeySpace.from_user_key(key)
        self.tag_config = TagConfig({})
        self.methods: dict[str, MethodConfig] = dict()
        self.subnodes: dict[str, SubnodeConfig] = dict()
        self.models: dict[str, DataModelConfig] = dict()
        self.props: dict[str, Prop] = dict()

    @classmethod
    def from_json5(cls, path: str):
        '''
        Creates a new node by loading the opening the parameter path with read persmissions to json5 and returns the NodeConfig of the new node
        
        Arguments:
            cls (type[Self@NodeConfig]): The NodeConfig class
            path (str): The path being opened on and loaded into json5

        Returns:
            NodeConfig
        '''
        if not pathlib.Path(path).exists():
            raise ValueError(f"Node configuration at path {path} does not exist")
        if pathlib.Path(path).is_dir():
            raise ValueError(f"Node configuration at path {path} is a directory")
        with open(path, "r") as f:
            node: dict[str, Any] = json5.load(f)
        return cls._config_from_json5_obj(node)
    
    @classmethod
    def from_json5_str(cls, string: str):
        '''
        Creates a new node by loading the parameter string to json5 and returns the NodeConfig of the new node
        
        Arguments:
            cls (type[Self@NodeConfig]): The NodeConfig class
            string (str): The string being directly loaded to json5

        Returns:
            NodeConfig
        '''
        node: dict[str, Any] = json5.loads(string) # type: ignore
        return cls._config_from_json5_obj(node)

    @staticmethod
    def _config_from_json5_obj(obj: dict[str, Any]):
        if "key" not in obj:
            raise LookupError(f"Keyword 'key' not found for node configuration")
        config = NodeConfig(obj["key"])
        config.tag_config = TagConfig.from_json5(obj.get("tags", []), obj.get("writable_config", []), obj.get("group_config", []))

        for method_json in obj.get("methods", []):
            method = MethodConfig.from_json5(method_json)
            config.methods[method.path] = method

        from gedge.node.subnode import SubnodeConfig
        for subnode_json in obj.get("subnodes", []):
            subnode = SubnodeConfig.from_json5(subnode_json, config.ks)
            config.subnodes[subnode.name] = subnode
        
        props = {key: Prop.from_json5(key, p) for key, p in obj.get("props", {}).items()}
        config.props = props
        
        return config

    def get_models(self) -> list[DataModelConfig]:
        models = []
        for tag in self.tag_config.tag_list():
            if tag.is_base_type():
                continue
            m = tag.load_model()
            if m:
                m.add_parent_tags()
                models.append(m)
        for method in self.methods.values():
            for p in method.params:
                m = p.type.load_model()
                if m:
                    m.add_parent_tags()
                    models.append(m)
            for r in method.responses:
                for b in r.body:
                    m = b.load_model()
                    if m:
                        m.add_parent_tags()
                        models.append(m)
        for subnode in self.subnodes.values():
            models += subnode.get_models()
        return models

    @property
    def key(self):
        '''
        Returns the user key of the current NodeConfig
        
        Arguments:
            None
        
        Returns:
            str: The user key of the current NodeConfig
        '''
        return self._user_key

    @key.setter
    def key(self, key: str):
        '''
        Sets the user key to the passed key and sets the corresponding NodeKeySpace in self.ks

        Arguments:
            key (str): The passed key for the user
        
        Returns:
            None
        '''
        self._user_key = key
        self.ks = NodeKeySpace.from_user_key(key)
    
    # experimenting with a decorator
    @staticmethod
    def warn_duplicate_tag(func):
        '''
        Checks if paths already exist in the current Node and prints a warning if there's a duplicate value

        Arguments:
            func(any): The function being checked
        Returns:
            Any
        '''
        def wrapper(self: Self, *args, **kwargs):
            path = args[0]
            if path in self.tag_config.tags:
                logger.warning(f"Tag with path '{path}' already exists on node '{self.key}', overwriting...")
            result = func(self, *args, **kwargs)
            return result
        return wrapper
    
    @warn_duplicate_tag
    def _add_readable_tag(self, path: str, type: Type, props: dict[str, TagBaseValue] = {}):
        '''
        Adds a new readable tag with the passed path, type, and properties

        Arguments:
            path (str): The path to the tag
            type (Type): The type of the new tag
            props (dict[str, TagValue]): The properties of the new tag
        
        Returns:
            Tag: The added tag
        '''
        tag = Tag(DataItemConfig(path, type, props_from_json5(props)), {}, {})
        self.tag_config[path] = tag
        logger.info(f"Adding tag with path '{path}' on node '{self.key}'")
        return tag
    
    def subnode(self, name: str) -> SubnodeConfig:
        '''
        Outlines the subnodes of the current node and returns the SubnodeConfig of the passed node

        Arguments:
            name (str): The name of the Subnode

        Returns:
            SubnodeConfig
        '''
        if "/" in name:
            curr_node = self
            subnodes = name.split("/")
            for s in subnodes:
                if s not in curr_node.subnodes:
                    raise ValueError(f"No subnode {s} when trying to find subnode {name}")
                curr_node = curr_node.subnodes[s]
            return curr_node # type: ignore

        if name not in self.subnodes:
            raise ValueError(f"No subnode {name} in config for {self.key}") 
        return self.subnodes[name]

    def add_tag(self, path: str, type: Type, props: dict[str, Any] = {}) -> Tag:
        '''
        Adds a new tag to the current node

        Arguments:
            path (str): The path to the tag
            type (Type): The type of the tag
            props (dict[str, Any]): The properties of the tag

        Returns:
            Tag: The new Tag
        '''
        return self._add_readable_tag(path, type, props)
    
    def add_tag_write_handler(self, path: str, handler: TagWriteHandler):
        '''
        Adds a TagWriteHandler to a current tag at the passed path

        Arguments:
            path (str): The path to the tag
            handler (TagWriteHandler): The handler being added to the tag

        Returns:
            None
        '''
        self.tag_config.add_write_handler(path, handler)
    
    def add_method_handler(self, path: str, handler: MethodHandler):
        '''
        Adds a MethodHandler to a current method at the passed path

        Arguments:
            path (str): The path to the method
            handler (MethodHandler): The handler being added to the method

        Returns:
            None
        '''
        if path not in self.methods:
            raise MethodLookupError(path, self.ks.name)
        self.methods[path].handler = handler
    
    def delete_method(self, path: str):
        '''
        Deletes the method at the passed path

        Arguments:
            path (str): The path to the method

        Returns:
            None
        '''
        if path not in self.methods:
            raise MethodLookupError(path, self.ks.name)
        logger.info(f"Deleting tag with path '{path}' on node '{self.key}'")
        del self.methods[path]
    
    def _verify_tags(self):
        '''
        Verifies the tags of the node, checks the tag write handlers and the amount of responses for each tag

        Arguments:
            None
        
        Returns:
            None
        '''
        for path in self.tag_config:
            tag = self.tag_config[path]
            # TODO: fix, what to verify here vs. at config loading time?
            # if tag.writable:
            #     assert tag.handler is not None, f"Tag {path} declared as writable but no write handler was provided"
            #     assert len(tag.responses) > 0, f"Tag {path} declared as writable but no responses registered for write handler"
    
    def _verify_methods(self):
        '''
        Verifies the methods of the node, checks the method handlers

        Arguments:
            None
        
        Returns:
            None
        '''
        for path in self.methods:
            method = self.methods[path]
            assert method.handler is not None, f"Method {path} has no handler"

    # essentially to_proto() for the node
    def build_meta(self) -> Meta:
        '''
        Passes the node's tags, methods, and subnodes to proto and creates a Meta object

        Arguments:
            None
        
        Returns:
            Meta
        '''
        from gedge.py_proto.meta import Meta
        self._verify_tags()
        meta = Meta(self.key, self.tag_config, self.methods, self.subnodes, self.models, self.props)
        return meta

    def _connect(self, connections: list[str]):
        '''
        Creates a NodeSession with the passed connections

        Arguments:
            connections (list[str]): The connections created in the Session

        Returns:
            NodeSession: The created session with the passed connections
        '''
        logger.info(f"Node {self.key} attempting to connect to network")
        models = self.get_models()
        self.models = {m.full_path: m for m in models}

        # TODO: ensure they provided a handler for all tag writes and methods

        return NodeSession(self, Comm(connections))

class NodeSession:
    def __init__(self, config: NodeConfig, comm: Comm):
        self._comm = comm
        self.config = config
        self.ks = config.ks
        self.connections: dict[str, RemoteConnection] = dict() # user_key -> RemoteConnection
        self.id = str(uuid.uuid4())
        self.tag_config: TagConfig = self.config.tag_config
        self.methods: dict[str, MethodConfig] = self.config.methods
        self.method_responses: dict[str, dict[int, ResponseConfig]] = {key:{r.code:r for r in value.responses} for key, value in self.methods.items()}
        self.subnodes: dict[str, SubnodeConfig] = self.config.subnodes
        self.models: dict[str, DataModelConfig] = self.config.models

        # connect
        self._comm.connect()

        # TODO: subscribe to our own meta to handle changes to config during session?
        self.meta = self.config.build_meta()
        # TODO: put models in singleton?
        logger.debug(f"Built meta: {self.meta}")

        self._startup()

        self.binds: dict[str, TagBind] = {}

    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        self.update_state(False)
        self._comm.__exit__(*exc)

    def close(self):
        '''
        Closes the NodeSession

        Arguments:
            None
        
        Returns:
            None
        '''
        for key in self.connections:
            self.disconnect_from_remote(key)
        self.update_state(False)
        self._comm.session.close()

    def _on_remote_close(self, key: str):
        '''
        Deletes the connections at the passed key

        Arguments:
            key (str): The key of the remote connection

        Returns:
            None
        '''
        del self.connections[key]

    def is_online(self, key: str) -> bool:
        '''
        Returns the online state of the node corresponding to the passed key

        Arguments:
            key (str): The key of the node being checked

        Returns:
            bool: The online state of the node
        '''
        return self._comm.is_online(NodeKeySpace.from_user_key(key))

    def node_on_network(self, key: str) -> Meta:
        '''
        Returns the Meta of the node that corresponds to the passed key

        Arguments:
            key (str): The key of the node

        Returns:
            Meta: The Meta of the passed node
        '''
        ks = NodeKeySpace.from_user_key(key)
        return self._comm.pull_meta_message(ks)
    
    def nodes_on_network(self, only_online: bool = False) -> list[Meta]:
        '''
        Returns a list of the Metas of all of the nodes in the current Zenoh session

        Arguments:
            only_online (bool): The nodes only on the network
        
        Returns:
            list[Meta]
        '''
        metas = self._comm.pull_meta_messages(only_online)
        return metas

    def print_nodes_on_network(self, only_online: bool = False):
        '''
        Prints data about all the nodes on the network

        Arguments:
            only_online (bool): The nodes only on the network

        Returns:
            None
        '''
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
        '''
        Connects the current node to a remote node at 'key'
        Raises a ValueError if the remote node 'key' is not online

        Example Implementation:
            def state_callback(str, state):
                print(f"State changed: {state} for {str}")

            def meta_callback(meta_data):
                print(f"Received metadata: {meta_data}")

            def liveliness_callback(str, liveliness_status):
                print(f"Liveliness status: {liveliness_status}, {str}")

            def tag_data_callback(path, data):
                print(f"Tag data at {path}: {data}")
            
                remote = session.connect_to_remote(
                    key="path", 
                    on_state=state_callback, 
                    on_meta=meta_callback, 
                    on_liveliness_change=liveliness_callback, 
                    tag_data_callbacks={"tag": tag_data_callback})

        Arguments:
            key (str): The key of the remote node
            on_state (StateCallback | None): Optional StateCallback for the connection
            on_meta (MetaCallback | None): Optional MetaCallback for the connection
            on_liveliness_change (LivelinessCallback | None): Optional LivelinessCallback for the connection
            tag_data_callbacks (dict[str, TagDataCallbacks] = {}): Optional Dictionary of TagDataCallbacks

        Returns:
            RemoteConnection: The new connection between the current node and remote node
        '''
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
        '''
        Disconnects from the remote node that corresponds to the passed key

        Arguments:
            key (str): The key to the remote node being disconnected from

        Returns:
            None
        '''
        if key not in self.connections:
            raise ValueError(f"Node {key} not connected to {self.ks.user_key}")
        connection = self.connections[key]
        connection.close()
        del self.connections[key]
    
    def _verify_node_collision(self):
        '''
        Verifies if the current node is NOT listed in the metas of the current connection

        Arguments:
            None
        
        Returns:
            None
        '''
        # verify that key expression with this key prefix and name is not online
        metas = self._comm.pull_meta_messages(only_online=True)
        # TODO: this is becoming an expensive operation? Either that or my computer is buggin
        assert not any([x.key == self.ks.user_key for x in metas]), f"{[x.key for x in metas]} are online, and {self.ks.user_key} match!"

    def _startup(self):
        '''
        The startup sequence of the NodeSession: Basic verification, hooks up TagWrite and Method handlers, and adds subnode callbacks

        Arguments:
            None
        
        Returns:
            None
        '''
        logger.debug(f"Verifying node collisions...")
        self._verify_node_collision()
        logger.info("Publishing node's meta")
        self._comm.send_meta(self.ks, self.meta)
        self.update_state(True)
        self.node_liveliness = self._comm.liveliness_token(self.ks)
        logger.info(f"Registering tags and methods on node {self.config.key}")
        for path in self.config.tag_config.all_writable_tags():
            # hook up tag write handlers
            tag = self.config.tag_config.get_tag(path)
            if not tag.is_writable():
                continue
            self._comm.tag_queryable(self.ks, tag, path) 
        for path in self.config.methods:
            # hook up method handlers
            method = self.config.methods[path]
            self._comm.method_queryable(self.ks, method) 
        
        def add_subnode_callbacks(config: SubnodeConfig):
            for path in config.tag_config.all_writable_tags():
                tag = config.tag_config[path]
                if not tag.is_writable():
                    continue
                self._comm.tag_queryable(config.ks, tag, path) 
            for path in config.methods:
                method = config.methods[path]
                self._comm.method_queryable(config.ks, method) 
            for name in config.subnodes:
                subnode = config.subnodes[name]
                add_subnode_callbacks(subnode)
        
        for s in self.config.subnodes.values():
            add_subnode_callbacks(s)

    def tag_binds(self, paths: list[str]) -> list[TagBind]:
        '''
        Updates all the tags on your own node that match the passed paths

        Note: To understand how an individual tag_bind functions look at the function tag_bind

        Arguments:
            paths (list[str]): The list of paths for the tags

        Returns:
            list[TagBind]: The list of the new TagBinds
        '''
        return [self.tag_bind(path) for path in paths]

    def tag_bind(self, path: str, value: Any = None) -> TagBind:
        '''
        Updates the tag at the passed back on your own node with an optional passed value

        Example Implementation:
            config = gedge.NodeConfig.from_json5("...")
            config.add_method_handler("...", handler=?)
            
            with gedge.connect(config, "...") as session:
                session.tag_bind(path="...")
                OR
                session.tag_bind(path="...", value=?)
            

        Arguments:
            path (str): The path of the tag
            value (Any | Optional): The value for the TagBind

        Returns:
            TagBind: The new TagBind
        '''
        if not self.tag_config.is_valid_path(path):
            raise ValueError(f"cannot bind to invalid path {path}")
        if not self.tag_config.is_base_type(path):
            raise ValueError(f"cannot bind to model tag (only base tags) {path}")
        bind = TagBind(self.ks, path, self._comm, self.tag_config, value, self._update_tag, self._on_tag_bind_close)
        self.binds[path] = bind
        return bind
    
    def _on_tag_bind_close(self, path: str):
        del self.binds[path]
    
    def update_tag(self, path: str, value: TagBaseValue):
        '''
        Updates the tag at the passed path with the passed value

        Arguments:
            path (str): The path of the tag
            value (Any): the value being passed to the Tag

        Returns:
            None
        '''

        tag = self.tag_config.get_tag(path)
        group = self.tag_config.get_group(path)
        if group:
            self.update_group({path: value})
            return
        self._update_tag(path, value, tag)

        if path in self.binds:
            self.binds[path]._update_value_externally(value)

    def _update_tag(self, path: str, value: TagBaseValue, tag: Tag):
        '''
        Updates the tag at the passed path with the passed value

        Arguments:
            path (str): The path of the tag
            value (Any): the value being passed to the Tag

        Returns:
            None
        '''
        config = tag.get_config(path)
        logger.debug(f"Putting tag value {value} on path {path}")
        d = BaseData.from_value(value, config.get_base_type()).to_proto() # type: ignore
        self._comm.update_tag(self.ks, path, d)
    
    def update_group(self, group: dict[str, Any]):
        groups = self.tag_config.get_groups(list(group.keys()))
        if len(groups) > 1:
            raise ValueError(f"tags are from multiple groups: {groups}")
        elif len(groups) == 0:
            raise ValueError(f"no groups found for group {list(group.keys())}")
        
        group_path: str = groups.pop()
        new_group: dict[str, proto.BaseData] = {}
        for path, value in group.items():
            config = self.tag_config.get_config(path)
            t = config.get_base_type()
            assert t is not None
            new_group[path] = BaseData.from_value(value, config.get_base_type()).to_proto() # type: ignore
        di = proto.TagGroup(data=new_group)
        key_expr = self.ks.group_data_path(group_path)
        self._comm.send_group(key_expr, di)

    def get_model_from_meta(self, config: DataModelRef) -> DataModelConfig:
        if self.models.get(config.full_path) is None:
            raise LookupError(f"No model with path {config.full_path} in meta")
        return self.models[config.full_path]
    
    def update_state(self, online: bool):
        '''
        Updates the state of the current NodeKeySpace with the passed online state

        Arguments:
            online (bool): The online state of the NodeKeySpace

        Returns:
            None
        '''
        online_str = "online" if online else "offline"
        logger.info(f"Updating node state: {online_str}")
        self._comm.send_state(self.ks, State(online))

    def subnode(self, name: str) -> SubnodeSession:
        '''
        Creates a SubnodeSession for the subnode that has the passed name

        Arguments:
            name (str): The name of subnode

        Returns:
            SubnodeSession: The new session for the subnode
        '''
        from gedge.node.subnode import SubnodeSession

        logger.info(f"Fetching subnode {name}...")

        # need to return a subnode session
        if "/" in name:
            curr_node: NodeConfig | SubnodeConfig = self.config
            subnodes = name.split("/")
            for s in subnodes:
                if s not in curr_node.subnodes:
                    raise ValueError(f"No subnode {s} when trying to find subnode {name}")
                curr_node = curr_node.subnodes[s]
            session = SubnodeSession(curr_node, self._comm) # type: ignore
            logger.debug(f"Found subnode with name {curr_node.name}") # type: ignore
            return session

        if name not in self.subnodes:
            raise ValueError(f"No subnode {name} in config for {self.config.key}") 
        session = SubnodeSession(self.config.subnodes[name], self._comm)
        logger.debug(f"Found subnode with name {name}")
        return session

    def sleep(self):
        '''
        Silly function for anyone that is scared to write these two lines of code
        '''
        while True:
            pass