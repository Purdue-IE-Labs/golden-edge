from typing import Any
import inspect

class Session:
    def __init__(self, thing):
        self.thing = thing

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass

    def func(self, value: int) -> float:
        func = self.thing.functions[0]
        string = func(value)
        return 1.0 + value

class Thing:
    def __init__(self):
        self.functions = []

    def add_function(self, func):
        self.functions.append(func)

    def connect(self) -> Session:
        class_name = "my_method"
        session = Session(self)
        setattr(session, class_name, session.func)
        function = getattr(session, class_name)
        function.__annotations__['value'] = float
        function.__annotations__['return'] = str
        print(f"function annotations: {function.__annotations__}")
        return session

def a(value: int) -> str:
    return "hi"

if __name__ == "__main__":
    thing = Thing()
    thing.add_function(a)
    with thing.connect() as session:
        print("method annotations")
        print(session.func.__annotations__)
        print(session.my_method.__annotations__)
        session.my_method()
    
    print(inspect.get_annotations(a))
    print(a.__annotations__)

    print(Session.__annotations__)
    print(Thing.__annotations__)

# annotations for adding type hints