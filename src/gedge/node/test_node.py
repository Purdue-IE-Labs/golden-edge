from __future__ import annotations

import uuid
from gedge import proto
from gedge.comm.mock_comm import MockCallback, MockComm, MockSample
from gedge.node import codes
from gedge.node.body import BodyData
from gedge.node.error import MethodLookupError
from gedge.node.gtypes import TagValue, ZenohCallback
from gedge.node.method_reply import MethodReply
from gedge.node.method_response import MethodResponse
from gedge.node.node import NodeConfig, NodeSession
from gedge.node.prop import Props
from gedge.node.query import MethodQuery
from gedge.node.remote import RemoteConfig
from gedge.node.tag_data import TagData

from typing import TYPE_CHECKING, Any, Iterator
if TYPE_CHECKING:
    from gedge.node.gtypes import MethodReplyCallback

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
    
    def __enter__(self): 
        return self
    
    def __exit__(self, *exc):
        self._comm.__exit__(*exc)

    def _verify_node_collision(self):
        # we don't need to verify collisions because we are not actually connecting
        pass

    # This call is exactly the same as remote, just on the session itself and not remote
    def call_method_iter(self, path: str, timeout: int | None = None, **kwargs) -> Iterator[MethodReply]:
        # connect to self
        remote = self.connect_to_remote(self.ks.user_key)
        return remote.call_method_iter(path, timeout, **kwargs)
