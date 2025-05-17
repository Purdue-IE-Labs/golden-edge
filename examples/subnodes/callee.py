import random
import sys
import time
import gedge
import pathlib

# we specify the path to the directory that holds all locally pulled models
# this allows us to use these models
here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

if len(sys.argv) > 1:
    ip_address = sys.argv[1]
else:
    ip_address = "localhost"

def level_1a_tag_write_handler(query: gedge.TagWriteQuery) -> None:
    print("level 1a tag write handler")
    if query.value > 10:
        query.reply_err(400)
    query.reply_ok(200)

def root_method_handler(query: gedge.MethodQuery) -> None:
    print("root method handler")
    query.reply_ok()

def level_1b_level_2a_method_handler(query: gedge.MethodQuery) -> None:
    print("level 1b level 2a method handler")
    query.reply_ok(200)

here = pathlib.Path(__file__).parent / "callee.json5"
node = gedge.NodeConfig.from_json5(str(here))
node.add_method_handler("root/method", handler=root_method_handler)

# in order to add handlers to subnodes, we need to subnode the node with this syntax
level_1a = node.subnode("level-1a")
level_1a.add_tag_write_handler("tag/write", handler=level_1a_tag_write_handler)

# dig straight down to the subnode that we want
level_1b_level_2a = node.subnode("level-1b/level-2a")
level_1b_level_2a.add_method_handler("inner/method", handler=level_1b_level_2a_method_handler)

with gedge.connect(node, ip_address) as session:
    level_1a = session.subnode("level-1a")
    level_1b = session.subnode("level-1b")

    """
    These three lines are equivalent and provide different methods 
    to get at a nested subnode. The structure here is 
    root {
        subnode level-1b {
            subnode level-2a
        }
    }
    We can either dig straight down using '/' or
    call '.subnode(...)' twice, or 
    call '.subnode(...)' on the existing subnode instance level_1b
    """
    level_2a = session.subnode("level-1b/level-2a")
    # level_2a = session.subnode("level-1b").subnode("level-2a")
    # level_2a = level_1b.subnode("level-2a")

    level_2a.update_tag("inner/tag", value=12.3)
    level_1a.update_tag("tag/write", value=239)

    try:
        # this line fails because subnode 'level-2a' does not have a tag 'tag/write'
        # that tag is actually defined only on 'level-1a'
        level_2a.update_tag("tag/write", value=239)
    except Exception as e:
        print(f"EXCEPTION: {e}")

    session.update_tag("root/tag", [1, 2])

    while True:
        # updating a model tag
        level_1a.update_tag("model/tag/qux", random.randint(0, 10))
        time.sleep(1)

        # updating a base tag
        level_2a.update_tag("inner/tag", random.random())
        time.sleep(1)