import gedge
import time

from constants import *
from gedge.node.method_response import ResponseType

config = gedge.NodeConfig("test/method/calls/caller")

with gedge.connect(config, "192.168.4.60") as session:
    remote = session.connect_to_remote("test/method/calls/callee") 

    print("FIRST METHOD CALL")
    r = list(remote.call_method_iter("call/method", name="super long things that should get rejected by func", speed=100))
    for response in r:
        print(response.code, response.props, response.body)
    assert len(r) >= 1
    assert r[-1].code == 401
    assert r[-1].type == ResponseType.ERR

    print("\n\nSECOND METHOD CALL")
    r = list(remote.call_method_iter("call/method", name="hello world", speed=200))
    for response in r:
        print(response.code, response.props, response.body)
    assert len(r) >= 1
    assert r[-1].code == 400
    assert r[-1].type == ResponseType.ERR
    assert r[-1].body[BODY_KEY] == 200

    print("\n\nTHIRD METHOD CALL")
    r = list(remote.call_method_iter("call/method", name="hello world", speed=40))
    assert len(r) >= 1
    assert r[0].code == 202
    assert r[0].type == gedge.ResponseType.INFO
    assert r[-1].code == 200
    assert r[-1].type == gedge.ResponseType.OK
    assert r[-1].body[BODY_KEY] == 40
    for response in r:
        print(response.code, response.props, response.body)

    print("\n\nFOURTH METHOD CALL")
    r = list(remote.call_method_iter("call/method", name=EXCEPTION, speed=40))
    assert len(r) >= 1
    assert r[0].code == gedge.CALLBACK_ERR
    assert r[0].type == gedge.ResponseType.ERR
    assert r[0].body["reason"] == EXCEPTION
    for response in r:
        print(response.code, response.props, response.body)

    print("\n\nFIFTH METHOD CALL")
    try:
        responses5 = remote.call_method_iter("call/method", name=EXCEPTION)
        for response in responses5:
            print(response.code, response.props, response.body)
    except:
        print(f"Incorrect parameters")

    print("\n\nSIXTH METHOD CALL")
    try:
        responses6 = remote.call_method_iter("call/method", 100, name="hello world", speed=40)
        for response in responses6:
            print(response.code, response.props, response.body)
    except TimeoutError:
        print("Timeout")

    print("\n\nSEVENTH METHOD CALL")
    r = list(remote.call_method_iter("call/method", name="hello world", speed=HANDLER_NEVER_RETURNS_SPEED))
    assert len(r) >= 1
    assert r[-1].code == gedge.CALLBACK_ERR
    assert r[-1].type == gedge.ResponseType.ERR
    for response in r:
        print(response.code, response.props, response.body)

    print("\n\nEIGHTH METHOD CALL")
    r = list(remote.call_method_iter("call/method", name="hello world", speed=HANDLER_RETURNS_OK_TWICE))
    assert len(r) >= 1
    assert r[-1].code == gedge.OK
    assert r[-1].type == gedge.ResponseType.OK
    for response in r:
        print(response.code, response.props, response.body)