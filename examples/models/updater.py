import pathlib
import random
import time
from typing import Any
import gedge
import sys

here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

if len(sys.argv) > 1:
    ip_address = sys.argv[1]
else:
    ip_address = "localhost"

def tag_write(query: gedge.TagWriteQuery):
    query.reply_ok(100)

def handler(query: gedge.MethodQuery):
    model: dict[str, Any] = query.params["model"]
    speed: int = query.params["speed"]

    print(f"got model: {model}")

    if speed < 0 or speed > 100:
        query.reply_err(400, body={"res1": speed})
    
    if speed == 10:
        response_model = {
            "tag": 12,
            "tag/2": {
                "foo/bar/baz": 10.4
            }
        }
        query.reply_ok(202, body={"res1": response_model})

    # passing a model back as a body item
    # importantly, this need not include all items of a 
    # model, it only needs to include a subset of them
    response_model = {
        "foo/bar/baz": 10.4
    }
    query.reply_ok(200, body={"res1": response_model})

here = pathlib.Path(__file__).parent / "models.json5"
config = gedge.NodeConfig.from_json5(str(here))
config.add_method_handler("call/method", handler)

with gedge.connect(config, ip_address) as session:
    while True:
        time.sleep(1)

        # tag/1 is of type "bar", and "bar" has item "foo/bar/baz", 
        # which is of type "float"
        session.update_tag("tag/1/foo/bar/baz/qux", random.random())