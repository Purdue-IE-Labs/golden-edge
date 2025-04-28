import pathlib
import random
import time
import gedge

def tag_write(query: gedge.TagWriteQuery):
    raise NotImplementedError

def method_handler(query: gedge.MethodQuery):
    raise NotImplementedError

def test_all_models_are_not_embedded_in_meta_except_for_meta_dot_models():
    here = pathlib.Path(__file__).parents[2] / "models"
    gedge.use_models(str(here))

    here = pathlib.Path(__file__).parent / "gedge_config.json5"
    config = gedge.NodeConfig.from_json5(str(here))
    config.add_tag_write_handler("tag/2", tag_write)

    with gedge.connect(config, "192.168.4.60") as session:
        while True:
            time.sleep(1)
            session.update_tag("tag/1", {
                "foo/bar/baz/qux": random.random(),
                "tag": random.randint(0, 10),
            })