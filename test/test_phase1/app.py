import gedge
from gedge.proto import State, Meta, TagData
import time

def on_state(state: State):
    print(f"app got state message: {state.online}")

def on_meta(meta: Meta):
    print(f"app got meta message: {meta}")

def on_tag_data(data: TagData):
    print(f"app got tag data: {data}")

def on_joint_position(data: list[float]):
    print(f"got joint position: {data}")

def on_project_running(data: bool):
    print(f"got project running change: {data}")

def on_liveliness_change(is_online: bool, name: str):
    print(f"name {name} is_online: {is_online}")

config = gedge.AppConfig("BuildAtScale/Robots/Arms", "app")
with gedge.connect(config) as session:
    session: gedge.AppSession

    session.connect_to_node("Daisy", on_state, on_meta, on_liveliness_change, tag_data_callbacks={
        "tm12/joint_pos": on_joint_position,
        "project/is_running": on_project_running,
    })

    while True:
        time.sleep(1)