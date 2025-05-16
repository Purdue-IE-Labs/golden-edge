import pathlib
import random
import sys
import time
import gedge

here = pathlib.Path(__file__).parent
config = gedge.NodeConfig.from_json5(str(here / "node.json5"))

if len(sys.argv) > 1:
    ip_address = sys.argv[1]
else:
    ip_address = "localhost"

with gedge.connect(config, ip_address) as session:
    while True:
        time.sleep(1)
        session.update_tag("base/tag/1", random.randint(0, 12))
        time.sleep(1)
        session.update_tag("base/tag/2", random.random())