import gedge

'''
The only purpose of this is to simulate an error occurring in the method handler that the client defines
'''
EXCEPTION = 'EXCEPTION'

config = gedge.NodeConfig("test/method/calls/caller")

with gedge.connect(config, "tcp/localhost:7447") as session:
    remote = session.connect_to_remote("test/method/calls/callee") 

    print("FIRST METHOD CALL")
    responses = remote.call_method_iter("call/method", name="super long things that should get rejected by func", speed=100)
    for response in responses:
        print(response.code, response.props, response.body)

    print("\n\nSECOND METHOD CALL")
    responses2 = remote.call_method_iter("call/method", name="hello world", speed=200)
    for response in responses2:
        print(response.code, response.props, response.body)

    print("\n\nTHIRD METHOD CALL")
    responses3 = remote.call_method_iter("call/method", name="hello world", speed=40)
    for response in responses3:
        if response.error:
            print(response.code, response.error)
        else:
            print(response.code, response.props, response.body)

    print("\n\nFOURTH METHOD CALL")
    responses4 = remote.call_method_iter("call/method", name=EXCEPTION, speed=40)
    for response in responses4:
        if response.error:
            print(response.code, response.error)
        else:
            print(response.code, response.props, response.body)

    print("\n\nFIFTH METHOD CALL")
    try:
        responses5 = remote.call_method_iter("call/method", name=EXCEPTION)
        for response in responses5:
            if response.error:
                print(response.code, response.error)
            else:
                print(response.code, response.props, response.body)
    except:
        print(f"Incorrect parameters")

    print("\n\nSIXTH METHOD CALL")
    try:
        responses6 = remote.call_method_iter("call/method", timeout=100, name="hello world", speed=40)
        for response in responses6:
            if response.error:
                print(response.code, response.error)
            else:
                print(response.code, response.props, response.body)
    except TimeoutError:
        print("Timeout")