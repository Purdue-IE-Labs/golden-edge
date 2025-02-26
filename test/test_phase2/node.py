import time
import gedge

THIS_NODE = "BuildScale/Robots/RemoteApiTest"
REMOTE_NODE = "BuildScale/Robots/ApiTest"

config = gedge.NodeConfig(THIS_NODE)
with gedge.connect(config) as session:
    remote = session.connect_to_remote(REMOTE_NODE)

    time.sleep(1)

    code, error = remote.write_tag("test/tag", 8)

    time.sleep(1)

    bind = remote.tag_bind("test/tag")
    bind.value = 5
