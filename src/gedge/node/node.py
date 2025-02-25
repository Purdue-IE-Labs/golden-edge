from gedge.edge.data_type import DataType
from gedge.edge.gtypes import LivelinessCallback, MetaCallback, StateCallback, TagDataCallback, TagValue, TagWriteHandler, Type, ZenohQueryCallback, Any
from gedge.edge.prop import Props
from gedge.node import codes
from gedge.node.query import Query
from gedge.node.remote import RemoteConfig, RemoteConnection
from gedge.proto import Meta, State, WriteResponseData, MethodCall
from gedge import proto
from gedge.edge.error import MethodLookupError, TagLookupError
from gedge.comm.comm import Comm
from gedge.edge.tag import Tag
from gedge.edge.tag_bind import TagBind
from gedge.comm.keys import *
from gedge.node.method import Method, Response
from gedge.edge.tag_data import TagData 
import zenoh

import logging
logger = logging.getLogger(__name__)


# TODO: eventually, should support JSON
class NodeConfig:
    def __init__(self, key: str):
        self._user_key = key
        self.ks = NodeKeySpace.from_user_key(key)
        self.tags: dict[str, Tag] = dict()
        self.methods: dict[str, Method] = dict()

    @property
    def key(self):
        return self._user_key

    @key.setter
    def key(self, key: str):
        self._user_key = key
        self.ks = NodeKeySpace.from_user_key(key)
    
    def _add_readable_tag(self, path: str, type: Type, props: dict[str, TagValue] = {}):
        tag = Tag(path, DataType.from_type(type), Props.from_value(props), False, [], None)
        if path in self.tags:
            logger.warning(f"Tag with path '{path}' already exists on node '{self.key}', overwriting...")
            del self.tags[path]
        self.tags[path] = tag
        logger.info(f"Adding tag with path '{path}' on node '{self.key}'")
        return tag

    def add_tag(self, path: str, type: Type, props: dict[str, Any] = {}) -> Tag:
        return self._add_readable_tag(path, type, props)

    def add_writable_tag(self, path: str, type: Type, write_handler: TagWriteHandler, responses: list[tuple[int, bool, dict[str, Any]]], props: dict[str, Any] = {}) -> Tag:
        tag = self._add_readable_tag(path, type, props)
        return tag.writable(write_handler, responses)
    
    def add_write_responses(self, path: str, responses: list[tuple[int, bool, dict[str, Any]]]):
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        tag = self.tags[path]
        for code, props in responses:
            tag.add_write_response(code, props)
    
    def add_write_response(self, path: str, code: int, props: dict[str, Any] = {}):
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        self.tags[path].add_write_response(code, props)
    
    def add_write_handler(self, path: str, callback: TagWriteHandler):
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        self.tags[path].add_write_handler(callback)
    
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
    
    def add_params(self, path: str, **kwargs):
        if path not in self.methods:
            raise MethodLookupError(path, self.ks.name)
        method = self.methods[path]
        method.add_params([(key, value) for key, value in kwargs.items()])
    
    def add_response(self, path: str, response: Response):
        if path not in self.methods:
            raise MethodLookupError(path, self.ks.name)
        method = self.methods[path]
        method.add_response(response)
    
    def delete_method(self, path: str):
        if path not in self.methods:
            raise MethodLookupError(path, self.ks.name)
        logger.info(f"Deleting tag with path '{path}' on node '{self.key}'")
        del self.methods[path]
    
    def _verify_tags(self):
        for path in self.tags:
            tag = self.tags[path]
            if tag._writable:
                assert tag.write_handler is not None, f"Tag {path} declared as writable but no write handler was provided"
                assert len(tag.responses) > 0, f"Tag {path} declared as writable but no responses registered for write handler"

    def build_meta(self) -> Meta:
        self._verify_tags()
        tags: list[proto.Tag] = [t.to_proto() for t in self.tags.values()]
        methods: list[proto.Method] = [m.to_proto() for m in self.methods.values()]
        meta = Meta(tracking=False, key=self.key, tags=tags, methods=methods)
        return meta

    def connect(self):
        logger.info(f"Node {self.key} attempting to connect to network")
        meta = self.build_meta()
        return NodeSession(config=self, meta=meta)

class NodeSession:
    def __init__(self, config: NodeConfig, meta: Meta):
        self._comm = Comm() 
        self.config = config
        self.ks = config.ks
        self.connections: dict[str, RemoteConnection] = dict() # user_key -> RemoteConnection

        # TODO: subscribe to our own meta to handle changes to config during session?
        self.meta = meta
        self.startup()
        self.tags: dict[str, Tag] = self.config.tags
        self.methods: dict[str, Method] = self.config.methods
        self.responses: dict[str, dict[int, Response]] = {key:{r.code:r for r in value.responses} for key, value in self.methods.items()}

    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        self.update_state(False)
        self._comm.__exit__(*exc)

    def close(self):
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
            print(f"{i}. {meta.key}: {"online" if self._comm.is_online(NodeKeySpace.from_user_key(meta.key), name) else "offline"}")
            print(f"{meta}\n")
            i += 1

    def connect_to_remote(self, key: str, on_state: StateCallback = None, on_meta: MetaCallback = None, on_liveliness_change: LivelinessCallback = None, tag_data_callbacks: dict[str, TagDataCallback] = {}) -> RemoteConnection:
        logger.info(f"Node {self.config.key} connecting to remote node {key}")
        connection = RemoteConnection(RemoteConfig(key), self._comm, self._on_remote_close)
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
    
    def close(self):
        for key in self.connections:
            self.disconnect_from_remote(key)
        self._comm.session.close()
    
    def _write_handler(self, path: str, handler: TagWriteHandler) -> ZenohQueryCallback:
        def _on_write(query: zenoh.Query) -> None:
            try:
                data: proto.TagData = self._comm.deserialize(proto.TagData(), query.payload.to_bytes())
                data: TagData = TagData.from_proto(data, self.tags[path].type).to_py()
                logger.info(f"Node {self.config.key} received tag write at path '{path}' with value '{data.value}'")
                code = handler(str(query.key_expr), data.value)
                if code not in [r.code for r in self.tags[path].responses]:
                    raise Exception(f"Tag write handler for tag {path} given incorrect code {code} not found in callback config")
                response = WriteResponseData(code=code)
            except Exception as e:
                response = WriteResponseData(code=codes.TAG_ERROR, error=repr(e))
            b = self._comm.serialize(response)
            query.reply(query.key_expr, payload=b)
        return _on_write
    
    def _method_call(self, path: str, handler):
        logger.info(f"Setting up method at path: {path} on node {self.ks.user_key}")
        method = self.config.methods[path]
        def _method_call(sample: zenoh.Sample) -> None:
            m: MethodCall = self._comm.deserialize(MethodCall(), sample.payload.to_bytes())
            params: dict[str, Any] = {}
            for key, value in m.parameters.items():
                data_type = method.parameters[key]
                params[key] = TagData.proto_to_py(value, data_type)
            key_expr = key_join(str(sample.key_expr), "response")
            q = Query(key_expr, self._comm, params, method.responses)
            try:
                logger.info(f"Node {self.config.key} method call at path '{path}' with parameters {params}")
                logger.debug(f"Received from {str(sample.key_expr)}")
                handler(q)
            except Exception as e:
                code = codes.METHOD_ERROR
                q.reply(code=code, error=repr(e))
            else:
                q.reply(code=codes.DONE)
        return _method_call
    
    def _verify_node_collision(self):
        # verify that key expression with this key prefix and name is not online
        metas = self._comm.pull_meta_messages(only_online=True)
        assert not any([x.key == self.ks.user_key for x in metas]), f"{[x.key for x in metas]} are online, and {self.ks.user_key} match!"

    def startup(self):
        self._verify_node_collision()
        self._comm.send_meta(self.ks, self.meta)
        self.update_state(True)
        self.node_liveliness = self._comm.liveliness_token(self.ks)
        logger.info(f"Registering tags and methods on node {self.config.key}")
        for path in self.config.tags:
            tag = self.config.tags[path]
            if not tag._writable: continue
            self._comm.tag_queryable(self.ks, path, self._write_handler(path, tag.write_handler))
        for path in self.config.methods:
            method = self.config.methods[path]
            self._comm.method_queryable_v2(self.ks, path, self._method_call(path, method.handler))

    def tag_binds(self, paths: list[str]) -> list[TagBind]:
        return [self.tag_bind(path) for path in paths]

    def tag_bind(self, path: str, value: Any = None) -> TagBind:
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        bind = TagBind(self.ks, self._comm, self.tags[path], value, self.update_tag)
        return bind
    
    def update_tag(self, path: str, value: Any):
        prefix = self.ks.prefix
        node_name = self.ks.name
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        tag = self.tags[path]
        self._comm.update_tag(prefix, node_name, tag.path, TagData.py_to_proto(value, tag.type))
    
    def update_state(self, online: bool):
        self._comm.send_state(self.ks, State(online=online))
