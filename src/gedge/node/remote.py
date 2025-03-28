from __future__ import annotations

from queue import Queue, Empty
import time
from gedge.node.tag_data import TagData
from gedge.node.method import Method
from gedge.node.method_reply import MethodReply
from gedge.node.method_response import MethodResponse
from gedge.node import codes
from gedge import proto
from gedge.node.error import MethodLookupError, SessionError, TagLookupError
from gedge.comm.comm import Comm
from gedge.node.tag import Tag
from gedge.node.tag_bind import TagBind
from gedge.comm.keys import *
import uuid

from typing import Any, Iterator, Callable, TYPE_CHECKING

from gedge.node.tag_write_reply import TagWriteReply
if TYPE_CHECKING:
    from gedge.node.gtypes import TagDataCallback, StateCallback, MetaCallback, LivelinessCallback, MethodReplyCallback
    from gedge.node.subnode import RemoteSubConnection

import logging
logger = logging.getLogger(__name__)

class RemoteConfig:
    def __init__(self, key: str, read_tags: list[str] = [], read_write_tags: list[str] = [], method_calls: list[str] = []):
        self.key = key
        self.read_tags = read_tags
        self.read_write_tags = read_write_tags
        self.method_calls = method_calls

class RemoteConnection:
    def __init__(self, config: RemoteConfig, ks: NodeKeySpace, comm: Comm, node_id: str, on_close: Callable[[str], None] | None = None):
        self.config = config
        self._comm = comm 
        self.key = self.config.key
        self.ks = ks
        self.on_close = on_close

        self.node_id = node_id

        '''
        TODO: perhaps we should subscribe to this node's meta message, in which case all the following utility variables (self.tags, self.methods, self.responses) 
        would need to react to that (i.e. be properties)
        '''
        self.meta = self._comm.pull_meta_message(ks)
        tags: list[Tag] = [Tag.from_proto(t) for t in self.meta.tags]
        self.tags = {t.path: t for t in tags}
        methods: list[Method] = [Method.from_proto(m) for m in self.meta.methods]
        self.methods = {m.path: m for m in methods}
        self.responses: dict[str, dict[int, MethodResponse]] = {key:{r.code:r for r in value.responses} for key, value in self.methods.items()}

        from gedge.node.subnode import SubnodeConfig
        subnodes: list[SubnodeConfig] = [SubnodeConfig.from_proto(s, self.ks) for s in self.meta.subnodes]
        self.subnodes: dict[str, SubnodeConfig] = {s.name: s for s in subnodes}

    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        self.close()
        self._comm.__exit__(*exc)
    
    def close(self):
        self._comm.close_remote(self.ks)
        if self.on_close is not None:
            self.on_close(self.key)
    
    def add_tag_data_callback(self, path: str, on_tag_data: TagDataCallback) -> None:
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)

        self.config.read_write_tags.append(path)
        self._comm.tag_data_subscriber(self.ks, path, on_tag_data, self.tags)

    def add_state_callback(self, on_state: StateCallback) -> None:
        self._comm.state_subscriber(self.ks, on_state)

    def add_meta_callback(self, on_meta: MetaCallback) -> None:
        self._comm.meta_subscriber(self.ks, on_meta)

    def add_liveliness_callback(self, on_liveliness_change: LivelinessCallback) -> None:
        self._comm.liveliness_subscriber(self.ks, on_liveliness_change)

    def tag_binds(self, paths: list[str]) -> list[TagBind]:
        return [self.tag_bind(path) for path in paths]

    def tag_bind(self, path: str, value: Any = None) -> TagBind:
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        tag = self.tags[path]
        bind = TagBind(self.ks, self._comm, tag, value, self.write_tag)
        return bind
    
    def subnode(self, name: str) -> RemoteSubConnection:
        from gedge.node.subnode import RemoteSubConnection
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
            from gedge.node.subnode import SubnodeConfig
            assert isinstance(curr_node, SubnodeConfig)
            r = RemoteSubConnection(RemoteConfig(name), curr_node.ks, curr_node, self._comm, self.node_id, on_close)
            return r

        if name not in self.subnodes:
            raise ValueError(f"No subnode {name}") 
        curr_node = self.subnodes[name]
        logger.debug(self._comm.session.is_closed())
        r = RemoteSubConnection(RemoteConfig(name), curr_node.ks, curr_node, self._comm, self.node_id, on_close)
        return r

    def _write_tag(self, path: str, value: Any) -> TagWriteReply:
        logger.info(f"Remote node '{self.key}' received write request at path '{path}' with value '{value}'")
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        tag = self.tags[path]
        response = self._comm.write_tag(self.ks, tag.path, TagData.py_to_proto(value, tag.type))
        code, error = response.code, response.error

        '''
        Bit of a design decision here. The issue is that golden-edge reserved codes do not have 
        any props, so we would get an error here. So, if the error field is not empty, we 
        can assume that something went wrong and the user should only be looking at 
        'code' and 'error' rather than props, because they are sorta in 'undefined behavior'.
        For well-defined errors (i.e. 401: project already running), the user should 
        define these in the meta and have the requisite props.
        '''
        props = {}    
        if not error:
            r = [r for r in self.tags[path].responses if r.code == code] 
            props = r[0].props.to_value()

        reply = TagWriteReply(self.ks.tag_write_path(path), code, error, value, props)
        return reply

    def write_tag(self, path: str, value: Any) -> TagWriteReply:
        return self._write_tag(path, value)

    async def write_tag_async(self, path: str, value: Any) -> TagWriteReply:
        return self._write_tag(path, value)
    
    # TODO: (key, value) vs {key: value}. Currently, we use the tuple for (name, type) and the dict for {name: value}
    def call_method(self, path: str, on_reply: MethodReplyCallback, **kwargs) -> None:
        # TODO: this setup may limit the user if they want to have a parameter "path" passed into 
        # their method because it conflicts with this function's arguments, but honestly we could just mangle our keyword args to be something like __path_ and _timeout__

        if path not in self.methods:
            raise MethodLookupError(path, self.ks.name)
        
        # TODO: should this be a queryable with selectors? 
        # TODO: should this be in comm?
        method_query_id = str(uuid.uuid4())
        method = self.methods[path]
        params: dict[str, proto.TagData] = {}
        for key, value in kwargs.items():
            data_type = method.params[key].type
            params[key] = TagData.py_to_proto(value, data_type)

        # TODO: we need a subscriber for /** and for /caller_id/method_query_id
        logger.info(f"Querying method of node {self.ks.name} at path {path} with params {params.keys()}")
        self._comm.query_method(self.ks, path, self.node_id, method_query_id, params, on_reply, self.methods[path])
    
    def call_method_iter(self, path: str, timeout: float | None = None, **kwargs) -> Iterator[MethodReply]:
        # appparently, Generator[Reply, None, None] == Iterator[Reply]?
        # TODO: we can probably merge this with call_method eventually
        if path not in self.methods:
            raise MethodLookupError(path, self.ks.name)

        method = self.methods[path]
        for param in method.params:
            if param not in kwargs:
                raise LookupError(f"Parameter {param} defined in config but not included in method call for method {method.path}")
        
        method_query_id = str(uuid.uuid4())
        params: dict[str, proto.TagData] = {}
        for key, value in kwargs.items():
            data_type = method.params[key].type
            params[key] = TagData.py_to_proto(value, data_type)
        
        replies: Queue[MethodReply] = Queue()
        def _on_reply(reply: MethodReply) -> None:
            replies.put(reply)

        logger.info(f"Querying method of node {self.ks.name} at path {path} with params {params.keys()}")
        # TODO: this function definition is longggggg, so many arguments
        start = time.time()
        self._comm.query_method(self.ks, path, self.node_id, method_query_id, params, _on_reply, self.methods[path])
        while True:
            try:
                elapsed = time.time() - start
                res = replies.get(block=True, timeout=max(0, (timeout - elapsed)) if timeout else None)
            except Empty:
                key_expr = self.ks.method_response(path, self.node_id, method_query_id)
                self._comm.cancel_subscription(key_expr)
                raise TimeoutError(f"Timeout of method call at path {method.path} exceeded")
            # Design decision: we don't give a codes.DONE to the iterator that the user uses
            # However, we do give them method and tag errors because they could be useful
            if res.code == codes.DONE:
                return
            yield res
            if res.code in {codes.METHOD_ERROR, codes.TAG_ERROR}:
                return
