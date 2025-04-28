import gedge
from gedge.node.gtypes import TagValue

def on_data(key_expr: str, value: TagValue):
    print(key_expr, value)

config = gedge.NodeConfig("data/model/object/subscriber")

with gedge.connect(config, "192.168.4.60") as session:
    remote = session.connect_to_remote("test/data/models/tags")
    remote.add_tag_data_callback("tag/1", on_data)
    while True:
        pass