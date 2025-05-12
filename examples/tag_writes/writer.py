import time
import gedge
import sys
import pathlib

here = pathlib.Path(__file__).parents[2] / "models"
gedge.use_models(str(here))

if len(sys.argv) > 1:
    ip_address = sys.argv[1]
else:
    ip_address = "localhost"

config = gedge.NodeConfig("gedge/examples/tag_writes/writer")

with gedge.connect(config, ip_address) as session:
    remote = session.connect_to_remote("gedge/examples/tag_writes/writee")

    response = remote.write_tag("base/tag/writable", 3.5)

    time.sleep(2)

    response = remote.write_tag("model/tag/foo/bar/baz", 12.3)
    print(response)

    time.sleep(1)

    # in writee.py, no handler was provided for this tag, so 
    # we receive a built-in callback error code (30) because 
    # the write request cannot be completed
    response = remote.write_tag("base/tag/writable/no/handler", True)
    print(response)

    try:
        # this tag is not writable, so it will throw an error
        response = remote.write_tag("base/tag", 1)
    except LookupError as e:
        print(f"EXCEPTION: {e}")

    try:
        # this is the wrong type, so a value error will be thrown
        response = remote.write_tag("base/tag/writable", "string")
    except ValueError as e:
        print(f"EXCEPTION: {e}")

    try:
        # this tag does not exist, so a lookup error is thrown
        response = remote.write_tag("ba/g/le", "string")
    except LookupError as e:
        print(f"EXCEPTION: {e}")

    time.sleep(2)