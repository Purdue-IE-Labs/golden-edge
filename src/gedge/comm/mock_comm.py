from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import zenoh
from gedge.comm.comm import Comm
from gedge import proto
from gedge.comm import keys
from gedge.comm.keys import NodeKeySpace

from typing import Any, TYPE_CHECKING, Callable

from gedge.node import codes
from gedge.node.gtypes import MethodHandler, MethodReplyCallback, TagBaseValue, TagValue, ZenohQueryCallback
from gedge.node.method import MethodConfig
from gedge.py_proto.data_model import DataItem
from gedge.node.query import TagWriteQuery
import threading

from gedge.py_proto.tag_config import Tag, TagConfig, ResponseConfig
if TYPE_CHECKING:
    from gedge.node.gtypes import ZenohCallback, ZenohQueryCallback, ZenohReplyCallback

ProtoMessage = proto.Meta | proto.DataItem | proto.Response | proto.State | proto.MethodCall

import logging
logger = logging.getLogger(__name__)

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
# for now, we will not worry about Zenoh queries, because we 
# may be removing them from Comm soon, anyway, due to timeout issues
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
    
    def cancel_subscription(self, key_expr: str):
        self.subscribers[key_expr] = []
    
    def _on_method_reply(self, on_reply: MethodReplyCallback, method: MethodConfig) -> MockCallback:
        def _on_reply(reply: MockSample) -> None:
            assert type(reply.value) == proto.Response
            self._handle_on_method_reply(method, reply.key_expr, reply.value, on_reply)
        return _on_reply
    
    def _method_reply(self, key_expr: str, method: MethodConfig):
        return super()._method_reply(key_expr, method)
    
    def _on_method_query(self, method: MethodConfig):
        def _on_query(sample: MockSample) -> None:
            assert type(sample.value) == proto.MethodCall
            self._handle_method_query(method, sample.key_expr, sample.value)
        return _on_query
    
    def method_queryable(self, ks: NodeKeySpace, method: MethodConfig) -> None:
        super().method_queryable(ks, method)
    
    def pull_meta_message(self, ks: NodeKeySpace) -> proto.Meta:
        return self.metas[ks.user_key]

    def send_meta(self, ks: NodeKeySpace, meta: proto.Meta):
        self.metas[ks.user_key] = meta
    
    def send_state(self, ks: NodeKeySpace, state: proto.State):
        # maybe MockComm will implement state at some point
        pass
    
    def liveliness_token(self, ks: NodeKeySpace) -> None:
        # MockComm doesn't worry about this for now, but we need to override Comm
        pass