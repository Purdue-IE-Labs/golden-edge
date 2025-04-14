from typing import Any
import gedge

def handler(key_expr: str, value: Any):
    print(value)

config = gedge.NodeConfig("test/tag/updates/subscriber")

with gedge.connect(config, "192.168.4.60") as session:
    remote = session.connect_to_remote("test/tag/updates/updater")
    remote.add_tag_data_callback("my/tag/1", handler)
    while True:
        pass