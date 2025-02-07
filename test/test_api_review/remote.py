import gedge
import time

import zenoh

def on_tag(sample: zenoh.Sample):
    print(f"got sample, {sample.payload}")

def on_write(sample: zenoh.Sample):
    print(f"got write, {sample.payload}")

THIS_NODE = "BuildScale/Robots/RemoteApiTest"
config = gedge.NodeConfig(THIS_NODE)
config.add_tag("test/tag", int, props={"units": "in"})
config.add_tag("test/tag/2", float)

with gedge.connect(config) as session:
    session._comm.session.declare_subscriber("BuildScale/Robots/NODE/RemoteApiTest/TAGS/DATA/test/tag", on_tag)
    session._comm.session.declare_subscriber("BuildScale/Robots/NODE/RemoteApiTest/TAGS/WRITE/test/tag", on_write)
    bind = session.tag_bind("test/tag")

    i = 0
    while i < 15:
        time.sleep(1)
        bind.value = i
        i += 1

