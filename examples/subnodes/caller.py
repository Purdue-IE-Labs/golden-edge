from typing import Any
import gedge
import pathlib
import sys

def on_tag_data(key_expr: str, value: Any):
    print(f"key_expr={key_expr}, value={value}")

# we specify the path to the directory that holds all locally pulled models
# this allows us to use these models
here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

if len(sys.argv) > 1:
    ip_address = sys.argv[1]
else:
    ip_address = "localhost"

config = gedge.NodeConfig("gedge/examples/subnodes/caller")

with gedge.connect(config, ip_address) as session:
    remote = session.connect_to_remote("gedge/examples/subnodes/callee")

    print("ROOT METHOD CALL")
    responses = remote.call_method_iter("root/method", name="joe", speed=10)
    for r in responses:
        print(r)
    print()
    
    """
    Similar to callee.py, we can 'subnode' the remote connection to 
    get access to the tags, methods, and subnodes defined on a subnode 
    of the remote node
    """
    print("LEVEL 1 TAG WRITE")
    remote_level_1a = remote.subnode("level-1a")
    response = remote_level_1a.write_tag("tag/write", value=9)
    print(response)
    print()

    """
    Similar to callee.py, we can use the '/' syntax to dig straight down 
    to the exact subnode that we want to call methods on
    """
    print("LEVEL 2 METHOD CALL")
    remote_level_1b_level_2a = remote.subnode("level-1b/level-2a")
    responses = remote_level_1b_level_2a.call_method_iter("inner/method")
    for r in responses:
        print(r)
    print()
    
    print("TAG DATA CALLBACKS")
    remote_level_1a.add_tag_data_callback("model/tag/qux", on_tag_data)
    remote_level_1b_level_2a.add_tag_data_callback("inner/tag", on_tag_data)
    
    session.sleep()
