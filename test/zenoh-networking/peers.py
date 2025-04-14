import json5
import gedge

config = gedge.NodeConfig("test/zenoh/discovery/Grayson")
with gedge.connect(config, "tcp/localhost:7447") as session:
    session.print_nodes_on_network(only_online=True)

import zenoh

zenoh.try_init_log_from_env()

config = json5.dumps({
    "mode": "peer",
    # "connect": {
    #     "endpoints": ["tcp/localhost:7447"]
    # }
})
config = zenoh.Config().from_json5(config)
with zenoh.open(config) as session:
    peers = session.info.peers_zid()
    routers = session.info.routers_zid()
    my_id = session.info.zid()
    print(peers)
    print(routers)
    print(my_id)
    while True:
        pass