import gedge
from typing import Any
import time

def on_reply(code: int, body: dict[str, Any], error: str):
    print(f"received code {code}")

with gedge.connect(gedge.NodeConfig("BuildAtScale/Robots/Methods/Demo/Caller")) as session:
    remote = session.connect_to_remote("BuildAtScale/Robots/Methods/Demo/Callee")
    remote.call_method("start/project", on_reply, name="testing2", speed=90)
    time.sleep(60)