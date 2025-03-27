import gedge
import pathlib

here = pathlib.Path(__file__).parent / "test_node.json5"
config = gedge.NodeConfig.from_json5(str(here))

with gedge.connect(config, "192.168.4.60") as session:
    print(session.config.tags["properties/test"].props.to_value()['arr'])
    print(session.config.tags["properties/test"].props.to_value()['arr_int'])
