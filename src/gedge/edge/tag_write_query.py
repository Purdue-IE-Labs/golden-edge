from typing import Any
from dataclasses import dataclass

import zenoh

from gedge.comm.comm import Comm
from gedge.edge.tag import Tag
from gedge import proto

import logging

from gedge.node import codes
logger = logging.getLogger(__name__)

@dataclass
class TagWriteQuery:
    key_expr: str
    value: Any
    tag_config: Tag
    _query: zenoh.Query
    _comm: Comm

    def reply(self, code: int, error: str = ""):
        logger.info(f"Replying to tag value write with code {code}")
        if code not in {i.code for i in self.tag_config.responses} and code not in {codes.TAG_ERROR}:
            raise ValueError(f"invalid response code {code}")
        b = self._comm.serialize(proto.WriteResponseData(code=code, error=error))
        self._query.reply(key_expr=self.key_expr, payload=b)
