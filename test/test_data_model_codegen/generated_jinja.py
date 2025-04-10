from dataclasses import dataclass

@dataclass
class MyModel:
    tag1: bool

    def my_method(self):
        print("hello, world")
        print(self.tag1)