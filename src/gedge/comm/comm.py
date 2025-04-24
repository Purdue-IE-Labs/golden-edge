from __future__ import annotations

import base64
from tkinter import W
import uuid
import zenoh
import json
from gedge.comm.sequence_number import SequenceNumber
from gedge.node import codes
from gedge.node.error import NodeLookupError, TagLookupError
from gedge import proto
from gedge.comm import keys
from gedge.comm.keys import NodeKeySpace, internal_to_user_key, method_response_from_call

from typing import Any, TYPE_CHECKING, Callable

from gedge.node.gtypes import LivelinessCallback, MetaCallback, MethodHandler, MethodReplyCallback, StateCallback, TagDataCallback, TagBaseValue, TagValue, TagWriteHandler
from gedge.node.method import MethodConfig
from gedge.node.method_reply import MethodReply
from gedge.node.method_response import MethodResponseConfig
from gedge.node.param import params_proto_to_py
from gedge.node.body import BodyConfig
from gedge.py_proto.data_model_config import DataModelConfig
from gedge.py_proto.data_model_object_config import DataModelObjectConfig
from gedge.py_proto.data_object_config import DataObjectConfig
from gedge.py_proto.props import Props
from gedge.node.query import MethodQuery
from gedge.py_proto.tag_config import TagConfig, TagWriteResponseConfig
from gedge.py_proto.data_model import DataObject
from gedge.node.tag_write_query import TagWriteQuery
if TYPE_CHECKING:
    from gedge.node.gtypes import ZenohCallback, ZenohQueryCallback, ZenohReplyCallback

ProtoMessage = proto.Meta | proto.DataObject | proto.TagWriteResponse | proto.State | proto.MethodCall | proto.MethodResponse | proto.DataModelConfig

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
        self.sequence_number = SequenceNumber()
    
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

        # TODO: how should sequence numbers be handled with queries and all that
        self.session.put(key_expr, b, encoding="application/protobuf", attachment=bytes(self.sequence_number))
        self.sequence_number.increment()
    
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

    def _on_tag_data(self, on_tag_data: TagDataCallback, tags: dict[str, TagConfig]) -> ZenohCallback:
        def _on_tag_data(sample: zenoh.Sample):
            data: proto.DataObject = self.deserialize(proto.DataObject(), sample.payload.to_bytes())
            logger.debug(f"Sample received on key expression {str(sample.key_expr)}, value = {data}, sequence_number = {sample.attachment.to_string() if sample.attachment else 0}")
            path: str = NodeKeySpace.tag_path_from_key(str(sample.key_expr))
            if path not in tags:
                node: str = NodeKeySpace.name_from_key(str(sample.key_expr))
                raise TagLookupError(path, node)
            tag_config = tags[path]
            value = DataObject.proto_to_py(data, tag_config.data_object_config)
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

    def _on_method_reply(self, on_reply: MethodReplyCallback, method: MethodConfig) -> ZenohCallback:
        def _on_reply(sample: zenoh.Sample) -> None:
            if not sample:
                logger.warning(f"reply from method failed")
                return
            r: proto.MethodResponse = self.deserialize(proto.MethodResponse(), sample.payload.to_bytes())
            self._handle_on_method_reply(method, str(sample.key_expr), r, on_reply)
        return _on_reply
    
    def _handle_on_method_reply(self, method: MethodConfig, key_expr: str, r: proto.MethodResponse, on_reply: MethodReplyCallback) -> None:
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
            response_config: MethodResponseConfig = MethodResponseConfig(r.code, Props.empty(), BodyConfig.empty())
        else:
            response_config: MethodResponseConfig = responses[r.code]
        body: dict[str, DataObject] = {}
        for key, value in r.body.items():
            body_config = response_config.body[key]
            props = response_config.body[key].props
            body[key] = DataObject.from_proto(value, body_config)
        props = response_config.props.to_value()
        reply = MethodReply(key_expr, r.code, body, r.error, props)
        on_reply(reply)
        if r.code in {codes.DONE, codes.METHOD_ERROR}:
            logger.debug(f"remove subscription for key expr {key_expr}")
            self.cancel_subscription(key_expr)
    
    def _tag_write_reply(self, query: zenoh.Query) -> Callable[[int, str], None]:
        def _reply(code: int, error: str = ""):
            write_response = proto.TagWriteResponse(code=code, error=error)
            b = self.serialize(write_response)
            query.reply(key_expr=str(query.key_expr), payload=b)
        return _reply

    def _on_tag_write(self, tag: TagConfig) -> ZenohQueryCallback:
        def _on_write(query: zenoh.Query) -> None:
            reply = self._tag_write_reply(query)
            try:
                if not query.payload:
                    raise ValueError(f"Empty write request")
                proto_data = self.deserialize(proto.DataObject(), query.payload.to_bytes())
                data: DataObject = DataObject.from_proto(proto_data, tag.data_object_config)
                logger.info(f"Node {query.key_expr} received tag write at path '{tag.path}' with value '{data}'")

                t = TagWriteQuery(str(query.key_expr), data, tag, reply)
                assert tag.write_handler is not None
                tag.write_handler(t)
                
                try:
                    code = t.code
                    error = t.error
                except:
                    raise ValueError(f"Tag write handler must call 'reply(...)' at some point")

                write_responses: dict[int, TagWriteResponseConfig] = {r.code:r for r in tag.responses}
                if code not in write_responses:
                    raise LookupError(f"Tag write handler for tag {tag.path} given incorrect code {code} not found in callback config")

                response = [code, error]
            except Exception as e:
                logger.warning(f"Sending tag write response on path {tag.path}: error={repr(e)}")
                response = [code, error]
            finally:
                reply(*response)
        return _on_write
    
    def _method_reply(self, key_expr: str, method: MethodConfig) -> Callable[[int, dict[str, TagValue], str], None]:
        responses = method.responses
        def _reply(code: int, body: dict[str, TagValue] = {}, error: str = "") -> None:
            if code not in {i.code for i in responses} and code not in {codes.DONE, codes.METHOD_ERROR, codes.TAG_ERROR}:
                raise ValueError(f"invalid repsonse code {code}")
            new_body: dict[str, proto.DataObject] = {}
            for key, value in body.items():
                response = [i for i in responses if i.code == code][0]
                config = response.body[key]
                new_body[key] = DataObject.py_to_proto(value, config)
            r = proto.MethodResponse(code=code, body=new_body, error=error)
            self._send_proto(key_expr=key_expr, value=r)
        return _reply
    
    def _on_method_query(self, method: MethodConfig):
        def _on_query(sample: zenoh.Sample) -> None:
            m = self.deserialize(proto.MethodCall(), sample.payload.to_bytes())
            self._handle_method_query(method, str(sample.key_expr), m)
        return _on_query

    def _handle_method_query(self, method: MethodConfig, key_expr: str, value: proto.MethodCall):
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
    
    def tag_data_subscriber(self, ks: NodeKeySpace, path: str, handler: TagDataCallback, tags: dict[str, TagConfig]) -> None:
        key_expr = ks.tag_data_path(path)
        zenoh_handler = self._on_tag_data(handler, tags)
        self._subscriber(key_expr, zenoh_handler)

    def tag_queryable(self, ks: NodeKeySpace, tag: TagConfig) -> zenoh.Queryable:
        key_expr = ks.tag_write_path(tag.path)
        zenoh_handler = self._on_tag_write(tag)
        logger.debug(f"tag queryable on {key_expr}")
        return self._queryable(key_expr, zenoh_handler)
    
    def query_tag(self, ks: NodeKeySpace, path: str, value: proto.DataObject) -> zenoh.Reply:
        b = self.serialize(value)
        logger.debug(f"querying tag at path {ks.tag_write_path(path)}")
        return self._query_sync(ks.tag_write_path(path), payload=b)
    
    def method_queryable(self, ks: NodeKeySpace, method: MethodConfig) -> None:
        key_expr = ks.method_query_listen(method.path)
        logger.info(f"Setting up method at path {method.path} on node {ks.name}")
        zenoh_handler = self._on_method_query(method)
        self._subscriber(key_expr, zenoh_handler)
    
    def query_method(self, ks: NodeKeySpace, path: str, caller_id: str, params: dict[str, proto.DataObject], on_reply: MethodReplyCallback, method: MethodConfig) -> str:
        method_query_id = str(uuid.uuid4())
        query_key_expr = ks.method_query(path, caller_id, method_query_id)
        query_data = proto.MethodCall(params=params)

        response_key_expr = ks.method_response(path, caller_id, method_query_id)
        zenoh_handler = self._on_method_reply(on_reply, method)
        self._subscriber(response_key_expr, zenoh_handler)
        self._send_proto(query_key_expr, query_data)

        return query_key_expr

    def update_tag(self, ks: NodeKeySpace, path: str, value: proto.DataObject):
        key_expr = ks.tag_data_path(path)
        self._send_proto(key_expr, value)

    def write_tag(self, ks: NodeKeySpace, path: str, value: proto.DataObject) -> proto.TagWriteResponse:
        reply = self.query_tag(ks, path, value)
        if reply.ok:
            d: proto.TagWriteResponse = self.deserialize(proto.TagWriteResponse(), reply.result.payload.to_bytes())
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
    
    def pull_meta_messages(self, only_online: bool = False) -> list[proto.Meta]:
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
            logger.warning(f"No model found at path {path} with version {version}")
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
                return None
        else:
            models = self._pull_all_model_versions(path)
            if not models:
                logger.warning(f"No model at path {path}")
                return None
            model = max(models, key=lambda m : m.version)
        
        if model.parent is not None:
            if not self.fetch_model(model.parent):
                logger.warning(f"Unable to fetch parent model {model.parent.path}")
        for tag in model.items:
            if not tag.config.is_model_path():
                continue
            if not self.fetch_model(tag.config.get_model_type()): # type: ignore
                logger.warning(f"Unable to fetch model {tag.config.config.config.path} for tag at path {tag.path}") # type: ignore
        return model
    
    def push_model(self, model: DataModelConfig, push_embedded: bool = True) -> bool:
        # TODO: if they use an embedded model but pass push_embedded=False, we run the risk of losing that model
        if push_embedded:
            if model.parent and model.parent.is_embedded():
                m = model.parent.get_embedded()
                if not m:
                    return False
                if not self.push_model(m, push_embedded):
                    return False
                model.parent.to_model_path()

            # Design decision: if we want to push recursively, we only do this for embedded models, not just path ones
            # Embedded includes both model and model_file
            for tag in model.items:
                model_config = tag.config.get_model_config()
                if not model_config:
                    continue
                logger.debug(f"Pushing embedded model {model_config.path}")
                if not self.push_model(model_config, push_embedded):
                    return False
                tag.config.to_model_path()

        res = self.pull_model(model.path)
        if res and res.version + 1 != model.version:
            logger.warning(f"Trying to update a model at path {model.path} without incrementing version, latest model in historian is {res.version}, you passed {model.version}! Try passing in a model with version {res.version + 1}")
            return False
        if not res and model.version not in {0, 1}:
            logger.warning(f"New model must start at version 0 or 1, found version {model.version}")
            return False
        key_expr = keys.model_path(model.path, model.version)
        self._send_proto(key_expr, model.to_proto())
        return True

    def fetch_model(self, config: DataModelObjectConfig) -> DataModelConfig | None:
        if config.is_embedded():
            return config.get_embedded()
        path = config.repr
        model = self.pull_model(path.path, path.version)
        if not model:
            return None
        config.repr = model
        return model