import sys
from typing import Any
import gedge
import pathlib

# we specify the path to the directory that holds all locally pulled models
# this allows us to use these models
here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

def handler(query: gedge.MethodQuery):
    # this is a base type parameter
    param1: int = query.params["param1"]

    # this is a model parameter
    param2: dict[str, Any] = query.params["param2"]

    # this is the key expression that the method will respond on
    k = query.key_expr

    if param1 == 0:
        # this will use the default built-in OK message
        # importantly, both query.reply_ok(...) and 
        # query.reply_err(...) will end the handler
        # (under the hood, they raise a well-known exception
        # to stop the execution of the handler)
        query.reply_ok() 

        # this will never run
        query.reply_ok()
    if param1 == 1:
        # use default built-in ERR message
        query.reply_err()
    if param1 == 2:
        # if we want to use a response that we defined ourselves
        # we provide the code and body. In our case, we have to 
        # provide a 'res1' body item based on the config
        query.reply_ok(200, { "res1" : param1 + 10 })
    if param1 == 3:
        query.reply_err(400, { "res1" : 0 })
    if param1 == 4:
        # there is no built-in info code, so the user must provide 
        # a code to this function
        # importantly, query.reply_info(...) does not end the 
        # function like query.reply_ok(...) and query.reply_err(...)
        query.reply_info(202)
        
        # this is invalid syntax
        # query.reply_info()
        query.reply_ok(200, { "res1" : param1 * 2 })
    else:
        # in this case, gedge will automatically response with 
        # an error message where code=gedge.ERR, type=gedge.ResponseType.ERR
        return

here = pathlib.Path(__file__).parent
config = gedge.NodeConfig.from_json5(str(here / "methods.json5"))
config.add_method_handler("my/method/path", handler=handler)

# this is the address of the zenoh instance that 
# we want to connect to
# if you have a zenoh-influx pair running as a container 
# on your machine, you can just use "localhost"
# otherwise, target the IP of the zenoh container
def get_ip_address():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return "localhost"

with gedge.connect(config, get_ip_address()) as session:
    # we enter an infinite loop to essentially say that we want to 
    # keep this node up but not actually do much besides that 
    # except to wait for other nodes to interact with us
    while True:
        pass