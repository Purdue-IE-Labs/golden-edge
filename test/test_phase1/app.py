import gedge
from gedge.proto import State, Meta, TagData
import time

def on_state(name: str, key_expr: str, state: State):
    print(f"app got state message: {state.online}")

def on_meta(name: str, key_expr: str, meta: Meta):
    print(f"app got meta message: {meta}")

def on_joint_position(name: str, key_expr: str, data: list[float]):
    print(f"from node {name}, key expr: {key_expr}, got joint position: {data}")

def on_project_running(name: str, key_expr: str, data: bool):
    print(f"from node {name}, key expr: {key_expr}, got project running change: {data}")

def on_liveliness_change(name: str, is_online: bool):
    print(f"name {name} is_online: {is_online}")

config = gedge.AppConfig("BuildAtScale/Robots/Arms", "app")
with gedge.connect(config) as session:
    session: gedge.AppSession

    # tag data callbacks can be added in two ways: in the connect_to_node argument and in its own function
    session.connect_to_node("Daisy", on_state, on_meta, on_liveliness_change, tag_data_callbacks={
        "tm12/joint_pos": on_joint_position,
    })
    session.add_tag_data_callback("Daisy", "project/is_running", on_project_running)

    while True:
        time.sleep(1)