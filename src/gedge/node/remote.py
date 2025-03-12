from __future__ import annotations

from gedge.node.body import Body, BodyData
from gedge.node.gtypes import MethodReplyCallback
from gedge.node.prop import Props
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
import zenoh
import uuid


from typing import Any, Iterator, Callable, TYPE_CHECKING

from gedge.node.tag_write_reply import TagWriteReply
if TYPE_CHECKING:
    from gedge.node.gtypes import TagDataCallback, ZenohCallback, StateCallback, MetaCallback, LivelinessCallback 

import logging
logger = logging.getLogger(__name__)

class RemoteConfig:
    def __init__(self, key: str, read_tags: list[str] = [], read_write_tags: list[str] = [], method_calls: list[str] = []):
        self.key = key
        self.read_tags = read_tags
        self.read_write_tags = read_write_tags
        self.method_calls = method_calls

class RemoteConnection:
    def __init__(self, config: RemoteConfig, comm: Comm, node_id: str, on_close: Callable[[str], None] | None = None):
        self.config = config
        self._comm = comm 
        self._subscriptions: list[zenoh.Subscriber] = []
        self.key = self.config.key
        self.ks = NodeKeySpace.from_user_key(self.key)
        self.on_close = on_close

        self.node_id = node_id

        '''
        TODO: perhaps we should subscribe to this node's meta message, in which case all the following utility variables (self.tags, self.methods, self.responses) 
        would need to react to that (i.e. be properties)
        '''
        self.meta = self._comm.pull_meta_message(self.ks)
        tags: list[Tag] = [Tag.from_proto(t) for t in self.meta.tags]
        self.tags = {t.path: t for t in tags}
        methods: list[Method] = [Method.from_proto(m) for m in self.meta.methods]
        self.methods = {m.path: m for m in methods}
        self.responses: dict[str, dict[int, MethodResponse]] = {key:{r.code:r for r in value.responses} for key, value in self.methods.items()}

    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        self.close()
        self._comm.__exit__(*exc)

    def _on_tag_data(self, on_tag_data: TagDataCallback) -> ZenohCallback:
        def _on_tag_data(sample: zenoh.Sample):
            tag_data: proto.TagData = self._comm.deserialize(proto.TagData(), sample.payload.to_bytes())
            path: str = NodeKeySpace.tag_path_from_key(str(sample.key_expr))
            if path not in self.tags:
                node: str = NodeKeySpace.name_from_key(str(sample.key_expr))
                raise TagLookupError(path, node)
            tag_config = self.tags[path]
            value = TagData.proto_to_py(tag_data, tag_config.type)
            logger.info(f"Remote node {self.key} updating tag {path} with value {value}")
            on_tag_data(str(sample.key_expr), value)
        return _on_tag_data

    def _on_state(self, on_state: StateCallback) -> ZenohCallback:
        def _on_state(sample: zenoh.Sample):
            state: proto.State = self._comm.deserialize(proto.State(), sample.payload.to_bytes())
            logger.info(f"Remote node {self.key} publishing state message")
            on_state(str(sample.key_expr), state)
        return _on_state

    def _on_meta(self, on_meta: MetaCallback) -> ZenohCallback:
        def _on_meta(sample: zenoh.Sample):
            meta: proto.Meta = self._comm.deserialize(proto.Meta(), sample.payload.to_bytes())
            logger.info(f"Remote node {self.key} publishing meta message")
            on_meta(str(sample.key_expr), meta)
        return _on_meta
    
    def _on_liveliness(self, on_liveliness_change: LivelinessCallback) -> ZenohCallback:
        def _on_liveliness(sample: zenoh.Sample):
            is_online = sample.kind == zenoh.SampleKind.PUT
            online = "online" if is_online else "offline"
            logger.info(f"Liveliness of remote node {self.key} changed: {online}")
            on_liveliness_change(str(sample.key_expr), is_online)
        return _on_liveliness

    def close(self):
        for sub in self._subscriptions:
            sub.undeclare()        
        if self.on_close is not None:
            self.on_close(self.key)
    
    def add_tag_data_callback(self, path: str, on_tag_data: TagDataCallback) -> None:
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)

        self.config.read_write_tags.append(path)
        _on_tag_data = self._on_tag_data(on_tag_data)
        subscriber = self._comm.tag_data_subscriber(self.ks, path, _on_tag_data)
        self._subscriptions.append(subscriber)

    def add_state_callback(self, on_state: StateCallback) -> None:
        _on_state = self._on_state(on_state)
        subscriber = self._comm.state_subscriber(self.ks, _on_state)
        self._subscriptions.append(subscriber)

    def add_meta_callback(self, on_meta: MetaCallback) -> None:
        _on_meta = self._on_meta(on_meta)
        subscriber = self._comm.meta_subscriber(self.ks, _on_meta)
        self._subscriptions.append(subscriber)

    def add_liveliness_callback(self, on_liveliness_change: LivelinessCallback) -> None:
        _on_liveliness = self._on_liveliness(on_liveliness_change)
        subscriber = self._comm.liveliness_subscriber(self.ks, _on_liveliness)
        self._subscriptions.append(subscriber)

    def tag_binds(self, paths: list[str]) -> list[TagBind]:
        return [self.tag_bind(path) for path in paths]

    def tag_bind(self, path: str, value: Any = None) -> TagBind:
        if path not in self.tags:
            raise TagLookupError(path, self.ks.name)
        tag = self.tags[path]
        bind = TagBind(self.ks, self._comm, tag, value, self.write_tag)
        return bind

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
    
    def _on_reply(self, path: str, on_reply: MethodReplyCallback) -> ZenohCallback:
        def _on_reply(sample: zenoh.Sample) -> None:
            if not sample:
                print("warning: reply super not ok")
                return
            r: proto.ResponseData = self._comm.deserialize(proto.ResponseData(), sample.payload.to_bytes())

            '''
            Design decision here. The problem is that golden-edge reserved codes do not have a 
            config backing (we could add one if we wanted), so we have to create a config on 
            the fly to give back to the user for them to look at. For now, it's empty. At config 
            initialization, we could (and maybe should) inject these. But then if the users 
            goes len(responses) they may be confused to find that we have added some without 
            there permission. Or maybe we just never show the user any of these. But also 
            they need to see the error ones to know that something went terribly wrong.
            '''
            if r.code in {codes.DONE, codes.METHOD_ERROR}:
                response: MethodResponse = MethodResponse(r.code, Props.empty(), {})
            else:
                response: MethodResponse = self.responses[path][r.code]
            body: dict[str, BodyData] = {}
            for key, value in r.body.items():
                data_type = response.body[key].type
                props = response.body[key].props
                body[key] = BodyData(TagData.proto_to_py(value, data_type), props.to_value())
            # method_config = self.methods[path] 
            props = response.props.to_value()
            reply = MethodReply(str(sample.key_expr), r.code, body, r.error, props)
            on_reply(reply)
            if r.code in {codes.DONE, codes.METHOD_ERROR}:
                # remove subscription after we are done
                logger.debug(f"remove subscription for key expr {sample.key_expr}")
                self._subscriptions.remove([x for x in self._subscriptions if x.key_expr == sample.key_expr][0])
        return _on_reply
    
    # TODO: (key, value) vs {key: value}. Currently, we use the tuple for (name, type) and the dict for {name: value}
    def call_method(self, path: str, on_reply: MethodReplyCallback, **kwargs) -> None:
        # TODO: this setup may limit the user if they want to have a parameter "path" passed into 
        # their method because it conflicts with this function's arguments

        if path not in self.methods:
            raise MethodLookupError(path, self.ks.name)
        
        # TODO: should this be a queryable with selectors? 
        method_query_id = str(uuid.uuid4())
        method = self.methods[path]
        params: dict[str, proto.TagData] = {}
        for key, value in kwargs.items():
            data_type = method.params[key].type
            params[key] = TagData.py_to_proto(value, data_type)

        on_reply_: ZenohCallback = self._on_reply(path, on_reply)
        # TODO: we need a subscriber for /** and for /caller_id/method_query_id
        # subscriber = self._comm.method_queryable_v2(self.ks, path, caller_id, method_query_id, on_reply)
        # self._subscriptions.append(subscriber)
        logger.info(f"Querying method of node {self.ks.name} at path {path} with params {params.keys()}")
        key_expr = self.ks.method_response(path, self.node_id, method_query_id)
        self._subscriptions.append(self._comm._subscriber(key_expr, on_reply_))
        self._comm.query_method(self.ks, path, self.node_id, method_query_id, params)
    
    def call_method_iter(self, path: str, timeout: int | None = None, **kwargs) -> Iterator[MethodReply]:
        # appparently, Generator[Reply, None, None] == Iterator[Reply]?
        # TODO: we can probably merge this with call_method eventually, but honestly we could just mangle our keyword args to be something like __path_ and _timeout__
        if path not in self.methods:
            raise MethodLookupError(path, self.ks.name)
        
        from queue import Queue, Empty
        
        method_query_id = str(uuid.uuid4())
        method = self.methods[path]
        params: dict[str, proto.TagData] = {}
        for key, value in kwargs.items():
            data_type = method.params[key].type
            params[key] = TagData.py_to_proto(value, data_type)
        
        replies: Queue[MethodReply] = Queue()
        def _on_reply(reply: MethodReply) -> None:
            replies.put(reply)

        logger.info(f"Querying method of node {self.ks.name} at path {path} with params {params.keys()}")
        key_expr = self.ks.method_response(path, self.node_id, method_query_id)
        self._subscriptions.append(self._comm._subscriber(key_expr, self._on_reply(path, _on_reply)))
        self._comm.query_method(self.ks, path, self.node_id, method_query_id, params)
        while True:
            try:
                res = replies.get(block=True, timeout=timeout)
            except Empty:
                logger.error(f"Timeout exceeded")
                return
            # Design decision: we don't give a codes.DONE to the iterator that the user uses
            # However, we do give them method and tag errors because they could be useful
            if res.code == codes.DONE:
                return
            yield res
            if res.code in {codes.METHOD_ERROR, codes.TAG_ERROR}:
                return

