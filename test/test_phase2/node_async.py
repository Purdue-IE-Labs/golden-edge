import asyncio
import time
import gedge

async def main():
    THIS_NODE = "BuildScale/Robots/RemoteApiTest"
    REMOTE_NODE = "BuildScale/Robots/ApiTest"

    config = gedge.NodeConfig(THIS_NODE)
    with gedge.connect(config) as session:
        remote = session.connect_to_remote(REMOTE_NODE)

        time.sleep(1)

        code, _ = await remote.write_tag_async("test/tag", 8) 
        print("wrote tag asyncly")
        print(f"got code: {code}")

asyncio.run(main())