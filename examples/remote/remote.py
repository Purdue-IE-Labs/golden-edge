import pathlib
import sys
import time
from typing import Any
import gedge

def on_tag_data1(key_expr: str, data: Any):
    assert isinstance(data, int)
    print(f"got tag data on key_expr {key_expr} with value {data}")

def on_tag_data2(key_expr: str, data: Any):
    assert isinstance(data, float)
    print(f"got tag data on key_expr {key_expr} with value {data}")

def on_state(key_expr: str, state: gedge.State):
    print(f"received state {state}")

def on_meta(key_expr: str, meta: gedge.Meta):
    print(f"received meta {meta}")

def on_liveliness(key_expr: str, is_online: bool):
    print(f"received liveliness change: is_online={is_online}")

config = gedge.NodeConfig("gedge/examples/remote/remote")

if len(sys.argv) > 1:
    ip_address = sys.argv[1]
else:
    ip_address = "localhost"

with gedge.connect(config, ip_address) as session:
    remote = session.connect_to_remote("gedge/examples/remote/node", on_state, on_meta, on_liveliness, tag_data_callbacks={
        "base/tag/1": on_tag_data1,
        "base/tag/2": on_tag_data2,
    })
    time.sleep(10)
    remote.close()

    time.sleep(5)

    remote = session.connect_to_remote("gedge/examples/remote/node")
    remote.add_state_callback(on_state)
    remote.add_tag_data_callback("base/tag/1", on_tag_data1)
    time.sleep(10)
