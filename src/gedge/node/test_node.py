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
        self._comm.update_liveliness(self.config.ks, True)
        super().connect_to_remote(key, on_state, on_meta, on_liveliness_change, tag_data_callbacks)

    def disconnect_from_remote(self, key: str):
        self._comm.update_liveliness(self.config.ks, False)
        super().disconnect_from_remote(key)

    def _startup(self):
        '''
        The startup sequence of the NodeSession: Basic verification, hooks up TagWrite and Method handlers, and adds subnode callbacks

        Arguments:
            None
        
        Returns:
            None
        '''
        # logger.debug(f"Verifying node collisions...")
        # self._verify_node_collision()
        logger.info("Publishing node's meta")
        self._comm.send_meta(self.ks, self.meta)
        self.update_state(True)
        self.node_liveliness = self._comm.liveliness_token(self.ks)
        logger.info(f"Registering tags and methods on node {self.config.key}")
        for path in self.config.tags:
            # hook up tag write handlers
            tag = self.config.tags[path]
            if not tag.is_writable():
                continue
            assert tag.write_handler is not None
            self._comm.tag_queryable(self.ks, tag) 
        for path in self.config.methods:
            # hook up method handlers
            method = self.config.methods[path]
            self._comm.method_queryable(self.ks, method) 
        
        '''
        def add_subnode_callbacks(config: SubnodeConfig):
            for path in config.tags:
                tag = config.tags[path]
                if not tag.is_writable():
                    continue
                assert tag.write_handler is not None
                self._comm.tag_queryable(config.ks, tag) 
            for path in config.methods:
                method = config.methods[path]
                self._comm.method_queryable(config.ks, method) 
            for name in config.subnodes:
                subnode = config.subnodes[name]
                add_subnode_callbacks(subnode)
        
        for s in self.config.subnodes.values():
            add_subnode_callbacks(s)
        '''

    
    # This call is exactly the same as remote, just on the session itself and not remote
    def call_method_iter(self, path: str, timeout: float | None = None, **kwargs) -> Iterator[MethodReply]:
        # connect to self
        remote = self.connect_to_remote(self.ks.user_key)
        return remote.call_method_iter(path, timeout, **kwargs)
