import gedge
import time

# quick demo to open, then close the vice

vise_tag = "isOpen"

def open_vice():
    print("opening vice")
    time.sleep(2)
    reply = remote.write_tag(vise_tag, True)
    print(reply.code)
    time.sleep(2)

def close_vice():
    print("closing vice")
    time.sleep(2)
    reply = remote.write_tag(vise_tag, False)
    print(reply.code)
    time.sleep(2)

config = gedge.NodeConfig("BuildScale/CNC/Vise/Caller")
with gedge.connect(config, "tcp/192.168.4.60:7447") as session:
    remote = session.connect_to_remote("BuildScale/CNC/Vise/Mill/Onlogic")
    vise = remote.subnode("Vise")
    reply = vise.write_tag(vise_tag, True)
    print(reply)
    time.sleep(5)
    reply = vise.write_tag(vise_tag, False)
    print(reply)