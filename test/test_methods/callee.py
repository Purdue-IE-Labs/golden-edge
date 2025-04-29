import gedge
import pathlib
import time

EXCEPTION = 'EXCEPTION'

def handler(query: gedge.MethodQuery):
    name = query.params["name"]
    speed = query.params["speed"]

    if speed == 456:
        # try to return ok twice
        query.reply_ok()
        query.reply_ok()
    if speed == 345:
        # simulate a control flow that never returns anything
        return 
    if name == EXCEPTION:
        raise ValueError("exception thrown in method handler")

    if len(name) > 30:
        query.reply_err(401)
    if speed < 0 or speed > 100:
        query.reply_err(400, body={"res1": speed})
    query.reply_ok(200, body={"res1": speed})

here = pathlib.Path(__file__).parent
config = gedge.NodeConfig.from_json5(str(here / "callee.json5"))
config.add_method_handler("call/method", handler=handler)

with gedge.connect(config, "192.168.4.60") as session:
    while True:
        pass