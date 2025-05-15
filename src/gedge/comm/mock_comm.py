from __future__ import annotations

from ast import Call
import base64
from collections import defaultdict
from dataclasses import dataclass
import zenoh
from zenoh import KeyExpr, Encoding, CongestionControl, Priority
import json
import base64
import gedge
from gedge.comm.comm import Comm
from gedge.node import codes
from gedge.node.body import BodyData
from gedge.node.error import NodeLookupError
from gedge import proto
from gedge.comm import keys
from gedge.comm.keys import NodeKeySpace, method_response_from_call
from gedge.proto import Meta

from typing import Any, TYPE_CHECKING, Callable, List, Optional, Union

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

if TYPE_CHECKING: # pragma: no cover
    from gedge.node.gtypes import ZenohCallback, ZenohQueryCallback, ZenohReplyCallback, TagWriteHandler
    

ProtoMessage = proto.Meta | proto.TagData | proto.WriteResponseData | proto.State | proto.MethodQueryData | proto.ResponseData | proto.WriteResponseData | proto.ResponseData

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


class MockLiveliness:
    def __init__(self, tokens: dict[str, Any]):
        # tokens maps key_expr strings to stored mock payloads
        self._tokens = tokens

    def get(
        self,
        selector: Union[KeyExpr, str],
        *,
        handler: Any = None,
        target: Any = None,
        consolidation: Any = None,
        timeout: Optional[float] = None,
        congestion_control: Optional[CongestionControl] = None,
        priority: Optional[Priority] = None,
        express: Optional[bool] = None,
        payload: Any = None,
        encoding: Any = None,
        attachment: Any = None
    ) -> "MockHandler":
        # Canonicalize selector
        key = selector if isinstance(selector, KeyExpr) else KeyExpr(selector)
        # Retrieve the mock payload (e.g., set up by connect_to_remote)
        mock_payload = self._tokens.get(str(key))
        return MockReply(mock_payload, None)
    
    def declare_subscriber(self, key_expr: str, handler: Callable):
        return MockSubscriber(key_expr, handler)

# Mock for zenoh.Reply, with 'ok' attribute
class MockReply:
    def __init__(self, ok: bool, result: MockResult):
        self.ok = ok
        self.result = result

class MockResult:
    def __init__(self, payload: bytes):
        self.payload = MockPayload(payload)

class MockPayload:
    def __init__(self, payload: bytes):
        self.payload = payload

    def to_bytes(self):
        # Simulate converting payload to bytes
        return self.payload

class MockSubscriber:
    def __init__(self, key_expr: KeyExpr, handler: Callable):
        self.key_expr: KeyExpr = key_expr
        self.handler: Callable = handler

    def undeclare(self):
        logger.info("Subscriber undeclared")

class MockSession:
    def __init__(self):
        self._storage = {}  # A simple dictionary to mimic key-value storage
        self._liveliness_tokens: dict[str, bool] = {}
        self._subscribers: dict[str, List[Callable]] = {}
        self.tag_write_handlers: dict[str, TagWriteHandler] = {}

    def put(self, 
            key_expr: Union[KeyExpr, str], 
            payload: Any, 
            *,
            encoding: Optional[Union[Encoding, str]] = None,
            congestion_control: Optional[CongestionControl] = None,
            priority: Optional[Priority] = None,
            express: Optional[bool] = None,
            attachment: Optional[Any] = None) -> None:
        
        
        # Mimic storing data in key-value format
        
        keyExpr = key_expr if isinstance(key_expr, KeyExpr) else KeyExpr(key_expr)

        self._storage[str(keyExpr)] = payload

        for sub_key, handlers in self._subscribers.items():
            if KeyExpr(sub_key).includes(keyExpr):
                for h in handlers:
                    h(  # emulate zenoh.Sample with minimal attributes
                        type('Sample', (), {
                            'key_expr': keyExpr,
                            'payload': payload,
                            'kind': None,
                            'timestamp': None
                        })()
                    )

        logger.info(f"Putting: {keyExpr} -> {payload}")

    def get(self, key_expr: Union[KeyExpr, str], payload: bytes =None) -> Any:
        logger.info(f"MockSession.get called with key: {key_expr}")
        lookupExpr = KeyExpr(key_expr)

        if payload is not None:
            logger.info("Payload present; invoking tag write handler")

            tag: Tag = self.get(key_expr)[0]


            if tag is None:
                raise LookupError(f"No tag for {key_expr}")

            if tag.write_handler is None:
                raise LookupError(f"No tag write handler for {key_expr}")

            # payload = b'CAk='
            decoded_payload = base64.b64decode(payload)
            value_passed = decoded_payload[1:]

            # Simulate decoding value from payload (adjust as needed)
            value = int.from_bytes(value_passed, byteorder="little")

            # Capture reply
            reply_data = {"code": int, "error": str}
            def reply_callback(code: int, error: str = ""):
                reply_data["code"] = code
                reply_data["error"] = error

            # Create the query object
            from gedge.node.tag_write_query import TagWriteQuery
            query = TagWriteQuery(
                key_expr=key_expr,
                value=value,
                tag_config=tag,
                _reply=reply_callback
            )

            # Call the handler
            tag.write_handler(query)

            if reply_data["code"] is None:
                raise RuntimeError("Handler did not call query.reply(...)")
            
            # print(reply_data["code"])

            response = proto.WriteResponseData(code=reply_data["code"], error=reply_data["error"])

            serialized = response.SerializeToString()

            encoded = base64.b64encode(serialized)

            # Return mock reply with response code as payload
            return (MockReply(True, MockResult(encoded)))

        replies: List[Any] = []
        for key, value in self._storage.items():
            compareExpr = KeyExpr(key)

            if lookupExpr.includes(compareExpr):
                replies.append(value)
        
        return replies

    def liveliness(self) -> MockLiveliness:
        """
        Return a mock Liveliness interface for liveliness queries.
        """
        return MockLiveliness(self._liveliness_tokens)
    
    def declare_subscriber(self, key_expr: Union[KeyExpr, str], handler: Callable[[Any], Any] = None) -> MockSubscriber:
        """
        Emulate Zenoh Session.declare_subscriber(key_expr, handler)
        """
        ke = key_expr if isinstance(key_expr, KeyExpr) else KeyExpr(key_expr)
        key_str = str(ke)

        # Register the handler
        self._subscribers.setdefault(key_str, []).append(handler)

        # Return a subscriber handle
        return MockSubscriber(ke, handler)

    def close(self):
        # Mimic closing the session
        logger.info("Closing session.")


# TODO: handle Zenoh queries
# for now, we will not worry about Zenoh queries, because we 
# may be removing them from Comm soon, anyway, due to timeout issues
class MockComm(Comm):
    def __init__(self):
        # just maps key expressions to functions
        self.subscribers: dict[str, list[MockCallback]] = defaultdict(list)
        self.active_methods: dict[str, MethodReplyCallback] = dict()
        self.metas: dict[str, proto.Meta] = dict()
        self.subscriptions: list[Any] = []
        
        self.session = MockSession()

    def __enter__(self):
        logger.info(f"Mock connection")
        return self

    def connect(self):
        self.__enter__()
    
    def __exit__(self, *exc):
        logger.info(f"Closing mock connection")

    def close_remote(self, ks: NodeKeySpace):
        logger.info(f"Mock Closing remote connection to {ks.user_key}")
        del self.metas[ks.user_key]
        # del self.session.storage[ks.user_key]

    def remove_remote_connection(self, ks: NodeKeySpace):
        del self.session._storage[ks.user_key]
        del self.metas[ks.user_key]

    def _query_liveliness(self, ks: NodeKeySpace) -> MockReply:
        '''
        Acquires the liveliness state as a reply of the passed node in the Zenoh session
        
        Arguments:
            ks (NodeKeySpace): The key space of the node being checked

        Returns:
            zenoh.Reply: The liveliness response from the Zenoh session
        '''
        return self.session.liveliness().get(ks.user_key)
    
    def _query_sync(self, key_expr: str, payload: bytes) -> zenoh.Reply:
        '''
        Sends the passed payload to the node corresponding to the passed key expression and returns the reply from Zenoh

        Arguments:
            key_expr (str): The key expression of the node the payload is being passed to
            payload (bytes): The payload being sent to the passed node

        Returns:
            zenoh.Reply
        '''
        try:
            reply = self.session.get(key_expr, payload=payload)
        except Exception:
            raise LookupError(f"No queryable defined at {key_expr}")
        return reply
    
    def is_online(self, ks: NodeKeySpace) -> bool:
        '''
        if (self.session.get(ks._user_key) != []):
            return True
        
        return False
        '''
        try:
            reply = self._query_liveliness(ks)
            if not reply.ok:
                return False
            return True
        except:
            return False

    def _send_proto(self, key_expr: str, value: ProtoMessage):
        '''
        Sends the passed ProtoMessage to the passed node

        Arguments:
            key_expr (str): The key expression of a node
            value (ProtoMessage): The value being passed to the node

        Returns:
            None
        '''
        logger.debug(f"putting proto on key_expr '{key_expr}'")
        b = self.serialize(value)

        self.session.put(key_expr, b, encoding="application/protobuf")
        # self.sequence_number.increment()
        
        for key in self.subscribers:
            if keys.overlap(key, key_expr):
                for handler in self.subscribers[key]:
                    thread = threading.Thread(target=handler, args=[MockSample(key_expr, value)])
                    thread.start()

    def _subscriber(self, key_expr: str, handler: MockCallback):
        self.subscribers[key_expr].append(handler)
    
    def cancel_subscription(self, key_expr: str):
        self.subscribers[key_expr] = []

    def is_closed(self):
        if (self.subscribers == defaultdict(list) and self.active_methods == dict() and self.metas == dict()):
            return True
        else:
            return False
        
    def _on_method_reply(self, on_reply: MethodReplyCallback, method: Method) -> MockCallback:
        def _on_reply(reply: MockSample) -> None:
            assert type(reply.value) == proto.ResponseData
            self._handle_on_method_reply(method, reply.key_expr, reply.value, on_reply)
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
    
    def _method_reply(self, key_expr: str, method: Method):
        return super()._method_reply(key_expr, method)
    
    def _on_method_query(self, method: Method):
        def _on_query(sample: MockSample) -> None:
            assert type(sample.value) == proto.MethodQueryData
            self._handle_method_query(method, sample.key_expr, sample.value)
        return _on_query
    
    def method_queryable(self, ks: NodeKeySpace, method: Method) -> None:
        super().method_queryable(ks, method)
    
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
    
    def pull_meta_messages(self, only_online: bool = False):
        metas: List[Meta] = []
        for key in self.metas:
            if (only_online == True):
                if (self.session._liveliness_tokens[key] == True):
                    metas.append(self.metas.get(key))
            else:
                metas.append(self.metas.get(key))
        return metas
    
    def update_liveliness(self, ks: NodeKeySpace, liveliness: bool):
        self.session._liveliness_tokens.update({ks.user_key: liveliness})

    def update_tag(self, ks: NodeKeySpace, path: str, value: proto.TagData):
        key_expr = ks.tag_data_path(path)
        self._send_proto(key_expr, value)

    def send_meta(self, ks: NodeKeySpace, meta: proto.Meta):
        self.metas[ks.user_key] = meta
    
    def send_state(self, ks: NodeKeySpace, state: proto.State):
        # maybe MockComm will implement state at some point
        key_expr = ks.state_key_prefix
        if (state.online != None):
            self.update_liveliness(ks, state.online)
        self._send_proto(key_expr, state)
    
    def liveliness_token(self, ks: NodeKeySpace) -> None:
        # MockComm doesn't worry about this for now, but we need to override Comm
        pass