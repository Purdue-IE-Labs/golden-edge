import pathlib
import gedge

def handler(query: gedge.TagWriteQuery) -> None:
    if query.value > 10:
        query.reply(400)
        return
    query.reply(200)

here = pathlib.Path(__file__).parent
config = gedge.NodeConfig.from_json5(str(here / "writee.json5"))
config.add_tag_write_handler("tag/write", handler=handler)

with gedge.connect(config, "tcp/localhost:7447") as session:
    session.print_nodes_on_network(only_online=True)
    while True:
        pass