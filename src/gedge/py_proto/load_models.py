from __future__ import annotations

import os
import pathlib
import re
from typing import TYPE_CHECKING

import json5
from gedge.py_proto.singleton import Singleton

if TYPE_CHECKING:
    from gedge.py_proto.data_model_config import DataModelConfig
    from gedge.py_proto.data_model_ref import DataModelRef


# should this be a try/except or return None?
# probably should just error out, if they try to load but no model, that's an exception
def load(path: DataModelRef) -> DataModelConfig:

    # acts as a bit of a cache, so we have to go to the filesystem less and less
    config = Singleton().get_model(path.full_path)
    if config is not None:
        return config 

    directory = Singleton().get_model_dir()
    if not directory:
        raise LookupError(f"Trying to find model {path.path} but no model directory passed in. For the cli, use --model-dir. For Python, use gedge.use_models(...)")
    if path.version is None:
        dir = pathlib.Path(directory) / path.path
        path.version = find_latest_version(str(dir))
    p = path.to_file_path()
    path_to_json = pathlib.Path(directory) / p

    config = load_from_file(str(path_to_json))
    # add to cache so next time we retrieve this, it's in the Singleton
    Singleton().add_model(config)
    return config

def load_from_file(path: str) -> DataModelConfig:
    from gedge.py_proto.data_model_config import DataModelConfig
    if not os.path.exists(path):
        raise LookupError(f"No model found at path {path}")
    with open(path, "r") as f:
        j = json5.load(f)
    config = DataModelConfig.from_json5(j)
    return config

def find_latest_version(dir: str) -> int:
    max_version = -1
    if not os.path.exists(dir):
        raise LookupError(f"No model found at path {dir}")
    for f in os.listdir(dir):
        m = re.match(r'v(\d+).json5', f)
        if m:
            version = int(m.group(1))
            max_version = max(max_version, version)
    if max_version == -1:
        raise LookupError(f"No local version of model found in {dir}")
    return max_version
    
def to_file_path(path: str, version: int):
    return f"{path}/v{version}.json5"