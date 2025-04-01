from __future__ import annotations

from ast import Call
import base64
from dataclasses import dataclass
from multiprocessing import Value
import zenoh
import json
from gedge.node import codes
from gedge.node.body import BodyData
from gedge.node.error import NodeLookupError, TagLookupError
from gedge import proto
from gedge.comm import keys
from gedge.comm.keys import NodeKeySpace, internal_to_user_key, method_response_from_call

from typing import Any, TYPE_CHECKING, Callable

from gedge.node.gtypes import LivelinessCallback, MetaCallback, MethodHandler, MethodReplyCallback, StateCallback, TagDataCallback, TagValue, TagWriteHandler
from gedge.node.method import Method
from gedge.node.method_reply import MethodReply
from gedge.node.method_response import MethodResponse
from gedge.node.param import params_proto_to_py
from gedge.node.prop import Props
from gedge.node.query import MethodQuery
from gedge.node.tag import Tag, WriteResponse
from gedge.node.tag_data import TagData
from gedge.node.tag_write_query import TagWriteQuery
if TYPE_CHECKING:
    from gedge.node.gtypes import ZenohCallback, ZenohQueryCallback, ZenohReplyCallback

ProtoMessage = proto.Meta | proto.TagData | proto.WriteResponseData | proto.State | proto.MethodQueryData | proto.ResponseData | proto.WriteResponseData

import logging
logger = logging.getLogger(__name__)

# handle Zenoh communications
# The user will not interact with this item
# TODO: should this hold a key_space? and allow for a context manager when we want to change it
class Comm:
    def __init__(self, connections: list[str]):
        config = json.dumps({
            "mode": "client",
            "connect": {
                "endpoints": connections
            }
        })
        self.config = config
        self.connections = connections
        self.subscriptions: list[zenoh.Subscriber] = []
    
    def connect(self):
        self.__enter__()
    
    def close(self):
        self.__exit__()

    def __enter__(self):
        logger.debug(f"Attemping to connect to: {self.connections}")
        config = zenoh.Config.from_json5(self.config)
        session = zenoh.open(config)
        logger.info(f"Connected to one of: {self.connections}")
        self.session = session
        return self
    
    def __exit__(self, *exc):
        self.session.close()
    
    def close_remote(self, ks: NodeKeySpace):
        logger.info(f"Closing remote connection to {ks.user_key}")
        subscriptions = [s for s in self.subscriptions if ks.contains(str(s.key_expr))]
        for s in subscriptions:
            s.undeclare()

    def serialize(self, proto: ProtoMessage) -> bytes:
        b = proto.SerializeToString()
        # TODO: base64 is needed due to errors with carriage returns in influxdb
        # which we should try to address in a better way than this
        b = base64.b64encode(b)
        return b
    
    def deserialize(self, proto: ProtoMessage, payload: bytes) -> Any:
        b = base64.b64decode(payload)
        proto.ParseFromString(b)
        return proto

    def _send_proto(self, key_expr: str, value: ProtoMessage):
        logger.debug(f"putting proto on key_expr '{key_expr}'")
        b = self.serialize(value)
        self.session.put(key_expr, b, encoding="application/protobuf")
    
    def liveliness_token(self, ks: NodeKeySpace) -> zenoh.LivelinessToken:
        key_expr = ks.liveliness_key_prefix
        return self.session.liveliness().declare_token(key_expr)

    def _on_liveliness(self, on_liveliness_change: LivelinessCallback) -> ZenohCallback:
        def _on_liveliness(sample: zenoh.Sample):
            is_online = sample.kind == zenoh.SampleKind.PUT
            online = "online" if is_online else "offline"
            
            ks = NodeKeySpace.from_internal_key(str(sample.key_expr))
            logger.info(f"Liveliness of remote node {ks.user_key} changed: {online}")
            on_liveliness_change(str(sample.key_expr), is_online)
        return _on_liveliness

    def _on_tag_data(self, on_tag_data: TagDataCallback, tags: dict[str, Tag]) -> ZenohCallback:
        def _on_tag_data(sample: zenoh.Sample):
            tag_data: proto.TagData = self.deserialize(proto.TagData(), sample.payload.to_bytes())
            logger.debug(f"Sample received on key expression {str(sample.key_expr)}, value = {tag_data}")
            path: str = NodeKeySpace.tag_path_from_key(str(sample.key_expr))
            if path not in tags:
                node: str = NodeKeySpace.name_from_key(str(sample.key_expr))
                raise TagLookupError(path, node)
            tag_config = tags[path]
            value = TagData.proto_to_py(tag_data, tag_config.type)
            logger.debug(f"Remote node {internal_to_user_key(str(sample.key_expr))} received value {value} for tag {path}")
            on_tag_data(str(sample.key_expr), value)
        return _on_tag_data

    def _on_state(self, on_state: StateCallback) -> ZenohCallback:
        def _on_state(sample: zenoh.Sample):
            state: proto.State = self.deserialize(proto.State(), sample.payload.to_bytes())
            logger.debug(f"Remote node {internal_to_user_key(str(sample.key_expr))} received state message: online = {state.online}")
            on_state(str(sample.key_expr), state)
        return _on_state

    def _on_meta(self, on_meta: MetaCallback) -> ZenohCallback:
        def _on_meta(sample: zenoh.Sample):
            meta: proto.Meta = self.deserialize(proto.Meta(), sample.payload.to_bytes())
            logger.debug(f"Remote node {internal_to_user_key(str(sample.key_expr))} received meta message")
            on_meta(str(sample.key_expr), meta)
        return _on_meta

    def _on_method_reply(self, on_reply: MethodReplyCallback, method: Method) -> ZenohCallback:
        def _on_reply(sample: zenoh.Sample) -> None:
            if not sample:
                logger.warning(f"reply from method failed")
                return
            r: proto.ResponseData = self.deserialize(proto.ResponseData(), sample.payload.to_bytes())
            self._handle_on_method_reply(method, str(sample.key_expr), r, on_reply)
        return _on_reply
    
    def _handle_on_method_reply(self, method: Method, key_expr: str, r: proto.ResponseData, on_reply: MethodReplyCallback) -> None:
        responses = {r.code: r for r in method.responses}
        '''
        Design decision here. The problem is that golden-edge reserved codes do not have a 
        config backing (we could add one if we wanted), so we have to create a config on 
        the fly to give back to the user for them to look at. For now, it's empty. At config 
        initialization, we could (and maybe should) inject these. But then if the users 
        goes len(responses) they may be confused to find that we have added some without 
        there permission. Or maybe we just never show the user any of these. But also 
        they need to see the error ones to know that something went terribly wrong.
        '''
        logger.info(f"Received reply from method at path '{method.path}' with code {r.code}")
        if r.code in {codes.DONE, codes.METHOD_ERROR}:
            response: MethodResponse = MethodResponse(r.code, Props.empty(), {})
        else:
            response: MethodResponse = responses[r.code]
        body: dict[str, BodyData] = {}
        for key, value in r.body.items():
            data_type = response.body[key].type
            props = response.body[key].props
            body[key] = BodyData(TagData.proto_to_py(value, data_type), props.to_value())
        props = response.props.to_value()
        reply = MethodReply(key_expr, r.code, body, r.error, props)
        on_reply(reply)
        if r.code in {codes.DONE, codes.METHOD_ERROR}:
            # TODO: we need to unsubcribe here because we are closing this method connection, does this mean we should move comm connections
            # to this function
            logger.debug(f"remove subscription for key expr {key_expr}")
            self.cancel_subscription(key_expr)
    
    def _tag_write_reply(self, query: zenoh.Query) -> Callable[[int, str], None]:
        def _reply(code: int, error: str = ""):
            write_response = proto.WriteResponseData(code=code, error=error)
            b = self.serialize(write_response)
            query.reply(key_expr=str(query.key_expr), payload=b)
        return _reply

    def _on_tag_write(self, tag: Tag) -> ZenohQueryCallback:
        def _on_write(query: zenoh.Query) -> None:
            reply = self._tag_write_reply(query)
            try:
                if not query.payload:
                    raise ValueError(f"Empty write request")
                proto_data = self.deserialize(proto.TagData(), query.payload.to_bytes())
                data: TagValue = TagData.proto_to_py(proto_data, tag.type)
                logger.info(f"Node {query.key_expr} received tag write at path '{tag.path}' with value '{data}'")

                t = TagWriteQuery(str(query.key_expr), data, tag, reply)
                assert tag.write_handler is not None
                tag.write_handler(t)
                
                try:
                    code = t.code
                    error = t.error
                except:
                    raise ValueError(f"Tag write handler must call 'reply(...)' at some point")

                write_responses: dict[int, WriteResponse] = {r.code:r for r in tag.responses}
                if code not in write_responses:
                    raise LookupError(f"Tag write handler for tag {tag.path} given incorrect code {code} not found in callback config")

                response = [code, error]
            except Exception as e:
                logger.warning(f"Sending tag write response on path {tag.path}: error={repr(e)}")
                response = [code, error]
            finally:
                reply(*response)
        return _on_write
    
    def _method_reply(self, key_expr: str, method: Method) -> Callable[[int, dict[str, TagValue], str], None]:
        responses = method.responses
        def _reply(code: int, body: dict[str, TagValue] = {}, error: str = "") -> None:
            if code not in {i.code for i in responses} and code not in {codes.DONE, codes.METHOD_ERROR, codes.TAG_ERROR}:
                raise ValueError(f"invalid repsonse code {code}")
            new_body: dict[str, proto.TagData] = {}
            for key, value in body.items():
                response = [i for i in responses if i.code == code][0]
                data_type = response.body[key].type
                new_body[key] = TagData.py_to_proto(value, data_type)
            r = proto.ResponseData(code=code, body=new_body, error=error)
            self._send_proto(key_expr=key_expr, value=r)
        return _reply
    
    def _on_method_query(self, method: Method):
        def _on_query(sample: zenoh.Sample) -> None:
            m = self.deserialize(proto.MethodQueryData(), sample.payload.to_bytes())
            self._handle_method_query(method, str(sample.key_expr), m)
        return _on_query

    def _handle_method_query(self, method: Method, key_expr: str, value: proto.MethodQueryData):
        params: dict[str, Any] = params_proto_to_py(dict(value.params), method.params)
        
        key_expr = method_response_from_call(key_expr)
        reply = self._method_reply(key_expr, method)
        q = MethodQuery(key_expr, params, reply, method.responses)
        try:
            name = NodeKeySpace.user_key_from_key(key_expr)
            logger.info(f"Node {name} method call at path '{method.path}' with params {params}")
            logger.debug(f"Received from {key_expr}")
            assert method.handler is not None, "No method handler provided"
            method.handler(q)
            code = codes.DONE
            error = ""
        except Exception as e:
            code = codes.METHOD_ERROR
            error = repr(e)
        finally:
            reply(code, {}, error)

    def liveliness_subscriber(self, ks: NodeKeySpace, handler: LivelinessCallback) -> None:
        key_expr = ks.liveliness_key_prefix
        zenoh_handler = self._on_liveliness(handler)
        subscriber = self.session.liveliness().declare_subscriber(key_expr, zenoh_handler)
        self.subscriptions.append(subscriber)

    def _query_liveliness(self, ks: NodeKeySpace) -> zenoh.Reply:
        key_expr = ks.liveliness_key_prefix
        return self.session.liveliness().get(key_expr).recv()

    def _subscriber(self, key_expr: str, handler: ZenohCallback) -> None:
        logger.debug(f"declaring subscriber on key expression '{key_expr}'")
        subscriber = self.session.declare_subscriber(key_expr, handler)
        self.subscriptions.append(subscriber)

    def cancel_subscription(self, key_expr: str):
        subs = [s for s in self.subscriptions if str(s.key_expr) == key_expr]
        logger.debug(f"canceling {len(subs)} subscriptions at key_expr = {key_expr}")
        for s in subs:
            s.undeclare()
            self.subscriptions.remove(s)
    
    def _queryable(self, key_expr: str, handler: ZenohQueryCallback) -> zenoh.Queryable:
        logger.debug(f"declaring queryable on key_expr = {key_expr}")
        return self.session.declare_queryable(key_expr, handler)
    
    def _query_sync(self, key_expr: str, payload: bytes) -> zenoh.Reply:
        try:
            reply = self.session.get(key_expr, payload=payload).recv()
        except Exception:
            raise LookupError(f"No queryable defined at {key_expr}")
        return reply
    
    def meta_subscriber(self, ks: NodeKeySpace, handler: MetaCallback) -> None:
        key_expr = ks.meta_key_prefix
        zenoh_handler = self._on_meta(handler)
        self._subscriber(key_expr, zenoh_handler)
    
    def state_subscriber(self, ks: NodeKeySpace, handler: StateCallback) -> None:
        key_expr = ks.state_key_prefix
        zenoh_handler = self._on_state(handler)
        self._subscriber(key_expr, zenoh_handler)
    
    def tag_data_subscriber(self, ks: NodeKeySpace, path: str, handler: TagDataCallback, tags: dict[str, Tag]) -> None:
        key_expr = ks.tag_data_path(path)
        zenoh_handler = self._on_tag_data(handler, tags)
        self._subscriber(key_expr, zenoh_handler)

    def tag_queryable(self, ks: NodeKeySpace, tag: Tag) -> zenoh.Queryable:
        key_expr = ks.tag_write_path(tag.path)
        zenoh_handler = self._on_tag_write(tag)
        logger.debug(f"tag queryable on {key_expr}")
        return self._queryable(key_expr, zenoh_handler)
    
    def query_tag(self, ks: NodeKeySpace, path: str, value: proto.TagData) -> zenoh.Reply:
        b = self.serialize(value)
        logger.debug(f"querying tag at path {ks.tag_write_path(path)}")
        return self._query_sync(ks.tag_write_path(path), payload=b)
    
    def method_queryable(self, ks: NodeKeySpace, method: Method) -> None:
        key_expr = ks.method_query_listen(method.path)
        logger.info(f"Setting up method at path {method.path} on node {ks.name}")
        zenoh_handler = self._on_method_query(method)
        self._subscriber(key_expr, zenoh_handler)
    
    def query_method(self, ks: NodeKeySpace, path: str, caller_id: str, method_query_id: str, params: dict[str, proto.TagData], on_reply: MethodReplyCallback, method: Method) -> None:
        query_key_expr = ks.method_query(path, caller_id, method_query_id)
        query_data = proto.MethodQueryData(params=params)

        response_key_expr = ks.method_response(path, caller_id, method_query_id)
        zenoh_handler = self._on_method_reply(on_reply, method)
        self._subscriber(response_key_expr, zenoh_handler)
        self._send_proto(query_key_expr, query_data)

    def update_tag(self, ks: NodeKeySpace, path: str, value: proto.TagData):
        key_expr = ks.tag_data_path(path)
        self._send_proto(key_expr, value)

    def write_tag(self, ks: NodeKeySpace, path: str, value: proto.TagData) -> proto.WriteResponseData:
        reply = self.query_tag(ks, path, value)
        if reply.ok:
            d: proto.WriteResponseData = self.deserialize(proto.WriteResponseData(), reply.result.payload.to_bytes())
            return d
        else:
            # TODO: more granular exception?
            raise Exception(f"Failure in receiving tag write reply for tag at path {path}")

    def send_state(self, ks: NodeKeySpace, state: proto.State):
        key_expr = ks.state_key_prefix
        self._send_proto(key_expr, state)

    def send_meta(self, ks: NodeKeySpace, meta: proto.Meta):
        key_expr = ks.meta_key_prefix
        self._send_proto(key_expr, meta)
    
    def pull_meta_messages(self, only_online: bool = False):
        res = self.session.get(keys.key_join("**", keys.NODE, "*", keys.META))
        messages: list[proto.Meta] = []
        for r in res:
            r: zenoh.Reply
            if not r.ok:
                continue
            result = r.result

            try:
                meta: proto.Meta = self.deserialize(proto.Meta(), result.payload.to_bytes())
                ks = NodeKeySpace.from_user_key(meta.key)
                is_online = self.is_online(ks)
                if only_online and not is_online:
                    continue
                messages.append(meta)
            except Exception as e:
                raise ValueError(f"Could not deserialize meta from historian")
        return messages

    def pull_meta_message(self, ks: NodeKeySpace) -> proto.Meta:
        try:
            reply = self.session.get(ks.meta_key_prefix).recv()
        except:
            raise NodeLookupError(ks.user_key)
        if not reply.ok:
            raise NodeLookupError(ks.user_key)
        
        meta = self.deserialize(proto.Meta(), reply.result.payload.to_bytes())
        return meta
            
    def is_online(self, ks: NodeKeySpace) -> bool:
        try:
            reply = self._query_liveliness(ks)
            if not reply.ok:
                return False
            return reply.ok.kind == zenoh.SampleKind.PUT
        except:
            return False
