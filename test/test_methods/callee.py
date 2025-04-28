import gedge
import pathlib
import time

EXCEPTION = 'EXCEPTION'

def handler(query: gedge.MethodQuery):
    name = query.params["name"]
    speed = query.params["speed"]
    if len(name) > 30:
        query.reply(401)
        return
    if speed < 0 or speed > 100:
        query.reply(400, body={"res1": speed})
        return
    if name == EXCEPTION:
        raise ValueError("exception thrown in method handler")
    query.reply(200, body={"res1": speed})
    time.sleep(2)
    query.reply(200, body={"res1": speed})

here = pathlib.Path(__file__).parent
config = gedge.NodeConfig.from_json5(str(here / "callee.json5"))
config.add_method_handler("call/method", handler=handler)

with gedge.connect(config, "192.168.4.60") as session:
    while True:
        pass