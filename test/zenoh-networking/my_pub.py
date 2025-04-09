import zenoh
import json
import time
import gedge
import gedge.proto

config = {
    "mode": "client"
}
json5 = json.dumps(config)

with zenoh.open(zenoh.Config.from_json5(json5)) as session:
    print(f"{session.zid()}")
    state = gedge.proto.State(online=True)
    session.put("zenoh-networking/1", payload=state.SerializeToString(), encoding=zenoh.Encoding.APPLICATION_PROTOBUF)
    time.sleep(5)
    session.put("stuff/META", bytes("hi", encoding="utf-8"))