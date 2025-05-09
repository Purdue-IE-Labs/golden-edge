from __future__ import annotations

import uuid
from gedge import proto
from gedge.comm.mock_comm import MockCallback, MockComm, MockSample
from gedge.comm.keys import NodeKeySpace
from gedge.node import codes
from gedge.node.body import BodyData
from gedge.node.error import MethodLookupError
from gedge.node.gtypes import TagValue, ZenohCallback
from gedge.node.method_reply import MethodReply
from gedge.node.method_response import MethodResponse
from gedge.node.node import NodeConfig, NodeSession
from gedge.node.prop import Props
from gedge.node.query import MethodQuery
from gedge.node.tag_data import TagData

from typing import TYPE_CHECKING, Any, Iterator
if TYPE_CHECKING:
    from gedge.node.gtypes import LivelinessCallback, MetaCallback, StateCallback, TagDataCallback, TagValue, Type, ZenohQueryCallback, TagWriteHandler, MethodHandler

'''
TODO: (Design Decision): It appears that dataclasses are "in" these 
days in python land. They generally just seem to look like pretty normal 
functions but without a constructor. Could start adding them places.
Here, I have opted to not use it to properly initialize self.methods,
self.tags, etc.
'''

import logging
logger = logging.getLogger(__name__)

class TestNodeSession(NodeSession):
    def __init__(self, config: NodeConfig, comm: MockComm) -> None:
        super().__init__(config, comm)
        self.config = config
    
    def __enter__(self): 
        return self
    
    def __exit__(self, *exc):
        self._comm.__exit__(*exc)

    def _verify_node_collision(self):
        # we don't need to verify collisions because we are not actually connecting
        pass

    def connect_to_remote(self, key: str, on_state: StateCallback | None = None, on_meta: MetaCallback | None = None, on_liveliness_change: LivelinessCallback | None = None, tag_data_callbacks: dict[str, TagDataCallback] = {}) -> RemoteConnection:
        if (self._comm.is_online(self.config.ks)):
            self._comm.update_liveliness(NodeKeySpace.from_user_key(key), True)
            super().connect_to_remote(key, on_state, on_meta, on_liveliness_change, tag_data_callbacks)
        else:
            logger.warning("Error: Session has been closed")

    def disconnect_from_remote(self, key: str):
        self._comm.update_liveliness(NodeKeySpace.from_user_key(key), False)
        super().disconnect_from_remote(key)
    
    # This call is exactly the same as remote, just on the session itself and not remote
    def call_method_iter(self, path: str, timeout: float | None = None, **kwargs) -> Iterator[MethodReply]:
        # connect to self
        remote = self.connect_to_remote(self.ks.user_key)
        return remote.call_method_iter(path, timeout, **kwargs)
