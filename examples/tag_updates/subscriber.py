import pathlib
import random
import sys
import time
from typing import Any
import gedge


if len(sys.argv) > 1:
    ip_address = sys.argv[1]
else:
    ip_address = "localhost"
    
here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

config = gedge.NodeConfig("gedge/examples/tag_updates/subscriber")

def handler(key_expr: str, value: Any):
    print(f"Received {key_expr} with value {value}")

with gedge.connect(config, ip_address) as session:
    remote = session.connect_to_remote("gedge/examples/tag_updates/updater")

    # similar to updater.py, we cannot add a callback to a model type, only 
    # to a base type
    remote.add_tag_data_callback("base/tag", handler)
    remote.add_tag_data_callback("model/tag/baz", handler)

    # this does the exact same thing as the lines above
    # remote = session.connect_to_remote("gedge/examples/tag_updates/updater", tag_data_callbacks={
    #     "base/tag": handler,
    #     "model/tag/baz": handler
    # })
    while True:
        pass