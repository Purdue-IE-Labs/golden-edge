import gedge
import pathlib

def handler(query: gedge.TagWriteQuery) -> None:
    if query.value > 10:
        query.reply(400)
        return
    query.reply(200)

here = pathlib.Path(__file__).parent / "gedge.json5"
node = gedge.NodeConfig.from_json5(str(here))

subnode = node.subnode("Vice")
subnode.add_tag_write_handler("tag/write", handler=handler)

with gedge.connect(node, "tcp/192.168.4.60:7447") as session:
    inner = session.subnode("Siemens828D/inner-subnode")
    print(inner)
    print(inner.tags, inner.methods)
    print(inner.ks)
    print(session.tags)
    print(session.ks)
    inner.update_tag("siemens/inner/tag", value=12.3)

    vice = session.subnode("Vice")
    vice.update_tag("tag/write", value=239)
    print(vice.ks)

    session.update_tag("root/tag", [1, 2])

    while True:
        pass