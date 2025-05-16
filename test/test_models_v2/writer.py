import gedge
import pathlib

from gedge.node import codes
from gedge.node.method_response import ResponseType
from gedge.node.reply import Response

num_response = 1
def print_response(response: Response):
    global num_response
    print(f"\n\nRESPONSE {num_response}")
    print(response.code, response.type, response.body, response.props)
    print("\n")
    num_response += 1

here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

config = gedge.NodeConfig("test/data/models/caller")
with gedge.connect(config, "192.168.4.60") as session:
    remote = session.connect_to_remote("test/data/models/tags")

    # HAPPY PATH - 1
    r = remote.write_tag("tag/1/tag", 12)
    print_response(r)
    assert r.type == ResponseType.OK

    # TAG THAT IS NOT WRITABLE, THROWS AN EXCEPTION
    try:
        r = remote.write_tag("tag/2/baz", True)
    except Exception as e:
        print(f"EXCEPTION: {e}")

    # DEEPLY NESTED TAG - 2
    r = remote.write_tag("tag/1/tag/2/baz", True)
    print_response(r)
    assert r.type == ResponseType.OK

    # TEST NOT RETURNING ANY CODE IN TAG WRITE HANDLER - 3
    r = remote.write_tag("base_tag", 10)
    print_response(r)
    assert r.code == codes.CALLBACK_ERR
    assert r.type == ResponseType.ERR

    # TEST GENERIC REPLY OK - 4
    r = remote.write_tag("base_tag", 20)
    print_response(r)
    assert r.code == codes.OK
    assert r.type == ResponseType.OK

    # TEST GENERIC REPLY ERR - 5
    r = remote.write_tag("base_tag", 30)
    print_response(r)
    assert r.code == codes.ERR
    assert r.type == ResponseType.ERR

    # TEST INVALID API USE - 6
    r = remote.write_tag("base_tag", 40)
    print_response(r)
    assert r.code == codes.CALLBACK_ERR
    assert r.type == ResponseType.ERR