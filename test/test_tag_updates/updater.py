import random
import time
import gedge
import json5


config_str = json5.dumps({
    "key": "test/tag/updates/updater",
    "tags": [
        {
            "path": "my/tag/1",
            "base_type": "int",
        },
        {
            "path": "my/tag/2",
            "base_type": "float",
        }
    ]
})

config = gedge.NodeConfig.from_json5_str(config_str)
with gedge.connect(config, "192.168.4.60") as session:
    while True:
        session.update_tag("my/tag/1", random.randint(0, 9))
        session.update_tag("my/tag/2", random.random())
        time.sleep(1)
