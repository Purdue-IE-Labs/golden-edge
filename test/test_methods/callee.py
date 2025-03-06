import gedge
import pathlib

def handler(query: gedge.MethodQuery):
    name = query.params["name"]
    speed = query.params["speed"]
    if len(name) > 30:
        query.reply(401)
        return
    if speed < 0 or speed > 100:
        query.reply(400)
        return
    query.reply(200, body={
        "res1": speed
    })

here = pathlib.Path(__file__).parent
config = gedge.NodeConfig.from_json5(str(here / "callee.json5"))
config.add_method_handler("call/method", handler=handler)

with gedge.connect(config, "tcp/localhost:7447") as session:
    while True:
        pass