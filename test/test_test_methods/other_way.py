import gedge
import pathlib

from gedge.node.gtypes import TagValue
from gedge.node.method import Method

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

here = pathlib.Path(__file__).parent
config = gedge.NodeConfig.from_json5(str(here / "callee.json5"))

def get_props(method: Method, code: int) -> dict[str, TagValue]:
    response = [r for r in method.responses if r.code == code]
    if not response:
        return {}
    return response[0].props.to_value()

def _reply(code, body, error):
    print(code, body, error, get_props(config.methods["call/method"], code))

q = gedge.MethodQuery(key_expr="joe", params={}, _reply=_reply, _responses=config.methods["call/method"].responses)

print("\n\nFIRST METHOD CALL")
params = {
    "name": "super long things that should get rejected by func",
    "speed": 100,
}
q.params = params
handler(q)


print("\n\nSECOND METHOD CALL")
params = {
    "name": "hello world",
    "speed": 200,
}
q.params = params
handler(q)

print("\n\nTHIRD METHOD CALL")
params = {
    "name": "hello world",
    "speed": 40,
}
q.params = params
handler(q)

# TODO: THIS CASE DOESN'T WORK IN THIS FILE
print("\n\nFOURTH METHOD CALL")
params = {
    "name": EXCEPTION,
    "speed": 40,
}
q.params = params
handler(q)
