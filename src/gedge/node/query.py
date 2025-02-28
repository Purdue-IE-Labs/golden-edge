from typing import Any

import zenoh

from gedge.comm import keys
from gedge.comm.comm import Comm
from gedge.comm.keys import NodeKeySpace
from gedge.edge.tag_data import TagData
from gedge.node import codes
from gedge.node.response import Response
from gedge import proto

import logging
logger = logging.getLogger(__name__)

class MethodQuery:
    def __init__(self, key_expr: str, comm: Comm, params: dict[str, Any] = {}, responses: list[Response] = []):
        self._comm = comm
        self._responses = responses

        self.params = params
        self.key_expr = key_expr
    
    def reply(self, code: int, body: dict[str, Any] = {}, error: str = ""):
        logger.info(f"Replying to method with code {code} on path {self.key_expr}")
        if code not in {i.code for i in self._responses} and code not in {codes.DONE, codes.METHOD_ERROR, codes.TAG_ERROR}:
            raise ValueError(f"invalid repsonse code {code}")
        new_body: dict[str, proto.TagData] = {}
        for key, value in body.items():
            response = [i for i in self._responses if i.code == code][0]
            data_type = response.body[key]
            new_body[key] = TagData.py_to_proto(value, data_type)
        r = proto.ResponseData(code=code, error=error, body=new_body)
        b = self._comm.serialize(r)
        self._comm.session.put(key_expr=self.key_expr, payload=b)