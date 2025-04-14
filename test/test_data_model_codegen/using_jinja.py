from email.mime import base
import jinja2
import jinja2.nativetypes

env = jinja2.nativetypes.NativeEnvironment()
t = env.from_string("{{x + y}}")
result = t.render(x=4, y=2)
print(result)
print(type(result))

model_name = "MyModel"
base_type = "bool"
tag_name = "tag1"

t = env.from_string(
"""
class {{model}}:
    {{base_type}} {{tag_name}} = True
"""
)

res = t.render(model=model_name, base_type=base_type, tag_name=tag_name)
print(res)

class Foo:
    def __init__(self, value):
        self.value = value

result = env.from_string('{{ x }}').render(x=Foo(15))
print(result)
print(type(result).__name__)

result = None
with open("./scripts/using_jinja.py.j2", "r") as f:
    t = env.from_string(f.read())
    result = t.render(model=model_name, base_type=base_type, tag_name=tag_name)

with open("./scripts/generated_jinja.py", "w") as f:
    f.write(result)

# from jinja2 import Environment, PackageLoader, select_autoescape
# env = Environment(
#     loader=PackageLoader("gedge"),
#     autoescape=select_autoescape()
# )
# print(env)
