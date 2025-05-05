import gedge
import pathlib

here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

config = gedge.NodeConfig("test/data/models/caller")
with gedge.connect(config, "192.168.4.60") as session:
    remote = session.connect_to_remote("test/data/models/tags")
    r = remote.write_tag("tag/1/tag", 12)
    print(r)