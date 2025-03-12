import gedge
import time

# quick demo to open, then close the vice

def open_vice():
    print("opening vice")
    time.sleep(2)
    reply = remote.write_tag("vice/open", True)
    print(reply.code)
    time.sleep(2)

def close_vice():
    print("closing vice")
    time.sleep(2)
    reply = remote.write_tag("vice/open", False)
    print(reply.code)
    time.sleep(2)

config = gedge.NodeConfig("BuildScale/Lathe/Caller")
with gedge.connect(config, "tcp/192.168.4.60:7447") as session:
    remote = session.connect_to_remote("BuildScale/Lathe/Onlogic")
    time.sleep(5)
    open_vice()
    close_vice()