import pathlib
import random
import sys
import gedge

def on_data(key_expr: str, value: gedge.TagBaseValue):
    print(f"key_expr={key_expr}, value={value}")

config = gedge.NodeConfig("gedge/examples/models/caller")

if len(sys.argv) > 1:
    ip_address = sys.argv[1]
else:
    ip_address = "localhost"

here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

with gedge.connect(config, ip_address) as session:
    remote = session.connect_to_remote("gedge/examples/models/updater") 

    # passing a model into a method
    # importantly, you don't need to set every item of the model
    # in this example, item "tag/2" of model "qux" is not included
    qux = {
        "foo/bar/baz/qux": random.random(),
        "tag": random.randint(0, 10),
    }
    responses = remote.call_method_iter("call/method", model=qux, speed=100)
    for response in responses:
        print(response.code, response.props, response.body)

    remote.add_tag_data_callback("tag/1/foo/bar/baz/qux", on_data)
    session.sleep()