import gedge
import pathlib
from constants import *

def handler(query: gedge.MethodQuery):
    name = query.params[NAME_PARAM]
    speed = query.params[SPEED_PARAM]

    if speed == HANDLER_RETURNS_OK_TWICE:
        # try to return ok twice
        query.reply_ok()
        query.reply_ok()
    if speed == HANDLER_NEVER_RETURNS_SPEED:
        # simulate a control flow that never returns anything
        return 
    if name == EXCEPTION:
        raise ValueError(EXCEPTION)

    query.reply_info(202)

    if len(name) > 30:
        query.reply_err(401)
    if speed < 0 or speed > 100:
        query.reply_err(400, body={BODY_KEY: speed})
    query.reply_ok(200, body={BODY_KEY: speed})

here = pathlib.Path(__file__).parent
config = gedge.NodeConfig.from_json5(str(here / "callee.json5"))
config.add_method_handler("call/method", handler=handler)

with gedge.connect(config, "192.168.4.60") as session:
    while True:
        pass