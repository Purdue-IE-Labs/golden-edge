import zenoh
import time
import json

config = {
    "mode": "client"
}
json5 = json.dumps(config)


def handle(sample: zenoh.Sample) -> None:
    print(f"got sample: {sample.attachment}, {sample.express}, {sample.congestion_control} {sample.encoding} {sample.timestamp}")

with zenoh.open(zenoh.Config()) as session:
    print(session.zid())
    session.declare_subscriber("zenoh-networking/1", handle)
    time.sleep(5)