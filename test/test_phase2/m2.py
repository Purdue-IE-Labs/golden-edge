import gedge
from typing import Any
import time

def on_reply(code: int, d: dict[str, Any], error: str):
    print(f"receied {code}, {error}, {d}")

config = gedge.NodeConfig("test/m2")
with gedge.connect(config) as session:
    remote = session.connect_to_remote("test/m1")
    remote.call_method("method", on_reply, param1=1, param2=[2.0])
    time.sleep(60)