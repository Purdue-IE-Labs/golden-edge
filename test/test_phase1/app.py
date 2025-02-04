import gedge
from gedge.proto import State, Meta, TagData
import time

# STATE
def on_state(name: str, key_expr: str, state: State):
    print(f"app got state message: {state.online}")

# META
def on_meta(name: str, key_expr: str, meta: Meta):
    print(f"app got meta message: {meta}")

# TAG VALUE
def on_joint_position(name: str, key_expr: str, data: list[float]):
    print(f"from node {name}, key expr: {key_expr}, got joint position: {data}")

# TAG VALUE
def on_project_running(name: str, key_expr: str, data: bool):
    print(f"from node {name}, key expr: {key_expr}, got project running change: {data}")

# LIVELINESS
def on_liveliness_change(name: str, is_online: bool):
    print(f"name {name} is_online: {is_online}")

key_prefix = "BuildAtScale/Robots/Arms"
config = gedge.AppConfig(key_prefix, "app")
with gedge.connect(config) as session:
    session.print_nodes_on_network(session.config.key_prefix, only_online=False)

    # tag data callbacks can be added in two ways: in the connect_to_node argument and in its own function
    name = "Daisy"
    session.connect_to_node(key_prefix, name, tag_data_callbacks={
        "tm12/joint_pos": on_joint_position,
        "tm11/joint_pos": on_joint_position,
    })
    session.add_state_callback(key_prefix, name, on_state)
    session.add_meta_callback(key_prefix, name, on_meta)
    session.add_liveliness_callback(key_prefix, name, on_liveliness_change)
    session.add_tag_data_callback("BuildAtScale/Robots/Arms", "Daisy", "project/is_running", on_project_running)
    while True:
        time.sleep(1)

session = gedge.connect(config)
# do stuff
session.close()