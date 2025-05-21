from __future__ import annotations

from queue import Queue, Empty
import time
from gedge.node.method import MethodConfig
from gedge.node.method_response import ResponseConfig, get_response_config
from gedge.node import codes
from gedge import proto
from gedge.node.error import MethodLookupError, SessionError, TagLookupError
from gedge.comm.comm import Comm
from gedge.node.tag_bind import TagBind
from gedge.comm.keys import *

from typing import Any, Iterator, Callable, TYPE_CHECKING

from gedge.node.reply import Response
from gedge.py_proto.base_data import BaseData
from gedge.py_proto.conversions import dict_proto_to_value, dict_value_to_proto, list_from_proto, props_to_json5
from gedge.py_proto.data_model import DataItem
from gedge.py_proto.data_model_config import DataModelConfig
from gedge.py_proto.data_model_ref import DataModelRef
from gedge.py_proto.tag_config import Tag, TagConfig
from gedge.node.remote import RemoteConnection
import threading

from fastapi import FastAPI, HTTPException # type: ignore
import uvicorn
if TYPE_CHECKING:
    from gedge.node.gtypes import TagDataCallback, StateCallback, MetaCallback, LivelinessCallback, MethodReplyCallback, TagValue, TagBaseValue, TagGroupDataCallback
    from gedge.node.subnode import RemoteSubConnection

import logging
logger = logging.getLogger(__name__)

app = FastAPI()
    

class VisualRemoteConnection(RemoteConnection):
    def __init__(self, ks: NodeKeySpace, comm: Comm, node_id: str, visual_path: str, on_close: Callable[[str], None] | None = None):
        self._comm = comm 
        self.key = ks.user_key
        self.ks = ks
        self.on_close = on_close

        self.node_id = node_id
        self.visual_path = visual_path
        
        self.latest_data = {
            "status": None,
            "value": None,
            "timestamp": None
        }

        from asyncio import Lock
        self._lock = Lock()

        print(f"Vis Path: {self.visual_path}")

        app.get(f"/{self.visual_path}/last_value")(self.get_last_value)

        '''
        TODO: perhaps we should subscribe to this node's meta message, in which case all the following utility variables (self.tags, self.methods, self.responses) 
        would need to react to that (i.e. be properties)
        '''
        if not self._comm.is_online(ks):
            raise ValueError(f"Node {ks.user_key} is not online, so it cannot be connected to!")
        self.meta = self._comm.pull_meta_message(ks)
        self.tag_config = self.meta.tags
        self.methods = self.meta.methods
        self.responses: dict[str, dict[int, ResponseConfig]] = {key:{r.code:r for r in value.responses} for key, value in self.methods.items()}
        self.models = self.meta.models

        from gedge.node.subnode import SubnodeConfig
        self.subnodes: dict[str, SubnodeConfig] = self.meta.subnodes

        self.binds: dict[str, TagBind] = {}

        self.server_thread = threading.Thread(target=self._start_server, daemon=True)
        self.server_thread.start()

    async def get_last_value(self):
        async with self._lock:
            if self.latest_data["value"] is None:
                raise HTTPException(status_code=404, detail="Nothing received yet")
            return self.latest_data.copy()
        
    def _start_server(self):
        uvicorn.run(app, host="0.0.0.0", port=8000)

    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        self.close()
        self._comm.__exit__(*exc)
    
    def close(self):
        '''
        Closes the current remote connection
        '''
        self._comm.close_remote(self.ks)
        if self.on_close is not None:
            self.on_close(self.key)
    
    # CAUTION: because this is a generator, just calling it (session.call_method_iter(...)) will do nothing,
    # it must be iterated upon to actually run
    # timeout in milliseconds
    def call_method_iter(self, _path: str, _param: str, _timeout: float | None = None, **kwargs) -> Iterator[Response]:
        '''
        Calls the method along the passed path with an optional timeout and visual elements included in Grafana

        Note: The returned object of this function is a generator, not a list

        Example Implementation:
            remote = session.connect_to_remote("example/path")
            responses = remote.call_method_iter("example/path", param0=x, param1=y)
            for response in responses:
                print(response.code, response.props, response.body)

        Arguments:
            path (str): The path to the method being called
            timeout (flout | None): Optional timeout in milliseconds
            kwargs (dict[str, Any]): Parameters passsed to the method

        Returns:
            Iterator[Response]: The generator corresponding to the replies from the method
        
        **Example**::

            remote = session.connect_to_visual_remote("test/method/calls/callee", "call/method", "speed", "test")

            r = list(remote.call_method_iter("call/method", name="super long things that should get rejected by func", speed=100))
            for response in r:
                print(response.code, response.props, response.body)
        '''
        
        data = self._check_param(_param, **kwargs)
        
        for response in super().call_method_iter(_path=_path, _timeout=_timeout, **kwargs):
            self._fill_data(data, response.code)
            yield response
            
    def _fill_data(self, value: Any, code: int):
        self.latest_data["status"] = code
        print(f"Updated Status: {code}")
        self.latest_data["value"] = value
        print(f"Updated Value: {value}")
        self.latest_data["timestamp"] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

    def _check_param(self, _param, **kwargs):
        if _param not in kwargs:
            raise LookupError(f"The passed args: {kwargs} don't match the passed visualization param: {self.param}")
        
        param_value = kwargs[_param]

        if isinstance(param_value, str):
            raise LookupError(f"The value of the visualization parameter cannot be properly displayed (must be number)")
        
        return param_value
        