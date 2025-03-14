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

from typing import TYPE_CHECKING, Iterator
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
    def __init__(self, config: NodeConfig) -> None:
        self.config = config
        self._comm = MockComm()
        self.methods = config.methods
        self.tags = config.tags
        self.ks = config.ks
        self.node_id = str(uuid.uuid4())
        self.responses: dict[str, dict[int, MethodResponse]] = {key:{r.code:r for r in value.responses} for key, value in self.methods.items()}
        logger.info(f"Registering tags and methods on node {self.config.key}")
        # for path in self.config.tags:
        #     # hook up tag write handlers
        #     tag = self.config.tags[path]
        #     if not tag.is_writable():
        #         continue
        #     assert tag.write_handler is not None
        #     self._comm.tag_queryable(self.ks, tag) 
        for path in self.config.methods:
            # hook up method handlers
            method = self.config.methods[path]
            self._comm.method_queryable(self.ks, method) 
    
    def __enter__(self): 
        return self
    
    def __exit__(self, *exc):
        self._comm.__exit__(*exc)

    def call_method_iter(self, path: str, timeout: int | None = None, **kwargs) -> Iterator[MethodReply]:
        # appparently, Generator[Reply, None, None] == Iterator[Reply]?
        # TODO: we can probably merge this with call_method eventually, but honestly we could just mangle our keyword args to be something like __path_ and _timeout__
        if path not in self.methods:
            raise MethodLookupError(path, self.ks.name)
        
        from queue import Queue, Empty
        
        method_query_id = str(uuid.uuid4())
        method = self.methods[path]
        params: dict[str, proto.TagData] = {}
        for key, value in kwargs.items():
            data_type = method.params[key].type
            params[key] = TagData.py_to_proto(value, data_type)
        
        replies: Queue[MethodReply] = Queue()
        def _on_reply(reply: MethodReply) -> None:
            replies.put(reply)

        logger.info(f"Querying method of node {self.ks.name} at path {path} with params {params.keys()}")
        # TODO: this function definition is longggggg, so many arguments
        self._comm.query_method(self.ks, path, self.node_id, method_query_id, params, _on_reply, self.responses[path])
        while True:
            try:
                res = replies.get(block=True, timeout=timeout)
            except Empty:
                logger.error(f"Timeout exceeded")
                return
            # Design decision: we don't give a codes.DONE to the iterator that the user uses
            # However, we do give them method and tag errors because they could be useful
            if res.code == codes.DONE:
                return
            yield res
            if res.code in {codes.METHOD_ERROR, codes.TAG_ERROR}:
                return


