from __future__ import annotations

import base64
import uuid
import zenoh
import json
from gedge.comm.sequence_number import SequenceNumber
from gedge.node import codes
from gedge.node.error import NodeLookupError, QueryEnd, TagLookupError
from gedge import proto
from gedge.comm import keys
from gedge.comm.keys import NodeKeySpace, group_path_from_key, internal_to_user_key, key_join, method_response_from_call, tag_path_from_key

from typing import Any, TYPE_CHECKING, Callable

from gedge.node.reply import Response
from gedge.py_proto.base_data import BaseData
from gedge.py_proto.conversions import props_to_json5
from gedge.py_proto.data_model_config import DataItemConfig, DataModelConfig
from gedge.node.query import MethodQuery, TagWriteQuery
from gedge.py_proto.data_model_ref import DataModelRef
from gedge.py_proto.state import State
from gedge.py_proto.tag_config import Tag, TagConfig 
if TYPE_CHECKING:
    from gedge.node.gtypes import LivelinessCallback, MetaCallback, MethodReplyCallback, StateCallback, TagDataCallback, TagValue, ZenohCallback, ZenohQueryCallback, ProtoMessage
    from gedge.node.method import MethodConfig
    from gedge.py_proto.meta import Meta

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
                "endpoints": connections,
                "timeout_ms": 3 * 1000,
                "exit_on_failure": True
            }
        })
        self.config = config
        self.connections = connections
        self.subscriptions: list[zenoh.Subscriber] = []
        self.sequence_number = SequenceNumber()
    
    def connect(self):
        '''
        Creates and opens the Zenoh session
        '''
        self.__enter__()
    
    def close(self):
        '''
        Closes the current Zenoh session
        '''
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
        '''
        Closes the node to Zenoh connection by undeclaring the current subscriptions

        Arguments:
            ks (NodeKeySpace): The key space of the node losing the connection

        Returns:
            None
        '''

        logger.info(f"Closing remote connection to {ks.user_key}")
        # TODO: will this be affected by one node having multiple instance connections to
        # the same remote? do we even allow that?
        subscriptions = [s for s in self.subscriptions if ks.contains(str(s.key_expr))]
        logger.debug(f"Undeclaring {len(subscriptions)} remote subscriptions")
        for s in subscriptions:
            s.undeclare()

    def serialize(self, proto: ProtoMessage) -> bytes:
        '''
        Converts the passed ProtoMessage to a base 64 encoded bytes object
        
        Note: In this instance "ProtoMessage" means proto.Meta | proto.TagData | proto.WriteResponseData | proto.State | proto.MethodQueryData | proto.ResponseData | proto.WriteResponseData

        Arguments:
            proto (ProtoMessage): The ProtoMessage being converted to bytes

        Returns:
            bytes: The ProtoMessage converted to bytes
        '''
        b = proto.SerializeToString()
        logger.debug(f"Size of serialized protobuf: {len(b)}")
        # TODO: base64 is needed due to errors with carriage returns in influxdb
        # which we should try to address in a better way than this
        # Base64 adds about 25% to the payload size (y = 4/3 * x, where x is the original payload and y is the new payload)
        # Example: 5 bytes encoded as base64 will become 8 bytes
        b = base64.b64encode(b)
        logger.debug(f"Size of serialized protobuf base64 encoded {len(b)}")
        return b
    
    def deserialize(self, proto: ProtoMessage, payload: bytes) -> Any:
        '''
        Converts the passed payload to a ProtoMessage

        Arguments:
            proto (ProtoMessage): The ProtoMessage that will be returned by the function as a ProtoMessage
            payload(bytes): The bytes object that will be converted to the ProtoMessage object

        Returns:
            Any: The payload converted to a ProtoMessage
        '''
        b = base64.b64decode(payload)
        proto.ParseFromString(b)
        return proto

    def _send_proto(self, key_expr: str, value: ProtoMessage):
        '''
        Sends the passed ProtoMessage to the passed node

        Arguments:
            key_expr (str): The key expression of a node
            value (ProtoMessage): The value being passed to the node

        Returns:
            None
        '''
        logger.debug(f"putting proto on key_expr '{key_expr}' with value {value}")
        b = self.serialize(value)
        self.session.put(key_expr, b, encoding="application/protobuf", attachment=bytes(self.sequence_number))
        self.sequence_number.increment()
    
    def liveliness_token(self, ks: NodeKeySpace) -> zenoh.LivelinessToken:
        '''
        Returns a liveliness token representing the liveliness (online state) of the passed node

        Arguments:
            ks (NodeKeySpace): The key space of the node whose liveliness is being checked

        Returns:
            zenoh.LivelinessToken
        '''
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

    # Tag Data is always of type BaseData
    def _on_tag_data(self, on_tag_data: TagDataCallback, tag_config: TagConfig) -> ZenohCallback:
        def _on_tag_data(sample: zenoh.Sample):
            data: proto.BaseData = self.deserialize(proto.BaseData(), sample.payload.to_bytes())
            logger.debug(f"Sample received on key expression {str(sample.key_expr)}, value = {data}, sequence_number = {sample.attachment.to_string() if sample.attachment else 0}")
            path: str = tag_path_from_key(str(sample.key_expr))
            try:
                config = tag_config.get_config(path)
            except:
                node: str = NodeKeySpace.name_from_key(str(sample.key_expr))
                raise TagLookupError(path, node)
            base_type = config.type.get_base_type()
            if base_type is None:
                raise ValueError("cannot write to model object")
            value = BaseData.proto_to_py(data, base_type)
            logger.debug(f"Remote node {internal_to_user_key(str(sample.key_expr))} received value {value} for tag {path}")
            on_tag_data(str(sample.key_expr), value)
        return _on_tag_data
    
    def _on_group_data_feed_to_tag_data_subscriber(self, on_tag_data: TagDataCallback, tag_config: TagConfig, path: str) -> ZenohCallback:
        def _func(sample: zenoh.Sample):
            data: proto.TagGroup = self.deserialize(proto.TagGroup(), sample.payload.to_bytes())
            group_path: str = group_path_from_key(str(sample.key_expr))
            configs = tag_config.get_group_member_configs(group_path)
            base_type = configs[path].get_base_type()
            if not base_type:
                raise ValueError
            value = BaseData.proto_to_py(data.data[path], base_type)
            logger.debug(f"Remote node {internal_to_user_key(str(sample.key_expr))} received value {value} for tag {path}")
            on_tag_data(str(sample.key_expr), value)
        return _func
    
    '''
    TODO: eventually, support nesting in API
    Example:
    update_group({"tag/tag": 10})
    vs
    update_group({
        "tag": {
            "tag": 10
        }
    })
    '''
    def _on_group_data(self, on_group_data: TagDataCallback, tag_config: TagConfig) -> ZenohCallback:
        def _on_group_data(sample: zenoh.Sample):
            data: proto.TagGroup = self.deserialize(proto.TagGroup(), sample.payload.to_bytes())
            logger.debug(f"Sample received on key expression {str(sample.key_expr)}, value = {data}, sequence_number = {sample.attachment.to_string() if sample.attachment else 0}")
            group_path: str = group_path_from_key(str(sample.key_expr))
            configs = tag_config.get_group_member_configs(group_path)
            # print(configs)

            new_data: dict[str, TagValue] = {}
            # value here must be of type BaseData
            for key, value in data.data.items():
                new_data[key] = BaseData.from_proto(value, configs[key].get_base_type()).to_py() # type: ignore
            on_group_data(str(sample.key_expr), new_data)
        return _on_group_data

    def _on_state(self, on_state: StateCallback) -> ZenohCallback:
        def _on_state(sample: zenoh.Sample):
            state: proto.State = self.deserialize(proto.State(), sample.payload.to_bytes())
            logger.debug(f"Remote node {internal_to_user_key(str(sample.key_expr))} received state message: online = {state.online}")
            on_state(str(sample.key_expr), State.from_proto(state))
        return _on_state

    def _on_meta(self, on_meta: MetaCallback) -> ZenohCallback:
        def _on_meta(sample: zenoh.Sample):
            meta: proto.Meta = self.deserialize(proto.Meta(), sample.payload.to_bytes())
            logger.debug(f"Remote node {internal_to_user_key(str(sample.key_expr))} received meta message")
            on_meta(str(sample.key_expr), Meta.from_proto(meta))
        return _on_meta

    def _on_method_reply(self, on_reply: MethodReplyCallback, method: MethodConfig) -> ZenohCallback:
        def _on_reply(sample: zenoh.Sample) -> None:
            if not sample:
                logger.warning(f"reply from method failed")
                return
            r: proto.Response = self.deserialize(proto.Response(), sample.payload.to_bytes())
            self._handle_on_method_reply(method, str(sample.key_expr), r, on_reply)
        return _on_reply
    
    def _handle_on_method_reply(self, method: MethodConfig, key_expr: str, r: proto.Response, on_reply: MethodReplyCallback) -> None:
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
        response_config = codes.config_from_code(r.code, method.responses)
        body: dict[str, TagValue] = response_config.body_proto_to_value(dict(r.body))
        props = props_to_json5(response_config.props)
        reply = Response(key_expr, r.code, response_config.type, body, props)
        on_reply(reply)
        if codes.is_final_method_response(reply):
            logger.debug(f"remove subscription for key expr {key_expr}")
            self.cancel_subscription(key_expr)
    
    def _tag_write_reply(self, query: zenoh.Query, tag: Tag) -> Callable[[int, dict[str, TagValue]], None]:
        def _reply(code: int, body: dict[str, TagValue]):
            path = tag_path_from_key(str(query.key_expr))
            responses, _ = tag.write_config[path]
            response_config = codes.config_from_code(code, responses)
            new_body: dict[str, proto.DataItem] = response_config.body_value_to_proto(body)
            write_response = proto.Response(code=code, body=new_body)
            b = self.serialize(write_response)
            query.reply(key_expr=str(query.key_expr), payload=b)
        return _reply

    def _on_tag_write(self, tag: Tag, path: str) -> ZenohQueryCallback:
        from gedge.node.method_response import ResponseType
        def _on_write(query: zenoh.Query) -> None:
            reply = self._tag_write_reply(query, tag)
            if not query.payload:
                reply(codes.CALLBACK_ERR, {"reason": "Empty write request"})
                return
            proto_data = self.deserialize(proto.BaseData(), query.payload.to_bytes())

            try: 
                config = tag.get_config(path)
                data: BaseData = BaseData.from_proto(proto_data, config.get_base_type()) # type: ignore
                logger.info(f"Node {query.key_expr} received tag write at path '{tag.path}' with value '{data}'")
            except:
                reply(codes.CALLBACK_ERR, {"reason": f"invalid path {path}"})
                return

            t = TagWriteQuery(str(query.key_expr), reply, tag.write_config[path][0], [], data.to_py())
            try:
                _, handler = tag.write_config[path]
                if handler is None:
                    raise Exception(f"No handler provided for tag {path}")
                handler(t)
            except QueryEnd as e:
                pass
            except Exception as e:
                t._reply(codes.CALLBACK_ERR, {"reason": str(e)}, ResponseType.ERR)
            finally:
                if not t._responses_sent or t._responses_sent[-1].type == ResponseType.INFO:
                    t._reply(codes.CALLBACK_ERR, { "reason": "tag write handler did not finish function with OK or ERR message" }, ResponseType.ERR)
            # reply(code, body)
        return _on_write
    
    def _method_reply(self, key_expr: str, method: MethodConfig) -> Callable[[int, dict[str, TagValue]], None]:
        responses = method.responses
        def _reply(code: int, body: dict[str, TagValue]) -> None:
            response_config = codes.config_from_code(code, responses)
            new_body: dict[str, proto.DataItem] = response_config.body_value_to_proto(body)
            r = proto.Response(code=code, body=new_body)
            self._send_proto(key_expr=key_expr, value=r)
        return _reply
    
    def _on_method_query(self, method: MethodConfig):
        def _on_query(sample: zenoh.Sample) -> None:
            m = self.deserialize(proto.MethodCall(), sample.payload.to_bytes())
            self._handle_method_query(method, str(sample.key_expr), m)
        return _on_query

    def _handle_method_query(self, method: MethodConfig, key_expr: str, value: proto.MethodCall):
        from gedge.node.method_response import ResponseType
        p = dict(value.params)
        params: dict[str, TagValue] = method.params_proto_to_py(p)
        
        key_expr = method_response_from_call(key_expr)
        reply_func = self._method_reply(key_expr, method)
        q = MethodQuery(key_expr, reply_func, method.responses, [], params)
        try:
            name = NodeKeySpace.user_key_from_key(key_expr)
            logger.info(f"Node {name} method call at path '{method.path}' with params {params}")
            logger.debug(f"Received from {key_expr}")
            assert method.handler is not None, "No method handler provided"
            method.handler(q)
        except QueryEnd as e:
            pass
        except Exception as e:
            # print("ENCOUNTERED EXCEPTION")
            body = {
                "reason": str(e)
            }
            q._reply(codes.CALLBACK_ERR, body, ResponseType.ERR) 
        finally:
            if not q._responses_sent or q._responses_sent[-1].type == ResponseType.INFO:
                q._reply(codes.CALLBACK_ERR, { "reason": "method handler did not finish function with OK or ERR message" }, ResponseType.ERR)

    def liveliness_subscriber(self, ks: NodeKeySpace, handler: LivelinessCallback) -> None:
        '''
        Creates a liveliness subscriber and adds it to the Zenoh session

        Arguments:
            ks (NodeKeySpace): The key space of the node recieving the Liveliness handler
            handler (LivelinessCallback): A callback that responds with the Liveliness state of the node

        Returns:
            None
        '''
        key_expr = ks.liveliness_key_prefix
        zenoh_handler = self._on_liveliness(handler)
        subscriber = self.session.liveliness().declare_subscriber(key_expr, zenoh_handler)
        self.subscriptions.append(subscriber)

    def _query_liveliness(self, ks: NodeKeySpace) -> zenoh.Reply:
        '''
        Acquires the liveliness state as a reply of the passed node in the Zenoh session
        
        Arguments:
            ks (NodeKeySpace): The key space of the node being checked

        Returns:
            zenoh.Reply: The liveliness response from the Zenoh session
        '''
        key_expr = ks.liveliness_key_prefix
        return self.session.liveliness().get(key_expr).recv()

    def _subscriber(self, key_expr: str, handler: ZenohCallback) -> None:
        '''
        Declares a subscriber with the passed handler on the node corresponding to the passed key expression

        Arguments:
            key_expr (str): The key expression of the node recieving the handler
            handler (ZenohCallback): The handler of the subscription being added

        Returns:
            None
        '''
        logger.debug(f"declaring subscriber on key expression '{key_expr}'")
        subscriber = self.session.declare_subscriber(key_expr, handler)
        self.subscriptions.append(subscriber)

    def cancel_subscription(self, key_expr: str):
        '''
        Removes all of the subscriptions of the node matching the passed key expression

        Arguments:
            key_expr (str): The key space of the node losing the subscriptions 

        Returns:
            None
        '''
        subs = [s for s in self.subscriptions if str(s.key_expr) == key_expr]
        logger.debug(f"canceling {len(subs)} subscriptions at key_expr = {key_expr}")
        for s in subs:
            s.undeclare()
            self.subscriptions.remove(s)
    
    def _queryable(self, key_expr: str, handler: ZenohQueryCallback) -> zenoh.Queryable:
        '''
        Declares a queryable in the current session on the node corresponding to the passed key expression

        Arguments:
            key_expr (str): The key expression of the node that the queryable is being declared upon
            handler (ZenohQueryCallback): The handler that is being declared as Queryable

        Returns:
            zenoh.Queryable: The new Zenoh Queryable created
        '''
        logger.debug(f"declaring queryable on key_expr = {key_expr}")
        return self.session.declare_queryable(key_expr, handler)
    
    def _query_sync(self, key_expr: str, payload: bytes) -> zenoh.Reply:
        '''
        Sends the passed payload to the node corresponding to the passed key expression and returns the reply from Zenoh

        Arguments:
            key_expr (str): The key expression of the node the payload is being passed to
            payload (bytes): The payload is being sent to the passed node

        Returns:
            zenoh.Reply
        '''
        try:
            reply = self.session.get(key_expr, payload=payload).recv()
        except Exception:
            raise LookupError(f"No queryable defined at {key_expr}")
        return reply
    
    def meta_subscriber(self, ks: NodeKeySpace, handler: MetaCallback) -> None:
        '''
        Declares a Meta subscriber with the passed handler on the passed node


        Arguments:
            ks (NodeKeySpace): The key space of the node recieving the Meta handler
            handler (MetaCallback): A MetaCallback handler

        Returns:
            None
        '''
        key_expr = ks.meta_key_prefix
        zenoh_handler = self._on_meta(handler)
        self._subscriber(key_expr, zenoh_handler)
    
    def state_subscriber(self, ks: NodeKeySpace, handler: StateCallback) -> None:
        '''
        Declares a State subscriber with the passed handler on the passed node

        Arguments:
            ks (NodeKeySpace): The key space of the node recieving the State handler
            handler: (StateCallback): A StateCallback handler

        Returns:
            None
        '''
        key_expr = ks.state_key_prefix
        zenoh_handler = self._on_state(handler)
        self._subscriber(key_expr, zenoh_handler)
    
    def cancel_tag_data_subscription(self, ks: NodeKeySpace, path: str) -> None:
        # TODO: handle groups
        key_expr = ks.tag_data_path(path)
        self.cancel_subscription(key_expr)
    
    def tag_data_subscriber(self, ks: NodeKeySpace, path: str, handler: TagDataCallback, tag_config: TagConfig) -> None:
        '''
        Declares a Tag Data subscriber with the passed handler on the passed node with the passed tags at the passed path

        Note: This is just creating a TagDataCallback on the passed node and it must include a given number of tags on the node, so we give it the path of the tags we are giving the handler to

        Arguments:
            ks (NodeKeySpace): The key space of the node recieving the Tag Data handler
            path (str): The path of the tags in the passed node
            handler (TagDataCallback): A TagDataCallback handler
            tag_config (TagConfig): Tag configuration for this node. It includes all tag and writable tag configurations

        Returns:
            None
        '''

        group = tag_config.get_group(path)
        if group:
            key_expr = ks.group_data_path(group)
            zenoh_handler = self._on_group_data_feed_to_tag_data_subscriber(handler, tag_config, path)
            self._subscriber(key_expr, zenoh_handler)
        else:
            key_expr = ks.tag_data_path(path)
            zenoh_handler = self._on_tag_data(handler, tag_config)
            self._subscriber(key_expr, zenoh_handler)
    
    def group_data_subscriber(self, ks: NodeKeySpace, group_path: str, handler: TagDataCallback, tag_config: TagConfig) -> None:
        key_expr = ks.group_data_path(group_path)
        zenoh_handler = self._on_group_data(handler, tag_config)
        self._subscriber(key_expr, zenoh_handler)

    def tag_queryable(self, ks: NodeKeySpace, tag: Tag, path: str | None = None) -> zenoh.Queryable:
        '''
        Registeres a zenoh queryable at <prefix>/NODE/<name>/TAGS/DATA/<path>
        If path is None, path defaults to the tag's path. This is to allow for queryables on tags embedded within models.

        Arguments:
            ks (NodeKeySpace): The key space of the node that has the queryable
            tag (Tag): The tag that has the queryable declared on it (or a subtag of it)
            path (str | None): The path on this node where the queryable should be registered

        Returns:
            zenoh.Queryable: A Zenoh key expression that is able to recieve queries and has a registered response defined
        '''
        if path is None:
            path = tag.path

        key_expr = ks.tag_write_path(path)
        zenoh_handler = self._on_tag_write(tag, path)
        logger.debug(f"tag queryable on {key_expr}")
        return self._queryable(key_expr, zenoh_handler)
    
    def _query_tag(self, key_expr: str, value: proto.BaseData) -> zenoh.Reply:
        '''
        Sends the passed value to the Tag on the passed path in the passed node

        Arguments:
            ks (NodeKeySpace): The key space of the node that the tag belongs to
            path (str): The path to the tag
            value (proto.TagData): The value that will be passed to the tag

        Returns:
            zenoh.Reply: The reply from Zenoh after passing the parameter value to the tag on the passed node
        '''
        b = self.serialize(value)
        logger.debug(f"querying tag at path {key_expr}")
        return self._query_sync(key_expr, payload=b)
    
    def _query_group(self, key_expr: str, value: proto.TagGroup) -> zenoh.Reply:
        b = self.serialize(value)
        logger.debug(f"querying group at path {key_expr}")
        return self._query_sync(key_expr, payload=b)
    
    def method_queryable(self, ks: NodeKeySpace, method: MethodConfig) -> None:
        '''
        Declares a method subscriber on the passed node with the passed method

        Arguments:
            ks (NodeKeySpace): The key space of the node that is setting up a method query
            method (Method): The method that will handle method queries

        Returns:
            None
        '''
        key_expr = ks.method_query_listen(method.path)
        logger.info(f"Setting up method at path {method.path} on node {ks.name}")
        zenoh_handler = self._on_method_query(method)
        self._subscriber(key_expr, zenoh_handler)
    
    def query_method(self, ks: NodeKeySpace, path: str, caller_id: str, params: dict[str, proto.DataItem], on_reply: MethodReplyCallback, method: MethodConfig) -> str:
        '''
        Queries the tag along the passed path between the caller and method query and then sends the response along proto
        
        Arguments:
            ks (NodeKeySpace): The key space of the node that method queries are being handled on
            path (str): The path of the tag which is being queried
            caller_id (str): The id of the caller of the method
            method_query_id (str): The id of the method query
            params (dict[str, proto.TagData]): The passed parameters for the Method Query Data
            on_reply (MethodReplyCallback): The MethodReplyCallback for the query
            method (Method): The method being queried
        
        Returns:
            str: The key expression of the query
        '''
        method_query_id = str(uuid.uuid4())
        query_key_expr = ks.method_query(path, caller_id, method_query_id)
        query_data = proto.MethodCall(params=params)

        response_key_expr = ks.method_response(path, caller_id, method_query_id)
        zenoh_handler = self._on_method_reply(on_reply, method)
        self._subscriber(response_key_expr, zenoh_handler)
        self._send_proto(query_key_expr, query_data)

        return query_key_expr

    def update_tag(self, ks: NodeKeySpace, path: str, value: proto.BaseData):
        '''
        Updates the tag within the passed node along the passed path with the passed value
        
        Arguments:
            ks (NodeKeySpace): The key space of the node whose tag is being updated
            path (str): The path of the tag
            value (proto.TagData): The value being sent to the tag within the node along the path
        
        Returns:
            None
        '''
        key_expr = ks.tag_data_path(path)
        self._send_proto(key_expr, value)

    def write_tag(self, ks: NodeKeySpace, path: str, value: BaseData) -> proto.Response:
        '''
        Queries the tag on the passed path in the passed node with the passed value
        
        Arguments:
            ks (NodeKeySpace): The key space of the node who is being written to
            path (str): The path of the tag in the node
            value (proto.Tagdata): The value being passed to the tag
        
        Returns:
            proto.WriteResponseData
        '''
        reply = self._query_tag(ks.tag_write_path(path), value.to_proto())
        if reply.ok:
            d: proto.Response = self.deserialize(proto.Response(), reply.result.payload.to_bytes())
            return d
        raise Exception(f"Failure in receiving tag write reply for tag at path {path}")
    
    def write_group(self, key_expr: str, value: dict[str, proto.BaseData]) -> proto.Response:
        reply = self._query_group(key_expr, proto.TagGroup(data=value))
        if reply.ok:
            d: proto.Response = self.deserialize(proto.Response(), reply.result.payload.to_bytes())
            return d
        raise Exception(f"Failure in receiving tag write reply for group at path {group_path_from_key(key_expr)}")

    def send_state(self, ks: NodeKeySpace, state: State):
        '''
        Sends the passed state to the passed node
        
        Arguments:
            ks (NodeKeySpace): The key space of the node who is being sent the state
            state (proto.State): The state being sent to the node
        
        Returns:
            None
        '''
        key_expr = ks.state_key_prefix
        self._send_proto(key_expr, state.to_proto())

    def send_meta(self, ks: NodeKeySpace, meta: Meta):
        '''
        Sends the passed meta to the passed node
        
        Arguments:
            ks (NodeKeySpace): The key space of the node who is being sent the meta
            meta (proto.Meta): The meta being sent to the node
        
        Returns:
            None
        '''
        key_expr = ks.meta_key_prefix
        self._send_proto(key_expr, meta.to_proto())
    
    def pull_meta_messages(self, only_online: bool = False) -> list[Meta]:
        '''
        Pulls all Metas in the current Zenoh session of online nodes

        Note: The only_online parameter translates to "Only give me meta messages from the historian of nodes that are currently online"
        
        Arguments:
            only_online (bool): The current online state of a given node
        
        Returns:
            list[Meta]: A list of the Meta messages
        '''
        from gedge.py_proto.meta import Meta
        res = self.session.get(keys.key_join("**", keys.NODE, "*", keys.META))
        messages: list[Meta] = []
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
                messages.append(Meta.from_proto(meta))
            except Exception as e:
                raise ValueError(f"Could not deserialize meta from historian: {e}")
        return messages

    def pull_meta_message(self, ks: NodeKeySpace) -> Meta:
        from gedge.py_proto.meta import Meta
        '''
        Returns the Meta of the passed node
        
        Arguments:
            ks (NodeKeySpace): The key space of the node whose meta message is being pulled
        
        Returns:
            proto.Meta
        '''
        try:
            reply = self.session.get(ks.meta_key_prefix).recv()
        except:
            raise NodeLookupError(ks.user_key)
        if not reply.ok:
            raise NodeLookupError(ks.user_key)
        
        meta = self.deserialize(proto.Meta(), reply.result.payload.to_bytes())
        return Meta.from_proto(meta)
            
    def is_online(self, ks: NodeKeySpace) -> bool:
        '''
        Returns the liveliness of the passed node
        
        Arguments:
            ks (NodeKeySpace): The key space of the node whose liveliness is being queried
        
        Returns:
            bool: The online state of the passed node
        '''
        try:
            reply = self._query_liveliness(ks)
            if not reply.ok:
                raise Exception # generic exception to trigger the except:
            return reply.ok.kind == zenoh.SampleKind.PUT
        except:
            return False
    
    def _pull_all_model_versions(self, path: str) -> list[DataModelConfig]:
        models = []
        res = self.session.get(keys.model_fetch(path))
        for r in res:
            r: zenoh.Reply
            if r.err:
                continue
            result = r.result
            assert isinstance(result, zenoh.Sample)
            try:
                config = self.deserialize(proto.DataModelConfig(), result.payload.to_bytes())
                config = DataModelConfig.from_proto(config)
                pulled_version = keys.version_from_model(str(result.key_expr))
                if config.version != pulled_version:
                    logger.warning(f"Versions do not match for model {path}, model says {config.version}, key says {pulled_version}")
                    return []
                models.append(config)
            except:
                raise ValueError(f"Could not deserialize model at path {path} from historian")
        return models
    
    def _pull_model_with_version(self, path: str, version: int) -> DataModelConfig | None:
        try:
            res = self.session.get(keys.model_path(path, version)).recv()
            if res.err:
                raise Exception
        except:
            logger.info(f"No model found at path {path} with version {version}")
            return None
        assert isinstance(res.result, zenoh.Sample)
        s = res.result
        try:
            config = self.deserialize(proto.DataModelConfig(), s.payload.to_bytes())
            config = DataModelConfig.from_proto(config)
        except:
            raise ValueError(f"Could not deserialize model at path {path} (version {version}) from historian")

        pulled_version = keys.version_from_model(str(s.key_expr))
        if config.version != pulled_version:
            logger.warning(f"Versions do not match for model {path}, model says {config.version}, key says {pulled_version}")
            return None
        return config
    
    # TODO: just take a DataModelType
    # we expand everything when we return it
    def pull_model(self, path: str, version: int | None = None) -> DataModelConfig | None:
        if version is not None:
            model = self._pull_model_with_version(path, version)
            if not model:
                logger.info(f"No model at path {path} with version {version}")
                return None
        else:
            models = self._pull_all_model_versions(path)
            if not models:
                logger.info(f"No model at path {path}")
                return None
            model = max(models, key=lambda m : m.version)
        
        if model.parent is not None:
            if not self._fetch(model.parent):
                logger.warning(f"Unable to fetch parent model {model.parent.path}")
        for item in model.items:
            ref = item.get_model_ref()
            if not ref:
                continue
            if not self._fetch(ref):
                logger.warning(f"Unable to fetch model {item.path} for tag at path {item.path}")
        return model
    
    def push_model(self, model: DataModelConfig, push_embedded: bool = True) -> bool:
        # TODO: if they use an embedded model but pass push_embedded=False, we run the risk of losing that model
        if push_embedded:
            # Design decision: if we want to push recursively, we only do this for embedded models, not just path ones
            # Embedded includes both model and model_file
            pass
            # for tag in model.items:
            #     model_config = tag.config.get_model_config()
            #     if not model_config:
            #         continue
            #     logger.debug(f"Pushing embedded model {model_config.path}")
            #     if not self.push_model(model_config, push_embedded):
            #         return False
            #     tag.config.to_model_path()

        res = self.pull_model(model.path)
        if res and res.version + 1 != model.version:
            # TODO: here we may check for equality of models before updating the version, 
            # but for now we just update and push
            logger.info(f"Trying to update a model at path {model.path} without incrementing version, latest model in historian is {res.version}, you passed {model.version}! Updating model to version {res.version + 1}...")
            model.version = res.version + 1
        if not res and model.version not in {0, 1}:
            logger.warning(f"New model must start at version 0 or 1, found version {model.version}")
            return False
        self._put_model(model)
        return True
    
    def _put_model(self, model: DataModelConfig):
        key_expr = keys.model_path(model.path, model.version)
        self._send_proto(key_expr, model.to_proto())

    def fetch_model(self, config: DataItemConfig) -> DataModelConfig | None:
        ref = config.get_model_ref()
        if not ref:
            return None
        return self._fetch(ref)
    
    def _fetch(self, ref: DataModelRef) -> DataModelConfig | None:
        return self.pull_model(ref.path, ref.version)
    
    def send_group(self, key_expr: str, proto: proto.TagGroup):
        self._send_proto(key_expr, proto)