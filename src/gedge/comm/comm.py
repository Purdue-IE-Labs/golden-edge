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
        config = json.dumps({ "mode": "client" })
        config = zenoh.Config.from_json5(config)
        self.config = config
        self.__enter__()

    def __enter__(self):
        session = zenoh.open(self.config)
        self.session = session
        return self
    
    def __exit__(self, *exc):
        self.session.close()

    def liveliness_token(self, key_expr: str) -> zenoh.LivelinessToken:
        return self.session.liveliness().declare_token(key_expr)

    def liveliness_subscriber(self, key_expr: str, handler: ZenohCallback) -> zenoh.Subscriber:
        return self.session.liveliness().declare_subscriber(key_expr, handler)

    def subscriber(self, key_expr: str, handler: ZenohCallback) -> zenoh.Subscriber:
        # print(f"adding subscriber on key: {key_expr}")
        return self.session.declare_subscriber(key_expr, handler)

    def query_liveliness(self, key_expr: str) -> zenoh.Reply:
        return self.session.liveliness().get(key_expr).recv()
    
    def tag_queryable(self, ks: NodeKeySpace, path: str, on_write: ZenohQueryCallback) -> zenoh.Queryable:
        # print(f"tag queryable on path: {ks.tag_write_path(path)}")
        return self.session.declare_queryable(ks.tag_write_path(path), on_write)
    
    def query_tag(self, ks: NodeKeySpace, path: str, value: proto.TagData) -> zenoh.Reply:
        b = self.serialize(value)
        return self.session.get(ks.tag_write_path(path), payload=b).recv()
    
    def method_queryable(self, ks: NodeKeySpace, path: str, on_call: ZenohQueryCallback) -> zenoh.Queryable:
        # print(f"method queryable on path: {ks.method_path(path)}")
        return self.session.declare_queryable(ks.method_path(path), on_call)
    
    def query_method(self, ks: NodeKeySpace, path: str, params: dict[str, proto.TagData], on_reply: ZenohReplyCallback) -> None:
        b = self.serialize(proto.MethodCall(parameters=params))
        self.session.get(ks.method_path(path), payload=b, handler=on_reply)
    
    def deserialize(self, proto: ProtoMessage, payload: bytes) -> ProtoMessage:
        b = base64.b64decode(payload)
        proto.ParseFromString(b)
        return proto
    
    def serialize(self, proto: ProtoMessage) -> bytes:
        b = proto.SerializeToString()
        b = base64.b64encode(b)
        return b

    def _send_protobuf(self, key_expr: str, value: proto.Meta | proto.State | proto.TagData):
        b = self.serialize(value)
        self.session.put(key_expr, b)

    def send_meta(self, key_prefix: str, name: str, meta: proto.Meta):
        key = keys.meta_key_prefix(key_prefix, name)
        # print(f"sending meta on key expression: {key}")
        self._send_protobuf(key, meta)
    
    def update_tag(self, key_prefix: str, name: str, key: str, value: proto.TagData):
        key = keys.tag_data_key(key_prefix, name, key)
        # print(f"updating tag on key expression: {key} with value {value}")
        self._send_protobuf(key, value)

    def write_tag(self, ks: NodeKeySpace, path: str, value: proto.TagData) -> proto.WriteResponseData:
        key_expr = ks.tag_write_path(path)
        # print(f"writing tag on key expression: {key_expr}")
        reply = self.query_tag(ks, path, value)
        if reply.ok:
            d = self.deserialize(proto.WriteResponseData(), reply.result.payload.to_bytes())
            print(f"returning {d}")
            return d
        else:
            print("raising exception")
            raise Exception("reply super not ok")
    
    def call_method(self, ks: NodeKeySpace, path: str, params: dict[str, proto.TagData], on_reply: ZenohReplyCallback) -> None:
        key_expr = ks.method_path(path)
        print(f"calling method on key expression: {key_expr}")
        self.query_method(ks, path, params, on_reply)
        # if reply.ok:
        #     d = self.deserialize(ResponseData(), reply.result.payload.to_bytes())
        #     print(f"returning {d}")
        #     return d
        # else:
        #     print("raising exception")
        #     raise Exception("reply super not ok")

    def send_state(self, key_prefix: str, name: str, state: proto.State):
        key = keys.state_key_prefix(key_prefix, name)
        # print(f"sending state on key expression: {key}")
        self._send_protobuf(key, state)

    def pull_meta_messages(self, key_prefix: str, only_online: bool = False) -> list[proto.Meta]:
        res = self.session.get(f"{key_prefix}/NODE/*/META")
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
    
    def pull_all_meta_messages(self, only_online: bool = False):
        res = self.session.get(f"**/NODE/*/META")
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
        # print(f"searching on key expr: {ks.user_key}")
        try:
            reply = self.session.get(ks.meta_key_prefix).recv()
        except:
            raise NodeLookupError(ks.user_key)
        if not reply.ok:
            raise NodeLookupError(ks.user_key)
        
        meta = self.deserialize(proto.Meta(), reply.result.payload.to_bytes())
        return meta
            
    def is_online(self, ks: NodeKeySpace) -> bool:
        # this command will fail is no token is declared for this prefix, meaning offline
        try:
            reply = self.query_liveliness(ks.liveliness_key_prefix)
            if not reply.ok:
                return False
            return reply.result.kind == zenoh.SampleKind.PUT
        except:
            return False
