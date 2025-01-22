import subprocess
import pathlib

here = pathlib.Path(__file__).parents[1]
proto_folder = here / "proto"
python_proto_folder = here / "src" / "gedge" / "proto"
res = subprocess.run(["protoc", f"--proto_path={str(proto_folder)}", f"--python_out=pyi_out:{str(python_proto_folder)}", f"{str(proto_folder)}\\*.proto"])
if res.returncode != 0:
    print("error generating protobuf files:")
    print(res.stderr)

import re
import os

files = [f for f in os.listdir(python_proto_folder) if os.path.isfile(python_proto_folder / f)]
for file in files:
    path = python_proto_folder / file
    newLines = []
    with open(path, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = re.sub(r'^import', "from . import", line)
            newLines.append(line)
    with open(path, "w") as f:
        for line in newLines:
            f.write(line)
