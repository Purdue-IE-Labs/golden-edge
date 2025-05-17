import sys
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
    print("vice tag write handler")
    if query.value > 10:
        query.reply_err(400)
    query.reply_ok(200)

def root_method_handler(query: gedge.MethodQuery) -> None:
    print("mill method handler")
    query.reply_err(401)

def level_1b_level_2a_method_handler(query: gedge.MethodQuery) -> None:
    print("inner subnode method handler")
    query.reply_ok(200)

here = pathlib.Path(__file__).parent / "gedge.json5"
node = gedge.NodeConfig.from_json5(str(here))
node.add_method_handler("call/method", handler=root_method_handler)

level_1a = node.subnode("level-1a")
level_1a.add_tag_write_handler("tag/write", handler=level_1a_tag_write_handler)

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
        level_2a.update_tag("tag/write", value=239)
    except Exception as e:
        print(f"EXCEPTION: {e}")

    session.update_tag("root/tag", [1, 2])

    # updating a model tag
    level_1a.update_tag("model/tag/qux", 123)

    while True:
        pass