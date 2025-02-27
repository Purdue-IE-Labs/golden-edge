from dataclasses import dataclass
from gedge.edge.gtypes import TagValue

@dataclass
class Reply:
    key_expr: str
    code: int
    body: dict[str, TagValue]
    error: str
