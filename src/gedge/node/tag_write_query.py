from __future__ import annotations

from dataclasses import dataclass
from gedge.py_proto.tag_config import Tag, TagConfig

from typing import Any, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from gedge.comm.comm import Comm
    from gedge.node.gtypes import TagValue

import logging

from gedge.node import codes
logger = logging.getLogger(__name__)

@dataclass
class TagWriteQuery:
    key_expr: str
    value: Any
    tag_config: Tag
    _reply: Callable[[int, dict[str, TagValue]], None]

    def reply(self, code: int, body: dict[str, TagValue]):
        # this is to allow the node to have access to this later
        self.code = code
        self.body = body

        logger.info(f"Replying to tag value write with code {code}")
        # if code not in {i.code for i in self.tag_config.responses} and code not in {codes.TAG_ERROR}:
        #     raise ValueError(f"invalid response code {code}")
        self._reply(code, body)
