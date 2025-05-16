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
    ip_address = "localhost"

with gedge.connect(config, ip_address) as session:
    # this gives us a variable that is essentially a stand-in
    # for this tag
    bind = session.tag_bind("base/tag/2")

    time.sleep(1)

    # this will update the tag, calling session.update_tag(...)
    # under the hood
    first_value = random.random()
    bind.value = first_value

    time.sleep(1)

    # if we update the tag value via "session.update_tag(...)",
    # the tag will still be updated via the tag bind
    second_value = random.random()
    session.update_tag("base/tag/2", second_value)
    assert bind.value == second_value

    time.sleep(20)

    # we can close the tag bind and render it inactive
    # this will cancel all associated subscriptions
    bind.close()