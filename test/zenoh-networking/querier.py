import sys
import time
import zenoh
import threading

def handler(reply: zenoh.Reply):
    print(f"got reply: {str(reply.result.payload.to_bytes())}")

def thread_func(key_expr: str, handler):
    print("starting call")
    session.get(key_expr, handler)

with zenoh.open(zenoh.Config()) as session:
    # for _ in range(1000):
    #     thread = threading.Thread(target=thread_func, args=["testing/queryables", handler])
    #     thread.start()
    result = session.get("testing/queryables", timeout=1).recv()
    print(result.result.payload.to_string())
    for i in range(10):
        print(i)
    session.get("testing/queryables", handler)
    print("done")