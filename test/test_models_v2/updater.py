import pathlib
import time
from typing import Any
import gedge

def tag_write(query: gedge.TagWriteQuery):
    query.reply_ok()

def base_tag_write(query: gedge.TagWriteQuery):
    value: int = query.value # type: ignore
    
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

def handler(query: gedge.MethodQuery):
    print(query.params)
    model: dict[str, Any] = query.params["model"]
    speed: int = query.params["speed"]

    rand_int = model.get("tag", -1)

    print(f"got model: {model}")

    if speed < 0 or speed > 100:
        query.reply_err(400, body={"res1": speed})
    
    if rand_int == 999:
        # TEST SENDING BACK A PARTIAL MODEL
        response_model = {
            "foo/bar/baz": 112.1
        }
        query.reply_ok(200, body={"res1": response_model})
    
    if rand_int == 555:
        # TEST SENDING BACK THE WRONG CODE
        # 400 is an ERR code but we pass reply ok
        query.reply_ok(400, body={"res1": 10})

    response_model = {
        "foo/bar/baz": 10.4,
        "baz": True,
        "qux": rand_int
    }
    query.reply_ok(200, body={"res1": response_model})

def handler2(query: gedge.MethodQuery):
    model = query.params["model"]
    speed = query.params["speed"]

    if speed == 50:
        # TESTING IF CALLER STILL GETS AN ERR CODE BACK
        return
    if speed == 100:
        query.reply_ok(200)
    if speed == 150:
        # TESTING IF ERR IS STILL SENT AFTER SOME INFOs
        query.reply_info(202)
        time.sleep(1)
        query.reply_info(202)
        return
    
    query.reply_ok()

here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

here = pathlib.Path(__file__).parent / "gedge_config.json5"
config = gedge.NodeConfig.from_json5(str(here))
config.add_tag_write_handler("tag/1/tag", tag_write)
config.add_method_handler("call/method", handler)
config.add_method_handler("test/method/returns", handler2)
config.add_tag_write_handler("base_tag", base_tag_write)
config.add_tag_write_handler("tag/1/tag/2/baz", tag_write)

with gedge.connect(config, "192.168.4.60") as session:
    print(session.tag_config)
    while True:
        time.sleep(5)
        session.update_tag("tag/1/tag/2/foo/bar/baz", 10.23)