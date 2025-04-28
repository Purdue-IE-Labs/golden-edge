# DELETE LATER

from gedge.proto.type_pb2 import BaseType, DataModelType
from gedge import proto

def num_bytes(obj):
    num = len(obj.SerializeToString())
    return num

def print_num_bytes(obj):
    num = num_bytes(obj)
    print(num)
    return num

def length_int(i: int):
    return (i.bit_length() + 7) // 8

bd = proto.BaseData(string_data="four")
bd2 = proto.BaseData(string_data="five_")
print_num_bytes(bd)
print_num_bytes(bd2)

do1 = proto.DataObject(base_data=bd)
print("Data Object 1:")
print_num_bytes(do1)
do2 = proto.DataObject(base_data=bd2)
print_num_bytes(do2)

num_items = 2
l = [do1] * num_items
dm = proto.DataModel(data=l)
dm_bytes = print_num_bytes(dm)
do_bytes = print_num_bytes(do1) * num_items
print(f"difference: {dm_bytes - do_bytes}, {dm_bytes}, {do_bytes}")

do = proto.DataObject(model_data=dm) # 22
print(f"Data Object: {num_bytes(do)}")

stuff = DataModelType(path="", version=4099999990)
# print_num_bytes(stuff)

# WON'T COMPILE
res = BaseType.LIST_BOOL
# print_num_bytes(res)

model_path = DataModelType(path="four", version=10) # 8
print_num_bytes(model_path)
moc = proto.DataModelObjectConfig(path=model_path) # 10
print_num_bytes(moc)
c = proto.Config(data_model_config=moc) # 12
print(f"Config: {num_bytes(c)}")

p = proto.Prop(config=c, value=do)
print(f"Prop: {num_bytes(p)}")
dict_ = {"four": p, "five": p, "six_": p, "seven": p}
props = proto.Props(props=dict_)
# for one, prop is 4 + p = 42, and props is 48, so adds 6
# for two, prop is 84, and props is 96, so it adds 12
print(f"Props: {num_bytes(props)}, equals {6 * len(dict_) + sum(len(x) + num_bytes(y) for x, y in dict_.items())}")

doc = proto.DataObjectConfig(config=c, props=props)
print(f"Data Object Config {num_bytes(doc)}, equals {5 + num_bytes(c) + num_bytes(props)}")

path = "four"
dmic = proto.DataModelItemConfig(path=path, config=doc)
print(f"Data Model Item Config: {num_bytes(dmic)}, equals {5 + len(path) + num_bytes(doc)}")

path = "nine()()("
version = 10
parent = moc
items = [dmic, dmic, dmic, dmic]
dmc = proto.DataModelConfig(path=path, version=10, parent=parent, items=items)
print(f"Data Model Config: {num_bytes(dmc)}")
print(f"Equation: {5 + 2 + len(path) + 1 + length_int(version) + num_bytes(moc) + (2 * len(items)) + sum(num_bytes(x) for x in items)}")

code = 10
res = proto.TagWriteResponseConfig(code=code, props=props)
print(f"Tag Write Response Config: {num_bytes(res)}")
print(f"Equals: {4 + length_int(code) + num_bytes(props)}")

num_items = 2
l = [res] * num_items
tc = proto.TagConfig(config=dmic, writable=True, responses=l)
print(f"Tag Config: {num_bytes(tc)}")
print(f"Equals: {4 + num_bytes(dmic) + 2 + (2 * num_items) + sum(num_bytes(x) for x in l)}")


dict_ = {"four": doc, "five": doc, "six": doc}
bc = proto.BodyConfig(body=dict_)
print(f"Body Config: {num_bytes(bc)}")
print(f"Equals: {4 + 6 * len(dict_) + sum(len(x) + num_bytes(y) for x, y in dict_.items())}")