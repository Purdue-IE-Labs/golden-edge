import gedge
import pathlib

from gedge.edge.gtypes import TagValue

def method_handler(query: gedge.Query):
    print("got query")
    query.reply(400)

def tag_write_handler(key_expr: str, value: TagValue) -> int:
    return 200


path = pathlib.Path(__file__).parents[1] / "gedge_config.json5"
config = gedge.NodeConfig.from_json5(str(path))

config.add_method_handler("start/project", method_handler)
config.add_method_handler("another/method", method_handler)
config.add_tag_write_handler("my/writable/tag", tag_write_handler)

with gedge.connect(config) as session:
    print("connected")
    print(session.ks.user_key)
    print(session.methods)
    print(session.tag_config)