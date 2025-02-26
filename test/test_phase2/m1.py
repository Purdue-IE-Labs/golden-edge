import gedge
import time

from gedge.edge.data_type import DataType
from gedge.edge.prop import Props

def method(query: gedge.Query):
    int_val = query.parameters["param1"]
    list_float_val = query.parameters["param2"]
    query.reply(code=100, body={"body1": int_val + 1, "body2": list_float_val + [1.0]})
    time.sleep(2)
    query.reply(code=200)

config = gedge.NodeConfig("test/m1")

m = config.add_method("method", method)
m.add_params(param1=int, param2=list[float])
r = m.add_response(code=100)
r.add_body(body1=int, body2=DataType.LIST_FLOAT)
with gedge.connect(config) as session:
    print("connected")
    print(session.config.methods)
    time.sleep(60)