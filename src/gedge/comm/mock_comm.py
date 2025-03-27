from __future__ import annotations

from ast import Call
import base64
from collections import defaultdict
from dataclasses import dataclass
import zenoh
import json
from gedge.comm.comm import Comm
from gedge.node import codes
from gedge.node.body import BodyData
from gedge.node.error import NodeLookupError
from gedge import proto
from gedge.comm import keys
from gedge.comm.keys import NodeKeySpace, method_response_from_call

from typing import Any, TYPE_CHECKING, Callable

from gedge.node.gtypes import MethodHandler, MethodReplyCallback, TagValue, ZenohQueryCallback
from gedge.node.method import Method
from gedge.node.method_reply import MethodReply
from gedge.node.method_response import MethodResponse
from gedge.node.param import params_proto_to_py
from gedge.node.prop import Props
from gedge.node.query import MethodQuery
from gedge.node.tag import Tag, WriteResponse
from gedge.node.tag_data import TagData
from gedge.node.tag_write_query import TagWriteQuery
from gedge.node.tag_write_reply import TagWriteReply
import threading
if TYPE_CHECKING:
    from gedge.node.gtypes import ZenohCallback, ZenohQueryCallback, ZenohReplyCallback

ProtoMessage = proto.Meta | proto.TagData | proto.WriteResponseData | proto.State | proto.MethodQueryData | proto.ResponseData | proto.WriteResponseData | proto.ResponseData

import logging
logger = logging.getLogger(__name__)

TAG_WRITE = [TagWriteQuery, TagWriteReply]
METHOD_CALL = [MethodQuery, MethodReply]

@dataclass
class MockSample:
    key_expr: str
    value: ProtoMessage

MockCallback = Callable[[MockSample], None]

'''
It would be maybe nice to subclass from zenoh.Subscriber, but it is marked as 
final so we cannot do that. Need to find another workaround
'''

# TODO: handle Zenoh queries
class MockComm(Comm):
    def __init__(self):
        # just maps key expressions to functions
        self.subscribers: dict[str, list[MockCallback]] = defaultdict(list)
        self.active_methods: dict[str, MethodReplyCallback] = dict()
        self.metas: dict[str, proto.Meta] = dict()

    def __enter__(self):
        logger.info(f"Mock connection")
        return self
    
    def __exit__(self, *exc):
        logger.info(f"Closing mock connection")

    def _send_proto(self, key_expr: str, value: ProtoMessage):
        for key in self.subscribers:
            if keys.overlap(key, key_expr):
                for handler in self.subscribers[key]:
                    thread = threading.Thread(target=handler, args=[MockSample(key_expr, value)])
                    thread.start()

    def _subscriber(self, key_expr: str, handler: MockCallback):
        self.subscribers[key_expr].append(handler)
    
    # TODO: combine this function with comm
    def _on_method_reply(self, on_reply: MethodReplyCallback, method: Method) -> MockCallback:
        responses = {r.code: r for r in method.responses}
        def _on_reply(reply: MockSample) -> None:
            assert type(reply.value) == proto.ResponseData
            code, body, error = reply.value.code, reply.value.body, reply.value.error
            if code not in {codes.DONE, codes.METHOD_ERROR, codes.TAG_ERROR}:
                response = responses[code]
            else:
                response = MethodResponse(code, Props.empty(), {})
            new_body: dict[str, BodyData] = {}
            for key, value in body.items():
                data_type = response.body[key].type
                props = response.body[key].props
                new_body[key] = BodyData(TagData.proto_to_py(value, data_type), props.to_value())
            props = response.props.to_value()
            r = MethodReply(reply.key_expr, code, new_body, error, props)
            on_reply(r)
        return _on_reply
    
    # TODO: combine this function with comm
    def _tag_write_reply(self, query: zenoh.Query) -> Callable[[int, str], None]:
        def _reply(code: int, error: str = ""):
            write_response = proto.WriteResponseData(code=code, error=error)
            b = self.serialize(write_response)
            query.reply(key_expr=str(query.key_expr), payload=b)
        return _reply

    # TODO: combine this function with comm
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
    
    # TODO: combine this function with comm
    def _method_reply(self, key_expr: str, method: Method):
        responses = method.responses
        def _reply(code: int, body: dict[str, TagValue] = {}, error: str = "") -> None:
            logger.info(f"Replying to method with code {code} on path {NodeKeySpace.method_path_from_response_key(key_expr)}")
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
        def _on_query(sample: MockSample) -> None:
            assert type(sample.value) == proto.MethodQueryData
            self._handle_method_query(method, sample.key_expr, sample.value)
        return _on_query
    
    # TODO: combine with comm
    def method_queryable(self, ks: NodeKeySpace, method: Method) -> None:
        key_expr = ks.method_query_listen(method.path)
        logger.info(f"Setting up method at path: {method.path} on node {ks.name}")
        handler = self._on_method_query(method)
        self._subscriber(key_expr, handler)
    
    # TODO: combine with comm
    def tag_queryable(self, ks: NodeKeySpace, tag: Tag) -> None:
        key_expr = ks.tag_write_path(tag.path)
        zenoh_handler = self._on_tag_write(tag)
        self._queryable(key_expr, zenoh_handler)
    
    def _queryable(self, key_expr: str, handler: Callable[[zenoh.Query], None]) -> None:
        # TODO: how will MockComm handle queries
        pass
    
    def pull_meta_message(self, ks: NodeKeySpace) -> proto.Meta:
        return self.metas[ks.user_key]

    def send_meta(self, ks: NodeKeySpace, meta: proto.Meta):
        self.metas[ks.user_key] = meta
    
    def send_state(self, ks: NodeKeySpace, state: proto.State):
        # maybe MockComm will implement state at some point
        pass
    
    def liveliness_token(self, ks: NodeKeySpace) -> None:
        # MockComm doesn't worry about this for now
        pass