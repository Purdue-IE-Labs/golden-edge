import gedge
import json5
import time
import random

# takeaway is that zenoh seems to throw the callbacks onto another thread, so the delay in the handler does not affect the telemetry updates

IP_ADDRESS = "tcp/192.168.4.60:7447"

# if these timeouts are too large, the query will timeout because of zenoh configuration
def handler(query: gedge.TagWriteQuery):
    time.sleep(3)
    print("writing tag")
    time.sleep(3)
    print("wrote tag")
    time.sleep(3)
    query.reply_ok(200)

json_ = json5.dumps({
    "key": "testing/async",
    "tags": [
        {
            "path": "telemetry/tag",
            "base_type": "list[float]",
            "props": {
                "desc": "This tag should be updated once per second"
            },
        },
        {
            "path": "slow/writable/tag",
            "base_type": "int",
            "writable": True,
            "responses": {
                "code": 200,
                "type": "ok"
            },
        }
    ],
})

config = gedge.NodeConfig.from_json5_str(json_)
config.add_tag_write_handler("slow/writable/tag", handler=handler)

with gedge.connect(config, IP_ADDRESS) as session:
    while True:
        start = time.time()
        tag = [random.random() for _ in range(6)]
        session.update_tag("telemetry/tag", value=tag)
        time.sleep(1)
        print(f"Updated tag in {time.time() - start} seconds")
