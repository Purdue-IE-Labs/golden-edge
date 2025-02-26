import zenoh
import time

def handle(query: zenoh.Query) -> zenoh.Reply:
    query.reply("hi/mom/1", payload=bytes("hi", encoding="utf-8"))
    time.sleep(10)
    query.reply("hi/mom/2", payload=bytes("hello", encoding="utf-8"))

def handle_reply(reply: zenoh.Reply):
    print(f"got reply, {reply.result.payload.to_bytes()}")

def sub(sample: zenoh.Sample) -> None:
    print(f"got sample: {sample}")

with zenoh.open(zenoh.Config()) as session:
    queryable = session.declare_queryable("hi/mom/*", handle)
    session.declare_subscriber("hi/mom/*", sub)
    session.get("hi/mom/*", handler=handle_reply, timeout=1000)
    # session.get("hi/mom/*", handler=handle_reply)
    # session.get("hi/mom/*", handler=handle_reply)
    # session.get("hi/mom/*", handler=handle_reply)
    # session.get("hi/mom/*", handler=handle_reply)
    time.sleep(50)