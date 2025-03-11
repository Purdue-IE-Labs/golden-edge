import gedge

config = gedge.NodeConfig("test/tag/writes/writer")

with gedge.connect(config, "tcp/localhost:7447") as session:
    remote = session.connect_to_remote("test/tag/writes/writee")

    print("FIRST TAG WRITE")
    reply = remote.write_tag("tag/write", value=20)
    print(f"got reply: {reply}\n")
    print(f"response props: {reply.props}")

    print("\n\nSECOND TAG WRITE")
    reply = remote.write_tag("tag/write", value=5)
    print(f"got reply: {reply}\n")
    print(f"response props: {reply.props}")