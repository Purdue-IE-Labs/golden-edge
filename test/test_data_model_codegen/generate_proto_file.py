from data_model_pb2 import Model, Base, Object
import json5

# TODO: stringify the type

def json_config() -> str:
    res = json5.dumps({
        "objects": [
            {
                "name": "root_object",
                "objects": [
                    {
                        "name": "inner",
                    }
                ],
                "bases": [

                ]
            }
        ],
        "bases": [

        ],
    })
    return res

def add_values_to_proto() -> Model:
    tag1 = Base(name="tag1", type="float")
    tag2 = Base(name="tag2", type="int32")

    tag3 = Base(name="tag3", type="string")
    tag4 = Base(name="tag4", type="bool")
    obj1 = Object(name="inner", bases=[tag3])

    obj = Object(name="root_object", objects=[obj1], bases=[tag4])

    model = Model(name="my_model", objects=[obj], bases=[tag1, tag2])
    return model

def proto_object(object: Object) -> str:
    res = ""
    index = 1
    for o in list(object.objects):
        res += proto_object(o)
    res += f"message {object.name}_message {{\n"
    for base in list(object.bases):
        res += f"\t{base.type} {base.name} = {index};\n"
        index += 1
    for o in list(object.objects):
        res += f"\t{o.name}_message {o.name} = {index};\n"
        index += 1
    res += f"}}\n\n"
    return res

def proto_model(model: Model) -> str:
    res = f"message {model.name} {{\n"
    index = 1
    for object in list(model.objects):
        res += f"\t{object.name}_message {object.name} = {index};\n"
        index += 1
    for base in list(model.bases):
        res += f"\t{base.type} {base.name} = {index};\n"
        index += 1
    res += f"}}\n"
    return res

model = add_values_to_proto()
print(model)

with open("./scripts/generated_proto_file.proto", "w") as f:
    f.write("""syntax = "proto3";\n\n""")

    for object in list(model.objects):
        f.write(proto_object(object))

    f.write(proto_model(model))
