# import gedge

# config = gedge.NodeConfig("gedge/examples/subnodes/caller")

# with gedge.connect(config, "tcp/192.168.4.60:7447") as session:
#     print(f"session: {session._comm.session.is_closed()}")
#     remote = session.connect_to_remote("test/subnode/Mill109")
#     responses = remote.call_method_iter("call/method", name="joe", speed=10)
#     for r in responses:
#         print(r)
    
#     vice = remote.subnode("Vice")
#     response = vice.write_tag("tag/write", value=9)
#     print(response)

#     inner = remote.subnode("Siemens828D/inner-subnode")
#     responses = inner.call_method_iter("inner/method")
#     for r in responses:
#         print(r)
