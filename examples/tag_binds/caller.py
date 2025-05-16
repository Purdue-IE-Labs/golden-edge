import pathlib
import random
import sys
import time
import gedge

# we specify the path to the directory that holds all locally pulled models
# this allows us to use these models
here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

config = gedge.NodeConfig("gedge/examples/tag_binds/writer")

if len(sys.argv) > 1:
    ip_address = sys.argv[1]
else:
    ip_address = "localhost"

with gedge.connect(config, ip_address) as session:
    remote = session.connect_to_remote("gedge/examples/tag_binds/updater") 
    bind = remote.tag_bind("base/tag/1")

    time.sleep(1)
    
    # this will write to the tag on the remote node, 
    # calling remote.write_tag(...) under the hood
    # the implication of this is that we never see the 
    # return codes or types when writing to this tag
    # we consider it a success if we get a ResponseType.OK,
    # and otherwise this line will throw an error
    new_value = random.randint(0, 5)
    bind.value = new_value
    assert bind.value == new_value

    time.sleep(1)
    
    # based on updater.py's tag write handler, this will throw an error
    try:
        bind.value = 12
    except Exception as e:
        print(e)
    