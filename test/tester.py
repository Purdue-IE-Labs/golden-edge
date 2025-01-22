import zenoh
import pathlib
from gedge import EdgeNode
from gedge.proto import DataType, TagData, Meta, State

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


with zenoh.open(zenoh.Config()) as session:
    session.declare_subscriber("**/META/**", meta_listener)
    session.declare_subscriber("**/TAG/**", tag_listener)
    session.declare_subscriber("**/STATE/**", state_listener)

    prefix = ""
    with open(prefix_path) as f:
        prefix = f.read().strip()
    print(f"'{prefix}'")

    e = EdgeNode(prefix, "test")
    e.add_tag("my_tag", DataType.INT, properties={"units": "in"}) 
    with e.connect() as session:
        print("connected")
