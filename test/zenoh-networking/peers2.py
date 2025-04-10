import json
import json5

import zenoh

zenoh.try_init_log_from_env()

key = "Build/Scale/Router/2"
config = json5.dumps({
    "mode": "peer",
    "transport": {
        "unicast": {
            "max_links": 10
        }
    }
})
import time
config = zenoh.Config().from_json5(config)
with zenoh.open(config) as session:
    time.sleep(10)
    peers = session.info.peers_zid()
    routers = session.info.routers_zid()
    my_id = session.info.zid()
    print(peers)
    print(f"routers: {routers}")
    print(my_id)
    for router_id in routers:
        res = session.get(f"@/{router_id}/router").recv()
        res = json.loads(res.result.payload.to_bytes())
        print(f"locators: {res['locators']}")
        print()
        print(f"metadata: {res['metadata']}")
        print()
        print(f"plugins: {res['plugins']}")
        print()
        print(f"sessions: {res['sessions']}")
        print()
        metadata = res['metadata']
        if key == metadata.get('key', ""):
            locators = res['locators']
            z_id = router_id
            break

print(f"connecting to zid {z_id} and locators {locators}")
config = json5.dumps({
    "mode": "client",
    "connect": {
        "endpoints": locators
    }
})
config = zenoh.Config.from_json5(config)
with zenoh.open(config) as session:
    print(session.info.routers_zid())
    while True:
        pass
