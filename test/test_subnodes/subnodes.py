import gedge
import pathlib

def vice_tag_write_handler(query: gedge.TagWriteQuery) -> None:
    print("vice tag write handler")
    if query.value > 10:
        query.reply_err(400)
        return
    query.reply_ok(200)

def mill_method_handler(query: gedge.MethodQuery) -> None:
    print("mill method handler")
    query.reply_err(401)

def inner_subnode_method_handler(query: gedge.MethodQuery) -> None:
    print("inner subnode method handler")
    query.reply_ok(200)

here = pathlib.Path(__file__).parent / "gedge.json5"
node = gedge.NodeConfig.from_json5(str(here))
node.add_method_handler("call/method", handler=mill_method_handler)

subnode = node.subnode("Vice")
subnode.add_tag_write_handler("tag/write", handler=vice_tag_write_handler)

subsubnode = node.subnode("Siemens828D/inner-subnode")
subsubnode.add_method_handler("inner/method", handler=inner_subnode_method_handler)

with gedge.connect(node, "tcp/192.168.4.60:7447") as session:
    inner = session.subnode("Siemens828D/inner-subnode")
    inner.update_tag("siemens/inner/tag", value=12.3)

    vice = session.subnode("Vice")
    vice.update_tag("tag/write", value=239)

    siemens = session.subnode("Siemens828D")
    session.update_tag("root/tag", [1, 2])

    inner = session.subnode("Siemens828D").subnode("inner-subnode")
    inner.update_tag("siemens/inner/tag", value=123.4)

    while True:
        pass