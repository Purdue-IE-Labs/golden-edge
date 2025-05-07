import random
import sys
import time
from typing import Any
import gedge
import pathlib

def on_tag_write(query: gedge.TagWriteQuery):
    value = query.value
    if value > 10:
        query.reply_err()
    query.reply_ok()

# we specify the path to the directory that holds all locally pulled models
# this allows us to use these models
here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

here = pathlib.Path(__file__).parent
config = gedge.NodeConfig.from_json5(str(here / "tag_binds.json5"))
config.add_tag_write_handler("base/tag/1", handler=on_tag_write)

if len(sys.argv) > 1:
    ip_address = sys.argv[1]
else:
    ip_address = "192.168.4.60"

with gedge.connect(config, ip_address) as session:
    # this gives us a variable that is essentially a stand-in
    # for this tag
    bind = session.tag_bind("base/tag/2")
    while True:
        time.sleep(1)
        # this will update the tag, calling session.update_tag(...)
        # under the hood
        bind.value = random.random()