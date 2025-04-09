class DomainSpecificLanguage(type):
    def __new__(cls, name, bases, attrs):
        # Find all methods starting with "when_" and store them in a dictionary
        events = {k: v for k, v in attrs.items() if k.startswith("when_")}
        
        # Create a new class that will be returned by this metaclass
        new_cls = super().__new__(cls, name, bases, attrs)
        
        # Define a new method that will be added to the class
        def listen(self, event):
            if event in events:
                events[event](self)
        
        def print_hello(self):
            print("Hello")
        
        # Add the new method to the class
        new_cls.listen = listen
        new_cls.print_hello = print_hello
        
        return new_cls

# Define a class using the DSL syntax
class MyDSLClass(metaclass=DomainSpecificLanguage):
    def when_hello(self):
        print("Hello!")

    def when_goodbye(self):
        print("Goodbye!")

# Use the DSL syntax to listen for events
obj = MyDSLClass()
obj.listen("hello")  # Output: "Hello!"
obj.listen("goodbye")  # Output: "Goodbye!"
obj.print_hello()