import time
import gedge
import pathlib

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
    time.sleep(10)
    query.reply(200, body={"res1": speed})

here = pathlib.Path(__file__).parent
config = gedge.NodeConfig.from_json5(str(here / "callee.json5"))
config.add_method_handler("call/method", handler=handler)

'''
session = gedge.mock_connect(config)

OR

with gedge.mock_connect(config) as session:
    ...
'''

node = gedge.mock_connect(config)
print("FIRST METHOD CALL")
responses = node.call_method_iter("call/method", name="super long things that should get rejected by func", speed=100)
for response in responses:
    print(response.code, response.props, response.body)

print("\n\nSECOND METHOD CALL")
responses2 = node.call_method_iter("call/method", name="hello world", speed=200)
for response in responses2:
    print(response.code, response.props, response.body)

print("\n\nTHIRD METHOD CALL")
responses3 = node.call_method_iter("call/method", name="hello world", speed=40)
for response in responses3:
    if response.error:
        print(response.code, response.error)
    else:
        print(response.code, response.props, response.body['res1'].value, response.body['res1'].props)

print("\n\nFOURTH METHOD CALL")
responses4 = node.call_method_iter("call/method", name=EXCEPTION, speed=40)
for response in responses4:
    if response.error:
        print(response.code, response.error)
    else:
        print(response.code, response.props, response.body)
