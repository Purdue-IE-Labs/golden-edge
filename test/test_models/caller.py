import random
import gedge

config = gedge.NodeConfig("data/model/object/caller")

with gedge.connect(config, "192.168.4.60") as session:
    remote = session.connect_to_remote("test/data/models/tags") 

    print("FIRST METHOD CALL")
    qux = {
        "foo/bar/baz/qux": random.random(),
        "tag": random.randint(0, 10),
    }
    responses = remote.call_method_iter("call/method", model=qux, speed=100)
    for response in responses:
        print(response.code, response.props, response.body)