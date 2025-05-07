import pathlib
import time
import gedge
from gedge.node.gtypes import TagValue

def on_group_data(key_expr: str, value: TagValue):
    print(f"GROUP: key_expr: {key_expr}, value {value}")

def on_tag_data(key_expr: str, value: TagValue):
    print(f"TAG: key_expr: {key_expr}, value {value}")

here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

config = gedge.NodeConfig("test/tag/groups/subscriber")
with gedge.connect(config, "192.168.4.60") as session:
    remote = session.connect_to_remote("test/tag/groups")
    remote.add_tag_group_callback("test_group", on_group_data)
    remote.add_tag_data_callback("tag/1/tag", on_tag_data)
    while True:
        time.sleep(1)