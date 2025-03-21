import gedge

IP_ADDRESS = "tcp/192.168.4.60:7447"

config = gedge.NodeConfig("testing/async/caller")
with gedge.connect(config, IP_ADDRESS) as session:
    remote = session.connect_to_remote("testing/async")
    result = remote.write_tag("slow/writable/tag", value=10)
    print(result)