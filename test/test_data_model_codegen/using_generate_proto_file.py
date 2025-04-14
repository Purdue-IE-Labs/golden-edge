
from generated_proto_file_pb2 import my_model

# i = my_model.root_object_message.inner_message(tag3="value")
# root = my_model.root_object_message(inner=i)
# model = my_model(root_object=root, tag1=2.3, tag2=1)
model = my_model()

print(model)
print(model.tag1)
print(model.root_object.inner.tag3)
print(model.root_object.tag4)
print(model.root_object.inner)