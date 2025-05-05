import pathlib
import random
import time
from typing import Any
import gedge

def tag_write(query: gedge.TagWriteQuery):
    query.reply(2000, {})

def handler(query: gedge.MethodQuery):
    model: dict[str, Any] = query.params["model"]
    speed: int = query.params["speed"]

    print(f"got model: {model}")

    if speed < 0 or speed > 100:
        query.reply_err(400, body={"res1": speed})

    response_model = {
        "tag10": 10.4
    }
    query.reply_ok(200, body={"res1": response_model})

here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

here = pathlib.Path(__file__).parent / "gedge_config.json5"
config = gedge.NodeConfig.from_json5(str(here))
config.add_tag_write_handler("tag/1/tag", tag_write)
config.add_method_handler("call/method", handler)

with gedge.connect(config, "192.168.4.60") as session:
    print(session.tag_config)
    while True:
        time.sleep(5)
        session.update_tag("tag/1/tag/2/foo/bar/baz", 10.23)