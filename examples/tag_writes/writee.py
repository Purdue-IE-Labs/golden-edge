import pathlib
import sys
import gedge

here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

if len(sys.argv) > 1:
    ip_address = sys.argv[1]
else:
    ip_address = "localhost"

def handler1(query: gedge.TagWriteQuery) -> None:
    # value is of type Any, but it is guaranteed to 
    # match the type given in the configuration json
    if query.value > 10:
        query.reply_err(400)
    query.reply_ok(200)

def handler2(query: gedge.TagWriteQuery) -> None:
    # this is the key expression that we use to write to the tag
    k = query.key_expr

    # if this line is uncommented, the result would be that 
    # gedge would search for this code in the config,
    # not find it, and so reply with code 30 (corresponding to a 
    # error in the handler that the user defined for a tag or method)
    # query.reply_ok(100000)

    if query.value > 15.5:
        query.reply_ok(205)
    elif query.value < 0.0:
        # if we never call any version of query.reply, gedge will 
        # catch this and return an error, noting that we used the 
        # API incorrectly
        return

    # if we use an empty query.reply_err() call, gedge 
    # uses the default err message instead of a code we defined
    query.reply_err()

here = pathlib.Path(__file__).parent
config = gedge.NodeConfig.from_json5(str(here / "tag_writes.json5"))

# this is the preferred method for adding handlers for the writable tags
# if a tag is defined as writable but a handler is not provided, 
# any node that tries to write to that tag will receive a callback 
# error code
config.add_tag_write_handler("base/tag/writable", handler=handler1)
config.add_tag_write_handler("model/tag/foo/bar/baz", handler=handler2)

with gedge.connect(config, ip_address) as session:
    while True:
        pass