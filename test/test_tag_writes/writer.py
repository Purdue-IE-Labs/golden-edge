import gedge

config = gedge.NodeConfig("test/tag/writes/writer")

with gedge.connect(config, "tcp/localhost:7447") as session:
    remote = session.connect_to_remote("test/tag/writes/writee")
    reply = remote.write_tag("tag/write", value=20)
    print(f"got reply: {reply}")
    print(f"tag props: {reply.tag_config.props}")
    print(f"response props: {reply.response_props}")
    reply = remote.write_tag("tag/write", value=5)
    print(f"got reply: {reply}")
    print(f"tag props: {reply.tag_config.props}")
    print(f"response props: {reply.response_props}")