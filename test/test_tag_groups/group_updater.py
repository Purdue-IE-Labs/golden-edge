import pathlib
import time
from typing import Any
import gedge

def tag_write(query: gedge.TagWriteQuery):
    query.reply_ok()

def base_tag_write(query: gedge.TagWriteQuery):
    value: int = query.value # type: ignore
    
    if value == 10:
        return
    if value == 20:
        query.reply_ok()
    if value == 30:
        query.reply_err()
    if value == 40:
        # invalid use of API
        query.reply_err(200)

    query.reply_ok(200)

here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

here = pathlib.Path(__file__).parent / "gedge_config.json5"
config = gedge.NodeConfig.from_json5(str(here))
config.add_tag_write_handler("tag/1/tag", tag_write)
config.add_tag_write_handler("base_tag", base_tag_write)
config.add_tag_write_handler("tag/1/tag/2/baz", tag_write)

with gedge.connect(config, "192.168.4.60") as session:
    print(session.tag_config.all_writable_tags())
    print(session.tag_config.all_groups())
    while True:
        time.sleep(1)
        session.update_group({
            "tag/1/tag": 12,
            "base_tag": 123
        })
        # session.update_tag("tag/1/tag/2/foo/bar/baz", 10.23)
