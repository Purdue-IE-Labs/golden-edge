import pathlib
import sys
import time
import gedge
from gedge.node.gtypes import TagBaseValue, TagGroupValue, TagValue

def on_group_data(key_expr: str, value: TagGroupValue):
    # 'value' will always be a dictionary of type dict[str, TagBaseValue]
    # it will include some subset (or all) of the tags in the group
    print(f"GROUP: key_expr: {key_expr}, value {value}")

def on_tag_data(key_expr: str, value: TagBaseValue):
    print(f"TAG: key_expr: {key_expr}, value {value}")

here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

if len(sys.argv) > 1:
    ip_address = sys.argv[1]
else:
    ip_address = "localhost"

config = gedge.NodeConfig("test/tag/groups/subscriber")
with gedge.connect(config, ip_address) as session:
    remote = session.connect_to_remote("test/tag/groups")

    # this callback will run anytime any subset of this group 
    # is updated
    # this callback will receive a dictionary mapping full tag paths to base values
    remote.add_tag_group_callback("test_group", on_group_data)

    # this callback will catch all updates to this tag, regardless of 
    # how they are initiated
    # if the node updates a group and changes this tag value, 
    # if the node just updates this tag alone,
    # in both cases this callback will be called
    # this callback will always receive a base value as parameter 'value'
    remote.add_tag_data_callback("tag/1/tag", on_tag_data)
    
    session.sleep()