import zenoh
import time

def handle(query: zenoh.Query):
    print('query received')
    print(f'query parameters: {query.parameters}')
    print(f'query selector: {query.selector}')
    print(f"payload: {query.payload}")
    print(f"encoding: {query.encoding}")
    print(f"attachment: {query.attachment}")
    print(f"key expression: {query.key_expr}")
    query.reply("hi/mom", bytes("hello", encoding="utf-8"))

def other(reply: zenoh.Reply):
    print("other?")
    print(f"reply: {reply.result.payload}")

with zenoh.open(zenoh.Config()) as session:
    queryable = session.declare_queryable("hi/mom", handle)
    time.sleep(2)
    query = zenoh.Selector("hi/mom", {"key": "value"})
    querier = session.declare_querier("hi/mom")
    querier.get(other, parameters={"key": "value"})
    time.sleep(1)
    queryable.undeclare()
    querier.undeclare()
print(f"here: {session.is_closed()}")