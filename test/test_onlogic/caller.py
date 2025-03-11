import gedge
import time

config = gedge.NodeConfig("BuildScale/Lathe/Caller")
with gedge.connect(config, "tcp/192.168.4.60:7447") as session:
    remote = session.connect_to_remote("BuildScale/Lathe/Onlogic")
    time.sleep(1)
    print()
    print("opening vice")
    reply = remote.write_tag("vice/open", True)
    print(reply.code)
    print()
    time.sleep(5)
    print("closing vice")
    reply = remote.write_tag("vice/open", False)
    print(reply.code)