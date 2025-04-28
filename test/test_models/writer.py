import gedge
from gedge.node.gtypes import TagValue

config = gedge.NodeConfig("data/model/object/writer")

with gedge.connect(config, "192.168.4.60") as session:
    remote = session.connect_to_remote("test/data/models/tags")
    result = remote.write_tag("tag/2", value={
        "tag10": 100.89
    })
    print(result.code)