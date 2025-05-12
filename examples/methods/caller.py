import pathlib
import sys
import gedge

# we specify the path to the directory that holds all locally pulled models
# this allows us to use these models
here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

# This is the callback that we pass into remote.call_method(...)
# It returns everytime we receive another response
def on_reply(r: gedge.Response):
    print(r)

# here, we define a Node Configuration with only a key
# this is useful when a node's only job is to interact 
# with other nodes (by calling methods, subscribing to tags, etc.)
config = gedge.NodeConfig("gedge/examples/methods/caller")

if len(sys.argv) > 1:
    ip_address = sys.argv[1]
else:
    ip_address = "192.168.4.60"

with gedge.connect(config, ip_address) as session:
    # we connect to another node by giving it the key of that node
    # this can be found in methods.json5 at 'key'
    # the RemoteConnection instance returned allows use to call 
    # methods, write to tags, etc. etc.
    remote = session.connect_to_remote("gedge/examples/methods/callee") 

    # defining a model that we will pass in as a parameter
    bar_model = {
        "foo/bar/baz": 23.45,
        "baz": False,
        "qux": 123
    }

    # remote.call_method_iter(...) takes a path to a method, an optional timeout, 
    # and a list of keyword arguments that must correspond to the parameters 
    # of the method that we are targeting
    # Importantly, remote.call_method_iter(...) is a generator, so it must either 
    # be iterated over (like below) to get the responses
    # or converted to a list with list(...). Otherwise, it is useless
    responses = remote.call_method_iter("my/method/path", param1=0, param2=bar_model)
    for r in responses:
        # importantly, r.is_err() and r.is_ok() will only fire on the last response iterated
        # over, because everything before it is assumed to be an INFO response.
        # that is, a sequence of responses from a method looks like the following:
        # (0 to inf INFO) followed by (1 OK or 1 ERR)

        # we can check if we have received a response of type == gedge.ResponseType.ERR
        if r.is_err():
            print("ERR")
            print(r.code, r.type, r.body, r.props)
        if r.is_ok():
            print("OK")
            print(r.code, r.type, r.body, r.props)
    
    # we can also call a method by passing in a callback that will run 
    # on each response of the method
    # this will not block, and the problem with that is we won't get any of 
    # the responses because the context manager will end right after this call.
    # Unless we add an infinite loop.
    remote.call_method("my/method/path", on_reply, param1=2, param2=bar_model)

    while True:
        pass
    