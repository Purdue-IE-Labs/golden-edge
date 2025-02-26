from typing import Any
import gedge

def write_handler(key: str, value: Any) -> int:
    print("write handler")

responses = [
    (200, True, {}),
    (400, False, {"description": "Bad Request"})
]
config = gedge.NodeConfig("BuildScale")

# OPTION 1
tag = config.add_tag("option1", int)

# OPTION 2
tag = config.add_writable_tag("option2", int, write_handler=write_handler, responses=responses)

with gedge.connect(config) as session:
    pass