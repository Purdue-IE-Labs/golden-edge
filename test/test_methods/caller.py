import gedge
import time

'''
The only purpose of this is to simulate an error occurring in the method handler that the client defines
'''
EXCEPTION = 'EXCEPTION'

config = gedge.NodeConfig("test/method/calls/caller")

def my_callback(reply):
    print("Callback received:")

    if reply.error:
        print(f"Error: {reply.code}, {reply.error}")
    else:
        print(f"Success: {reply.code}, {reply.props}, {reply.body}")

with gedge.connect(config, "192.168.4.60") as session:
    remote = session.connect_to_remote("test/method/calls/callee") 

    print("FIRST METHOD CALL")
    responses = remote.call_method_iter("call/method", 5000, name="super long things that should get rejected by func", speed=100)
    for response in responses:
        print(response.code, response.props, response.body)

    time.sleep(1)

    print("\n\nSECOND METHOD CALL")
    responses2 = remote.call_method_iter("call/method", name="hello world", speed=200)
    for response in responses2:
        print(response.code, response.props, response.body)

    print("\n\nTHIRD METHOD CALL")
    responses3 = remote.call_method_iter("call/method", name="hello world", speed=40)
    for response in responses3:
        print(response.code, response.props, response.body)

    print("\n\nFOURTH METHOD CALL")
    responses4 = remote.call_method_iter("call/method", name=EXCEPTION, speed=40)
    for response in responses4:
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
        responses6 = remote.call_method_iter("call/method", _timeout=100, name="hello world", speed=40)
        for response in responses6:
            print(response.code, response.props, response.body)
    except TimeoutError:
        print("Timeout")

    print("\n\nSEVENTH METHOD CALL")
    responses7 = remote.call_method_iter("call/method", name="hello world", speed=345)
    for response in responses7:
        print(response.code, response.props, response.body)

    print("\n\nEIGHTH METHOD CALL")
    responses8 = remote.call_method_iter("call/method", name="hello world", speed=456)
    for response in responses8:
        print(response.code, response.props, response.body)