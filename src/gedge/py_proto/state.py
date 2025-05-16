from dataclasses import dataclass

from gedge import proto

@dataclass
class State:
    online: bool

    @classmethod
    def from_proto(cls, proto: proto.State):
        return cls(proto.online)
    
    def to_proto(self):
        return proto.State(online=self.online)