from gedge.edge.data_type import DataType
from gedge.edge.gtypes import LivelinessCallback, MetaCallback, StateCallback, TagDataCallback, TagWriteHandler, Type, ZenohQueryCallback, Any
from gedge.edge.prop import Props
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
from gedge.edge.tag_data import TagData, from_tag_data
import zenoh

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

    def add_tag(self, path: str, type: Type, props: dict[str, Any] = {}) -> Tag:
        tag = Tag(path, DataType.from_type(type), Props.from_value(props), False, [], None)
        if path in self.tags:
            print(f"Warning: tag {path} already exists in edge node {self.key}, updating...")
            del self.tags[path]
        # print(f"adding tag on key: {path}")
        self.tags[path] = tag
        return tag

    def add_writable_tag(self, path: str, type: Type, write_handler: TagWriteHandler, responses: list[tuple[int, bool, dict[str, Any]]], props: dict[str, Any] = {}) -> Tag:
        tag = Tag(path, DataType.from_type(type), Props.from_value(props), True, responses, write_handler)
        if path in self.tags:
            print(f"Warning: tag {path} already exists in edge node {self.key}, updating...")
            del self.tags[path]
        print(f"adding tag on key: {path}")
        self.tags[path] = tag
        return tag
    
    def add_write_responses(self, path: str, responses: list[tuple[int, bool, dict[str, Any]]]):
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        tag = self.tags[path]
        for code, success, props in responses:
            tag.add_write_response(code, success, props)
    
    def add_write_response(self, path: str, code: int, success: bool, props: dict[str, Any] = {}):
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        self.tags[path].add_write_response(code, success, props)
    
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
        del self.tags[path]
    
    def add_method(self, path: str, handler, props: dict[str, Any] = {}):
        method = Method(path, handler, Props.from_value(props), {}, [])
        self.methods[path] = method
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
        del self.methods[path]
    
    def _verify_tags(self):
        for path in self.tags:
            tag = self.tags[path]
            if tag._writable:
                assert tag.write_handler is not None, f"Tag {path} declared as writable but no write handler"
                assert len(tag.responses) > 0, f"Tag {path} declared as writable but no responses registered for write handler"

    def build_meta(self) -> Meta:
        # print(f"building meta for {self.key}")
        self._verify_tags()
        tags: list[proto.Tag] = [t.to_proto() for t in self.tags.values()]
        methods: list[proto.Method] = [m.to_proto() for m in self.methods.values()]
        meta = Meta(tracking=False, key=self.key, tags=tags, methods=methods)
        return meta

    def connect(self):
        meta = self.build_meta()
        return NodeSession(config=self, meta=meta)

class NodeSession:
    def __init__(self, config: NodeConfig, meta: Meta):
        self._comm = Comm() 
        self.config = config
        self.ks = config.ks
        self.connections: list[RemoteConnection] = []

        # TODO: subscribe to our own meta to handle changes to config during session?
        self.meta = meta
        self.startup()
        self.tags: dict[str, Tag] = self.config.tags
        self.methods: dict[str, Method] = self.config.methods
        # print(self.config.methods)
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
        connection = [c for c in self.connections if c.key == key][0]
        self.connections.remove(connection)

    def _pull_meta_message(self, key: str) -> Meta:
        ks = NodeKeySpace.from_user_key(key)
        return self._comm.pull_meta_message(ks)

    def _pull_meta_messages(self, key_prefix: str, only_online: bool) -> list[Meta]:
        return self._comm.pull_meta_messages(key_prefix, only_online)

    def is_online(self, key: str) -> bool:
        return self._comm.is_online(NodeKeySpace.from_user_key(key))

    # Currently, node_on_network and nodes_on_network accept different types of keys
    # node_on_network receives <key_prefix>/<node_name>, which gets expanded to 
    # <key_prefix>/NODE/<node_name>/META
    # Meanwhile, nodes_on_network(...) accepts just a <key_prefix>, which gets expanded to
    # <key_prefix>/NODE/*/META
    def node_on_network(self, key: str) -> Meta:
        return self._pull_meta_message(key)
    
    def nodes_on_network(self, key_prefix: str, only_online: bool = False) -> list[Meta]:
        return self._pull_meta_messages(key_prefix, only_online)

    def print_nodes_on_network(self, key_prefix: str, only_online: bool = False):
        messages = self._pull_meta_messages(key_prefix, only_online=only_online)
        if len(messages) == 0:
            print("No Nodes on Network!")
            return
        print("Nodes on Network:")
        i = 1
        for meta in messages:
            _, _, name = meta.key.rpartition("/")
            print(f"{i}. {meta.key}: {"online" if self._comm.is_online(NodeKeySpace.from_user_key(meta.key), name) else "offline"}")
            print(f"{meta}\n")
            i += 1

    def connect_to_remote(self, key: str, on_state: StateCallback = None, on_meta: MetaCallback = None, on_liveliness_change: LivelinessCallback = None, tag_data_callbacks: dict[str, TagDataCallback] = {}) -> RemoteConnection:
        connection = RemoteConnection(RemoteConfig(key), self._comm, self._on_remote_close)
        if on_state:
            connection.add_state_callback(on_state)
        if on_meta:
            connection.add_meta_callback(on_meta)
        if on_liveliness_change:
            connection.add_liveliness_callback(on_liveliness_change)

        for path in tag_data_callbacks:
            connection.add_tag_data_callback(path, tag_data_callbacks[path])

        self.connections.append(connection)
        
        return connection

    def disconnect_from_remote(self, key: str):
        connection = [c for c in self.connections if c.key == key]
        if len(connection) == 0:
            raise ValueError(f"Node {key} not connected to {self.ks.user_key}")
        connection = connection[0]
        connection.close()
        self.connections.remove(connection)
    
    def close(self):
        for node in self.connections:
            self.disconnect_from_remote(node.key)
        self._comm.session.close()
    
    def _write_handler(self, path: str, callback: TagWriteHandler) -> ZenohQueryCallback:
        print("registered write callback")
        def _on_write(query: zenoh.Query) -> None:
            try:
                data: proto.TagData = self._comm.deserialize(proto.TagData(), query.payload.to_bytes())
                data: TagData = TagData.from_proto(data, self.tags[path].type).to_py()
                code = callback(str(query.key_expr), data)
                if code not in [r.code for r in self.tags[path].responses]:
                    raise Exception(f"Tag write handler for tag {path} given incorrect code {code} not found in callback config")
                response = WriteResponseData(code=code)
            except Exception as e:
                code = 500
                response = WriteResponseData(code=code, error=str(e))
            b = self._comm.serialize(response)
            query.reply(query.key_expr, payload=b)
        return _on_write
    
    def _method_call(self, path: str, handler):
        method = self.config.methods[path]
        def _method_call(query: zenoh.Query) -> zenoh.Reply:
            m: MethodCall = self._comm.deserialize(MethodCall(), query.payload.to_bytes())
            params: dict[str, Any] = {}
            for key, value in m.parameters.items():
                data_type = method.parameters[key]
                params[key] = from_tag_data(value, data_type.value)
            q = Query(self.ks, path, self._comm, query, query.parameters, method.responses)
            q.parameters = params
            handler(q)
        return _method_call
    
    def _verify_node_collision(self):
        # verify that key expression with this key prefix and name is not online
        metas = self._comm.pull_all_meta_messages(only_online=True)
        assert not any([x.key == self.ks.user_key for x in metas]), f"{[x.key for x in metas]} are online, and {self.ks.user_key} match!"

    def startup(self):
        self._verify_node_collision()
        prefix, name = self.ks.prefix, self.ks.name
        self._comm.send_meta(prefix, name, self.meta)
        self.update_state(True)
        self.node_liveliness = self._comm.liveliness_token(self.ks.liveliness_key_prefix)
        for path in self.config.tags:
            tag = self.config.tags[path]
            if not tag._writable: continue
            self._comm.tag_queryable(self.ks, path, self._write_handler(path, tag.write_handler))
        for path in self.config.methods:
            method = self.config.methods[path]
            self._comm.method_queryable(self.ks, path, self._method_call(path, method.handler))

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
        self._comm.send_state(self.ks.prefix, self.ks.name, State(online=online))
