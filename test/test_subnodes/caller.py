import gedge

config = gedge.NodeConfig("test/subnode/Mill109/caller")

with gedge.connect(config, "tcp/192.168.4.60:7447") as session:
    print(f"session: {session._comm.session.is_closed()}")
    remote = session.connect_to_remote("test/subnode/Mill109")
    print(f"remote {remote._comm.session.is_closed()}")
    print()
    print(remote.ks)
    print()
    another_remote = remote.subnode("Vice")
    print()
    print(another_remote.ks)
    print()
    print(f"another_remote: {another_remote._comm.session.is_closed()}")
    result = another_remote.write_tag("tag/write", value=9)
    print(f"WROTE TAG: RESULT = {result}")
    final_remote = remote.subnode("Siemens828D/inner-subnode")
    print()
    print(final_remote.ks)
    print()
    print(f"final remote: {final_remote._comm.session.is_closed()}")

