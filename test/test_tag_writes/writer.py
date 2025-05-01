import gedge

# Define some sample callback functions
def state_callback(str, state):
    print(f"State changed: {state} for {str}")

def meta_callback(meta_data):
    print(f"Received metadata: {meta_data}")

def liveliness_callback(str, liveliness_status):
    print(f"Liveliness status: {liveliness_status}, {str}")

def tag_data_callback(str, value):
    
    print("CALLBACK YIPPEEEE")
    print(f"Tag data at {str}: {value}")

config = gedge.NodeConfig("test/tag/writes/writer")

with gedge.connect(config, "192.168.4.60") as session:
    remote = session.connect_to_remote(
        key="test/tag/writes/writee",
        on_state=state_callback,
        on_meta=meta_callback,
        on_liveliness_change=liveliness_callback,
        tag_data_callbacks={
            "tag/write": tag_data_callback
        })
    #remote = session.connect_to_remote("test/tag/writes/writee")

    print("FIRST TAG WRITE")
    reply = remote.write_tag("tag/write", value=20)
    print(f"got reply: {reply}\n")
    print(f"response props: {reply.props}")

    print("\n\nSECOND TAG WRITE")
    reply = remote.write_tag("tag/write", value=5)
    print(f"got reply: {reply}\n")
    print(f"response props: {reply.props}")
    
    while True:
        pass