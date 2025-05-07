from __future__ import annotations

from queue import Queue, Empty
import time
from gedge.node.gtypes import TagBaseValue, TagValue
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
if TYPE_CHECKING:
    from gedge.node.gtypes import TagDataCallback, StateCallback, MetaCallback, LivelinessCallback, MethodReplyCallback
    from gedge.node.subnode import RemoteSubConnection

import logging
logger = logging.getLogger(__name__)

class RemoteConnection:
    def __init__(self, ks: NodeKeySpace, comm: Comm, node_id: str, on_close: Callable[[str], None] | None = None):
        self._comm = comm 
        self.key = ks.user_key
        self.ks = ks
        self.on_close = on_close

        self.node_id = node_id

        '''
        TODO: perhaps we should subscribe to this node's meta message, in which case all the following utility variables (self.tags, self.methods, self.responses) 
        would need to react to that (i.e. be properties)
        '''
        self.meta = self._comm.pull_meta_message(ks)
        self.tag_config = TagConfig.from_proto(self.meta.tags)
        methods: list[MethodConfig] = [MethodConfig.from_proto(m) for m in self.meta.methods]
        self.methods = {m.path: m for m in methods}
        self.responses: dict[str, dict[int, ResponseConfig]] = {key:{r.code:r for r in value.responses} for key, value in self.methods.items()}
        self.models: dict[str, DataModelConfig] = {DataModelRef(m.path, m.version).full_path: DataModelConfig.from_proto(m) for m in self.meta.models}

        from gedge.node.subnode import SubnodeConfig
        subnodes: list[SubnodeConfig] = [SubnodeConfig.from_proto(s, self.ks) for s in self.meta.subnodes]
        self.subnodes: dict[str, SubnodeConfig] = {s.name: s for s in subnodes}

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
    
    def add_tag_data_callback(self, path: str, on_tag_data: TagDataCallback) -> None:
        '''
        Adds the passed TagDataCallback to the current node on the passed path

        Arguments:
            path (str): The path of the node recieving the new tag data callback
            on_tag_data (TagDataCallbacks): The new TagDataCallback being added

        Returns:
            None
        '''
        if not self.tag_config.is_valid_path(path):
            raise TagLookupError(path, self.ks.name)
        
        # group = self.tag_config.get_group(path)
        # if group:
        #     self.add_tag_group_callback(group, on_tag_data)
        #     return
        self._comm.tag_data_subscriber(self.ks, path, on_tag_data, self.tag_config)
    
    def add_tag_group_callback(self, group_path: str, on_group_data: TagDataCallback) -> None:
        if not self.tag_config.is_valid_group_path(group_path):
            raise LookupError(group_path)
        
        self._comm.group_data_subscriber(self.ks, group_path, on_group_data, self.tag_config)

    def add_state_callback(self, on_state: StateCallback) -> None:
        '''
        Adds the passed StateCallback to the current node

        Arguments:
            on_state (StateCallback): The handler being added to the node

        Returns:
            None
        '''
        self._comm.state_subscriber(self.ks, on_state)

    def add_meta_callback(self, on_meta: MetaCallback) -> None:
        '''
        Adds the passed MetaCallback to the current node

        Arguments:
            on_meta (MetaCallback): The handler being added to the node

        Returns:
            None
        '''
        self._comm.meta_subscriber(self.ks, on_meta)

    def add_liveliness_callback(self, on_liveliness_change: LivelinessCallback) -> None:
        '''
        Adds the passed LivelinessCallback to the current node

        Arguments:
            on_liveliness_change (LivelinessCallback): The handler being added to the node

        Returns:
            None
        '''
        self._comm.liveliness_subscriber(self.ks, on_liveliness_change)

    def tag_binds(self, paths: list[str]) -> list[TagBind]:
        '''
        Binds all of the tags in the passed paths to the current node

        Note: To understand how an individual tag_bind functions look at the function tag_bind

        Arguments:
            paths (list[str]): The list of paths for the tags

        Returns:
            list[TagBind]: The list of the newly bound tags
        '''
        return [self.tag_bind(path) for path in paths]

    def tag_bind(self, path: str, value: Any = None) -> TagBind:
        '''
        Binds the tag at the passed path to the current node

        Note: This allows users to declare a tag_bind on a tag that belongs to a remote node and then treat the tag as if it were their own.

        Example Implementation:
            remote = session.connect_to_remote(...)
            my_tag = remote.tag_bind("my/tag")
            my_tag.value = False
            my_tag.value = True

        Arguments:
            path (str): The path of the tag
            value (Any | Optional): The value for the TagBind

        Returns:
            TagBind: The new TagBind
        '''
        if path not in self.tag_config:
            raise TagLookupError(path, self.ks.name)
        tag = self.tag_config[path]
        bind = TagBind(self.ks, self._comm, tag, value, self._write_tag)
        return bind
    
    def subnode(self, name: str) -> RemoteSubConnection:
        '''
        Creates a RemoteSubConnection for the subnode that has the passed name

        Arguments:
            name (str): The name of subnode

        Returns:
            RemoteSubConnection: The new connection for the subnode
        '''
        from gedge.node.subnode import RemoteSubConnection
        def on_close(key):
            pass
        if "/" in name:
            curr_node = self
            subnodes = name.split("/")
            for s in subnodes:
                if s not in curr_node.subnodes:
                    raise ValueError(f"No subnode {s}")
                curr_node = curr_node.subnodes[s]
            # we inherit comm
            # different uuid or same?
            from gedge.node.subnode import SubnodeConfig
            assert isinstance(curr_node, SubnodeConfig)
            r = RemoteSubConnection(name, curr_node.ks, curr_node, self._comm, self.node_id, on_close)
            return r

        if name not in self.subnodes:
            raise ValueError(f"No subnode {name}") 
        curr_node = self.subnodes[name]
        logger.debug(self._comm.session.is_closed())
        r = RemoteSubConnection(name, curr_node.ks, curr_node, self._comm, self.node_id, on_close)
        return r

    def _write_tag(self, path: str, value: TagBaseValue, tag: Tag) -> Response:
        '''
        Writes the passed value to the tag at the passed path and returns the reply

        Arguments:
            path (str): The path of the tag being written to
            value (Any): The value being written to the tag

        Returns:
            TagWriteReply: The reply from the tag write
        '''
        logger.info(f"Remote node '{self.key}' received write request at path '{path}' with value '{value}'")
        config = self.tag_config.get_config(path)
        base_type = config.get_base_type()
        if not base_type:
            raise ValueError("cannot write to model type")
        response = self._comm.write_tag(self.ks, path, BaseData.from_value(value, base_type))
        code = response.code

        responses, _ = self.tag_config.all_writable_tags()[path]
        config = get_response_config(code, responses)

        body: dict[str, TagValue] = dict_proto_to_value(dict(response.body), config.body)
        props = props_to_json5(config.props)

        reply = Response(self.ks.tag_write_path(path), code, config.type, body, props)
        return reply

    def write_tag(self, path: str, value: Any) -> Response:
        '''
        Writes the passed value to the tag at the passed path and returns the reply

        Example Implementation:
            remote = session.connect_to_remote(...)
            reply = remote.write_tag("example/path", value=n)
            print(f"got reply: {reply}")
            print(f"reply props: {reply.props}")

        Arguments:
            path (str): The path of the tag being written to
            value (Any): The value being written to the tag

        Returns:
            TagWriteReply: The reply from the tag write
        '''
        if path not in self.tag_config.all_writable_tags():
            raise LookupError(f"tag {path} not writable")

        tag = self.tag_config.get_tag(path)
        return self._write_tag(path, value, tag)

    async def write_tag_async(self, path: str, value: Any) -> Response:
        '''
        Writes the passed value to the tag at the passed path and returns the reply

        Note: As of now this functions is implemented the same as write_tag

        Example Implementation:
            remote = session.connect_to_remote(...)
            reply = await remote.write_tag_async("example/path", param=n)
            print(f"got reply: {reply}")
            print(f"reply props: {reply.props}")

        Arguments:
            path (str): The path of the tag being written to
            value (Any): The value being written to the tag

        Returns:
            TagWriteReply: The reply from the tag write
        '''
        if path not in self.tag_config.all_writable_tags():
            raise LookupError(f"tag {path} not writable")

        tag = self.tag_config.get_tag(path)
        return self._write_tag(path, value, tag)
    
    def call_method(self, _path: str, _on_reply: MethodReplyCallback, **kwargs) -> None:
        '''
        Registers the passed MethodReplyCallback and then calls the method at the passed path and all replies get routed to the passed Callback

        Example Implementation:
            def my_callback(reply):
                if reply.error:
                    print(f"Error: {reply.code}, {rply.error}")
                else:
                    print(f"Success: {reply.code}, {reply.props}, reply.body}")
            
            remote = session.connect_to_remote(...)
            remote.call_method("example/path", my_callback, param0=x, param1=y)
        
        Arguments:
            _path (str): The path of the method
            on_reply (MethodReplyCallback): The MethodReplyCallback for the replies
            kwargs (dict[str, Any]): Parameters passsed to the method

        Returns:
            None
        '''
        if _path not in self.methods:
            raise MethodLookupError(_path, self.ks.name)
        
        method = self.methods[_path]
        params = method.params_py_to_proto(kwargs.items()) # type: ignore
        logger.info(f"Querying method of node {self.ks.name} at path {_path} with params {params.keys()}")
        self._comm.query_method(self.ks, _path, self.node_id, params, _on_reply, self.methods[_path])
    
    # CAUTION: because this is a generator, just calling it (session.call_method_iter(...)) will do nothing,
    # it must be iterated upon to actually run
    # timeout in milliseconds
    def call_method_iter(self, _path: str, _timeout: float | None = None, **kwargs) -> Iterator[Response]:
        '''
        Calls the method along the passed path with an optional timeout

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
            Iterator[MethodReply]: The generator corresponding to the replies from the method
        '''

        if _timeout:
            _timeout /= 1000

        if _path not in self.methods:
            raise MethodLookupError(_path, self.ks.name)

        method = self.methods[_path]
        for param in method.params:
            if param.path not in kwargs:
                raise LookupError(f"Parameter {param} defined in config but not included in method call for method {method.path}")
        
        params: dict[str, proto.DataItem] = dict_value_to_proto(kwargs, method.params)
        replies: Queue[Response] = Queue()
        def _on_reply(reply: Response) -> None:
            replies.put(reply)

        logger.info(f"Querying method of node {self.ks.name} at path {_path} with params {params.keys()}")
        start = time.time()
        key_expr = self._comm.query_method(self.ks, _path, self.node_id, params, _on_reply, self.methods[_path])
        while True:
            try:
                elapsed = (time.time() - start)
                if _timeout and elapsed >= _timeout:
                    # timeout exceeded, we need an item ASAP
                    res = replies.get(block=False)
                elif _timeout:
                    # we can wait timeout - elapsed more seconds
                    res = replies.get(block=True, timeout=(_timeout - elapsed))
                else:
                    # if no timeout, we block forever
                    res = replies.get(block=True)
            except Empty:
                key_expr = method_response_from_call(key_expr)
                self._comm.cancel_subscription(key_expr)
                raise TimeoutError(f"Timeout of method call at path {method.path} exceeded")
            yield res
            if codes.is_final_method_response(res):
                logger.debug("Ending call_method_iter iterator")
                return