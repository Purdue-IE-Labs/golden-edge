import gedge
from typing import Any
import time

def on_reply(reply: gedge.Reply):
    code, body, error = reply.code, reply.body, reply.error
    print(f"received code {code}")

with gedge.connect(gedge.NodeConfig("BuildAtScale/Robots/Methods/Demo/Caller"), "tcp/localhost:7447") as session:
    remote = session.connect_to_remote("BuildAtScale/Robots/Methods/Demo/Callee")
    print("first method call")
    responses1 = remote.call_method_iter("start/project", name="testing2", speed=90)
    for response in responses1:
        print(response)
        if response.code == 202:
            break
    print("second method call")
    responses2 = remote.call_method_iter("start/project", name="testing", speed=80)
    for response in responses2:
        print(response)
    
    # we can collect responses that we didn't see earlier because we said "break" before iterating through all responses
    for response in responses1:
        print(response)

    time.sleep(60)