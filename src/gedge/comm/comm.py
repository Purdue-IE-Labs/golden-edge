import base64
import zenoh
import json
from gedge.edge.error import NodeLookupError
from gedge import proto
from gedge.comm import keys
from gedge.comm.keys import NodeKeySpace
from gedge.edge.gtypes import ZenohCallback, ZenohQueryCallback, ZenohReplyCallback

ProtoMessage = proto.Meta | proto.TagData | proto.WriteResponseData | proto.State | proto.MethodCall

# handle Zenoh communications
# The user will not interact with this item
class Comm:
    def __init__(self):
        # TODO: user should specify which router than want to connect to 
        config = json.dumps({
            "mode": "client",
        })
        config = zenoh.Config.from_json5(config)
        self.config = config
        self.__enter__()

    def __enter__(self):
        session = zenoh.open(self.config)
        self.session = session
        return self
    
    def __exit__(self, *exc):
        self.session.close()

    def serialize(self, proto: ProtoMessage) -> bytes:
        b = proto.SerializeToString()
        b = base64.b64encode(b)
        return b
    
    def deserialize(self, proto: ProtoMessage, payload: bytes) -> ProtoMessage:
        b = base64.b64decode(payload)
        proto.ParseFromString(b)
        return proto

    def _send_proto(self, key_expr: str, value: proto.Meta | proto.State | proto.TagData):
        b = self.serialize(value)
        self.session.put(key_expr, b, encoding="application/protobuf")
    
    def liveliness_token(self, ks: NodeKeySpace) -> zenoh.LivelinessToken:
        key_expr = ks.liveliness_key_prefix
        return self.session.liveliness().declare_token(key_expr)

    def liveliness_subscriber(self, ks: NodeKeySpace, handler: ZenohCallback) -> zenoh.Subscriber:
        key_expr = ks.liveliness_key_prefix
        return self.session.liveliness().declare_subscriber(key_expr, handler)

    def query_liveliness(self, ks: NodeKeySpace) -> zenoh.Reply:
        key_expr = ks.liveliness_key_prefix
        return self.session.liveliness().get(key_expr).recv()

    def _subscriber(self, key_expr: str, handler: ZenohCallback) -> zenoh.Subscriber:
        return self.session.declare_subscriber(key_expr, handler)
    
    def _queryable(self, key_expr: str, handler: ZenohQueryCallback) -> zenoh.Queryable:
        return self.session.declare_queryable(key_expr, handler)
    
    def _query_sync(self, key_expr: str, payload: bytes) -> zenoh.Reply:
        return self.session.get(key_expr, payload=payload)
    
    def _query_callback(self, key_expr: str, payload: bytes, handler: ZenohReplyCallback) -> None:
        self.session.get(key_expr, payload=payload, handler=handler)
    
    def meta_subscriber(self, ks: NodeKeySpace, handler: ZenohCallback) -> zenoh.Subscriber:
        key_expr = ks.meta_key_prefix
        return self._subscriber(key_expr, handler)
    
    def state_subscriber(self, ks: NodeKeySpace, handler: ZenohCallback) -> zenoh.Subscriber:
        key_expr = ks.state_key_prefix
        return self._subscriber(key_expr, handler)
    
    def tag_data_subscriber(self, ks: NodeKeySpace, path: str, handler: ZenohCallback) -> zenoh.Subscriber:
        key_expr = ks.tag_data_path(path)
        return self._subscriber(key_expr, handler)

    def tag_queryable(self, ks: NodeKeySpace, path: str, on_write: ZenohQueryCallback) -> zenoh.Queryable:
        key_expr = ks.tag_write_path(path)
        return self._queryable(key_expr, on_write)
    
    def query_tag(self, ks: NodeKeySpace, path: str, value: proto.TagData) -> zenoh.Reply:
        b = self.serialize(value)
        return self._query_sync(ks.tag_write_path(path), payload=b)
    
    def method_queryable(self, ks: NodeKeySpace, path: str, on_call: ZenohQueryCallback) -> zenoh.Queryable:
        return self._queryable(ks.method_path(path), on_call)
    
    def query_method(self, ks: NodeKeySpace, path: str, params: dict[str, proto.TagData], on_reply: ZenohReplyCallback) -> None:
        key_expr = ks.method_path(path)
        method_call = proto.MethodCall(parameters=params)
        b = self.serialize(method_call)
        self._query_callback(key_expr, payload=b, handler=on_reply)

    def update_tag(self, ks: NodeKeySpace, path: str, value: proto.TagData):
        key_expr = ks.tag_data_path(path)
        self._send_proto(key_expr, value)

    def write_tag(self, ks: NodeKeySpace, path: str, value: proto.TagData) -> proto.WriteResponseData:
        reply = self.query_tag(ks, path, value)
        if reply.ok:
            d = self.deserialize(proto.WriteResponseData(), reply.result.payload.to_bytes())
            print(f"returning {d}")
            return d
        else:
            print("raising exception")
            raise Exception("reply super not ok")

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
                print(f"couldn't decode {e}")
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
            reply = self.query_liveliness(ks.liveliness_key_prefix)
            if not reply.ok:
                return False
            return reply.result.kind == zenoh.SampleKind.PUT
        except:
            return False
