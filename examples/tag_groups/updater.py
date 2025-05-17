import pathlib
import random
import sys
import time
from typing import Any
import gedge

def tag_write(query: gedge.TagWriteQuery):
    query.reply_ok()

def base_tag_write(query: gedge.TagWriteQuery):
    assert isinstance(query.value, int)
    value = query.value
    
    if value == 10:
        return
    if value == 20:
        query.reply_ok()
    if value == 30:
        query.reply_err()
    if value == 40:
        # invalid use of API
        query.reply_err(200)

    query.reply_ok(200)

here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

if len(sys.argv) > 1:
    ip_address = sys.argv[1]
else:
    ip_address = "localhost"

here = pathlib.Path(__file__).parent / "tag_groups.json5"
config = gedge.NodeConfig.from_json5(str(here))
config.add_tag_write_handler("tag/1/tag", tag_write)
config.add_tag_write_handler("tag/3", base_tag_write)
config.add_tag_write_handler("tag/1/tag/2/baz", tag_write)

with gedge.connect(config, ip_address) as session:
    while True:
        time.sleep(1)

        # members of the group need not have the same base type
        session.update_group({
            "tag/1/tag": random.randint(0, 10),
            "tag/2/qux": random.randint(0, 100),
            "tag/3": random.randint(0, 1000),
            "tag/4": random.random(),
        })
        time.sleep(1)

        # we can also individually update any of the 
        # tags in a group, but they will go on 
        # key expression ".../NODE/.../GROUPS/..."
        session.update_tag("tag/1/tag", 1123123)
