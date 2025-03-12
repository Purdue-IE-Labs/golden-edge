import gedge

config = gedge.NodeConfig("test/method/calls/caller")

with gedge.connect(config, "tcp/localhost:7447") as session:
    remote = session.connect_to_remote("test/method/calls/callee") 
    method_props = None
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
        print(response.code, response.props, response.body.get('res1', {}).get('value', None), response.body.get('res1', {}).get('props', None))