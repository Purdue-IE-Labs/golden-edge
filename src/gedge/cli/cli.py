import argparse
import pathlib
import json5
import gedge

from gedge.comm.comm import Comm
from gedge.py_proto.data_model_config import DataModelConfig
from gedge.py_proto.singleton import Singleton

import logging
logger = logging.getLogger(__name__)

def push(args):
    print("PUSH COMMAND")
    path = args.path
    model_dir = args.model_dir
    json_dir: str | None = args.json_dir
    if json_dir is None:
        logger.debug("No json_dir set, using parent of json file passed in...")
        json_dir = str(pathlib.Path(path).parent)
    Singleton(model_dir, json_dir)

    with Comm([f"tcp/{args.ip_address}:7447"]) as comm:
        with open(path, "r") as f:
            res = f.read()
        j = json5.loads(res)
        config = DataModelConfig.from_json5(j) 
        logger.debug(f"Parsed config at json path {path}: {config}")
        if not comm.push_model(config):
            logger.warning(f"Could not push model at path {path}")

def pull(args):
    print("PULL COMMAND")
    path = args.path
    version = args.version
    model_dir = args.model_dir
    if not model_dir:
        raise LookupError("Argument '--model-dir' required for 'gedge pull' command")
    Singleton(model_dir)

    with Comm([f"tcp/{args.ip_address}:7447"]) as comm:
        config = comm.pull_model(path, version)
        if not config:
            raise LookupError(f"No model found at path {path} with version {version}")
        config.to_file(str(model_dir), comm)

def main():
    parser = argparse.ArgumentParser(prog="gedge", description="Handle models in golden-edge", epilog="Try 'gedge --help' for more info")
    parser.add_argument('--ip-address', type=str, default="192.168.4.60")
    
    # currently for pushing, we search what we currently have
    parser.add_argument("--model-dir", type=str, help="outptut directory where all pulled models will go")

    subparsers = parser.add_subparsers(title="subcommands", help="subcommand help")

    push_parser = subparsers.add_parser("push")
    push_parser.add_argument("--json-dir", type=str, default=None, help="directory where we should search for json files (defaults to parent directory of path)")
    push_parser.add_argument("path", type=str, help="path to json5 file describing model")
    push_parser.set_defaults(func=push)

    pull_parser = subparsers.add_parser("pull")
    pull_parser.add_argument("--version", type=int, default=None, help="version of the model to pull")
    pull_parser.add_argument("path", type=str, help="path where model lives in the historian")
    pull_parser.set_defaults(func=pull)

    args = parser.parse_args()

    print(args)
    print(args.ip_address)
    print(args.path)
    args.func(args)
