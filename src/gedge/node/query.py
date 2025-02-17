from typing import Any

import zenoh

from gedge.comm.comm import Comm
from gedge.comm.keys import NodeKeySpace
from gedge.edge.tag_data import TagData, from_tag_data, convert
from gedge.node.response import Response
from gedge import proto

class Query:
    def __init__(self, ks: NodeKeySpace, path: str, comm: Comm, query: zenoh.Query, parameters: dict[str, Any] = {}, responses: list[Response] = []):
        self.path = path
        self._ks = ks
        self._comm = comm
        self._query = query
        self.parameters: dict[str, Any] = parameters
        self._responses = responses
    
    def reply(self, code: int, body: dict[str, Any], error: str = ""):
        new_body: dict[str, proto.TagData] = {}
        for key, value in body.items():
            response = [i for i in self._responses if i.code == code][0]
            data_type = response.body[key]
            new_body[key] = convert(value, data_type.type)
        r = proto.ResponseData(code=code, error=error, body=new_body)
        b = self._comm.serialize(r)
        self._query.reply(key_expr=self._ks.method_path(self.path), payload=b)