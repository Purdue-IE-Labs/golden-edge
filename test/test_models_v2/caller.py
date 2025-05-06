import random
import gedge
import pathlib

from gedge.node.method_response import ResponseType
from gedge.node.reply import Response

num_response = 1
def print_responses(responses: list[Response]):
    global num_response
    print(f"\n\nREPONSE {num_response}")
    for r in responses:
        print(r.code, r.type, r.body, r.props)
    print("\n")
    num_response += 1

here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

config = gedge.NodeConfig("test/data/models/caller")
with gedge.connect(config, "192.168.4.60") as session:
    remote = session.connect_to_remote("test/data/models/tags")
    r = remote.write_tag("tag/1/tag", 12)
    print(r)

    model = {
        "tag": random.randint(0, 10),
        "tag/2": {
            "foo/bar/baz": 10.23,
            "baz": True,
            "qux": 2,
        }
    }

    # HAPPY PATH
    responses = list(remote.call_method_iter("call/method", model=model, speed=10))
    assert responses[0].type == ResponseType.OK
    print_responses(list(responses))

    # SHOULD RETURN AN ERR
    responses = list(remote.call_method_iter("call/method", model=model, speed=101))
    assert responses[0].type == ResponseType.ERR
    print_responses(list(responses))
    
    # TEST SENDING A PARTIAL MODEL
    partial_model = {
        "tag": random.randint(0, 300)
    }
    responses = list(remote.call_method_iter("call/method", model=partial_model, speed=10))
    assert responses[0].type == ResponseType.OK
    print_responses(list(responses))

    # TEST RECEIVING A PARTIAL MODEL (see updater.py for context)
    partial_model = {
        "tag": 999,
        "tag/2": {
            "foo/bar/baz": 10.23,
            "baz": True,
            "qux": 2,
        }
    }
    responses = list(remote.call_method_iter("call/method", model=partial_model, speed=10))
    assert responses[0].type == ResponseType.OK
    print_responses(list(responses))

    # TESTING IMPROPER USE OF API IN METHOD HANDLER (see updater.py)
    partial_model["tag"] = 555
    responses = list(remote.call_method_iter("call/method", model=partial_model, speed=10))
    assert responses[0].type == ResponseType.ERR
    print_responses(list(responses))

    # TESTING METHODS RETURNING OK OR ERR

    # TESTING WHEN A METHOD HANDLER DOES NOT RETURN ANY CODE (WE RECEIVE AN ERR HERE, which is intended)
    responses = list(remote.call_method_iter("test/method/returns", model=partial_model, speed=50))
    assert responses[0].type == ResponseType.ERR
    print_responses(list(responses))

    # TESTING REPLYING WITH AN OK CODE AND NOT RETURNING IN HANDLER (it should return for you)
    responses = list(remote.call_method_iter("test/method/returns", model=partial_model, speed=100))
    assert responses[0].type == ResponseType.OK
    print_responses(list(responses))

    # TESTING AN EMPTY REPLY_OK, it should default to default OK code
    responses = list(remote.call_method_iter("test/method/returns", model=partial_model, speed=1))
    assert responses[0].type == ResponseType.OK
    print_responses(list(responses))

    # TESTING SOME INFOs AND THEN ERR sent
    responses = list(remote.call_method_iter("test/method/returns", model=partial_model, speed=150))
    assert responses[-1].type == ResponseType.ERR
    print_responses(list(responses))