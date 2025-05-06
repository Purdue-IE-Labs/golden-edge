import random
import gedge
import pathlib

here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

config = gedge.NodeConfig("test/data/models/caller")
with gedge.connect(config, "192.168.4.60") as session:
    remote = session.connect_to_remote("test/data/models/tags")
    r = remote.write_tag("tag/1/tag", 12)
    print(r)

    model = {
            "foo/bar/baz/qux": random.random(),
            "tag": random.randint(0, 10),
            "tag/2": {
                "foo/bar/baz": 10.23,
                "baz": True,
                "qux": 2,
            }
        }
    responses = remote.call_method_iter("call/method", model=model, speed=10)
    for r in responses:
        print(r)