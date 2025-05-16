import pathlib
import sys
import time
from typing import Any
import gedge

# Specifying different handlers for different tags
def on_tag_data1(key_expr: str, data: Any):
    assert isinstance(data, int)
    print(f"got tag data on key_expr {key_expr} with value {data}")
def on_tag_data2(key_expr: str, data: Any):
    assert isinstance(data, float)
    print(f"got tag data on key_expr {key_expr} with value {data}")

'''
The distinction between state and liveliness mostly has to do with a 
graceful and an ungraceful shutdown. Liveliness is a zenoh construct 
that keeps record of a session and notifies us when it goes offline.
State is a golden-edge construct that the node itself controls (i.e. 
if the node knows it is shutting down or going offline, it sends state=false).
'''
def on_state(key_expr: str, state: gedge.State):
    print(f"received state {state}")
def on_liveliness(key_expr: str, is_online: bool):
    print(f"received liveliness change: is_online={is_online}")

'''
This will only fire when the node in question goes offline and then comes back online,
because only when a node comes online does it publish its meta. Thus, to get this 
handler to run. First start node.py, then start remote.py, then restart node.py
'''
def on_meta(key_expr: str, meta: gedge.Meta):
    print(f"received meta {meta}")

config = gedge.NodeConfig("gedge/examples/remote/remote")

if len(sys.argv) > 1:
    ip_address = sys.argv[1]
else:
    ip_address = "localhost"

with gedge.connect(config, ip_address) as session:
    # for debugging, you can print the nodes on the network to make sure you have the key right
    session.print_nodes_on_network(only_online=True)

    # This is the full version of connect_to_remote. Everything after the key is optional. However, 
    # we can specify callbacks for anytime the state, liveliness, meta, or tag values change on 
    # the remote node
    print("connecting to remote")
    remote = session.connect_to_remote("gedge/examples/remote/node", on_state, on_meta, on_liveliness, tag_data_callbacks={
        "base/tag/1": on_tag_data1,
        "base/tag/2": on_tag_data2,
    })
    time.sleep(10)
    # this cancels all subscriptions specified above
    remote.close()

    time.sleep(5)

    print("connecting to remote again")
    # we can also connect and then add callbacks after the fact
    remote = session.connect_to_remote("gedge/examples/remote/node")
    remote.add_state_callback(on_state)
    remote.add_tag_data_callback("base/tag/1", on_tag_data1)
    time.sleep(10)
