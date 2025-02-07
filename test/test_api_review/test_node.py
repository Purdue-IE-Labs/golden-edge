import gedge
import time

import zenoh

from typing import Any

import gedge.proto

def on_tag(sample: zenoh.Sample):
    print(f"got sample, {sample.payload}")

def on_tag_data(key: str, data: Any):
    print(f"got tag data from remote on key {key}: {data}")

def on_state(key: str, state: gedge.proto.State):
    print(f"got state on key {key}: {state}")

THIS_NODE = "BuildScale/Robots/ApiTest"
REMOTE_NODE = "BuildScale/Robots/RemoteApiTest"
config = gedge.NodeConfig(THIS_NODE)
config.add_tag("test/tag", int, props={"units": "in"})
config.add_tag("test/tag/2", float)

with gedge.connect(config) as session:
    session._comm.session.declare_subscriber("BuildScale/Robots/NODE/ApiTest/TAGS/DATA/test/tag", on_tag)
    bind = session.tag_bind("test/tag")
    bind.value = 10
    print(bind.value)
    session.update_tag("test/tag", 12)
    time.sleep(0.1)
    print(bind.value)

    remote_node = session.connect_to_remote(REMOTE_NODE)
    # remote_node.add_tag_data_callback("test/tag", on_tag_data)
    bind = remote_node.tag_bind("test/tag")
    remote_node.add_state_callback(on_state)
    i = 0
    while True:
        print(bind.value)
        time.sleep(1)
        i += 1
        if i == 10:
            bind.value = 1223
