import zenoh
import time

i = 0
def handler(query: zenoh.Query):
    global i
    i += 1
    print("big calculation...")
    time.sleep(5)
    print("finished calculation")
    query.reply(key_expr=query.key_expr, payload=bytes(f"{i} {i}", encoding="utf-8"), congestion_control=zenoh.CongestionControl.BLOCK)

def handler2(query: zenoh.Query):
    print("big calculation...")
    time.sleep(5)
    print("finished calculation")
    query.reply(key_expr=query.key_expr, payload=bytes(f"{i}", encoding="utf-8"), congestion_control=zenoh.CongestionControl.BLOCK)

with zenoh.open(zenoh.Config()) as session:
    queryable = session.declare_queryable("testing/queryables", handler=handler, complete=False)
    # queryable = session.declare_queryable("testing/queryables", handler=handler2, complete=False)
    while True:
        pass