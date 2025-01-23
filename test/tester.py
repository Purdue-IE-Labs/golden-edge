from typing import Any
import zenoh
import pathlib
from gedge import EdgeNodeConfig, EdgeNodeSession
from gedge.proto import DataType, TagData, Meta, State
import threading

prefix_path = pathlib.Path(__file__).parent / "prefix.txt"

def meta_listener(sample: zenoh.Sample):
    meta = Meta()
    meta.ParseFromString(sample.payload.to_bytes())
    print(f"meta: \n\tkey_expr: {sample.key_expr}, \n\tpayload: {sample.payload.to_bytes()}, \n\tmeta: {meta}")

def tag_listener(sample: zenoh.Sample):
    tag_data = TagData()
    tag_data.ParseFromString(sample.payload.to_bytes())
    print(f"tag: \n\tkey_expr: {sample.key_expr}, \n\ttag_data: {tag_data}")

def state_listener(sample: zenoh.Sample):
    state = State()
    state.ParseFromString(sample.payload.to_bytes())
    print(f"state: \n\tkey_expr: {sample.key_expr}, \n\tstate: {state}")

def send_message_periodic(tag_name: str, value: Any):
    t = threading.Timer(0.5, send_message_periodic, args=[tag_name, value])
    t.start()
    session.write_tag(tag_name, value)

with zenoh.open(zenoh.Config()) as session:
    session.declare_subscriber("**/META/**", meta_listener)
    session.declare_subscriber("**/TAGS/**", tag_listener)
    session.declare_subscriber("**/STATE/**", state_listener)

    prefix = ""
    with open(prefix_path) as f:
        prefix = f.read().strip()
    print(f"'{prefix}'")

    e = EdgeNodeConfig(prefix, "test")
    e.add_tag("my_tag", list[int], properties={"units": "in"}, key_expr="this/is/my_tag/1") 
    with e.connect() as session:
        print("connected")
        send_message_periodic("my_tag", [0, 1, 3, 4, 5])
        import time
        time.sleep(1000)
