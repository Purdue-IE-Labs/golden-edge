import argparse
import pathlib
import json5
import gedge

from gedge.comm.comm import Comm
from gedge.py_proto.data_model_config import DataModelConfig
from gedge.py_proto.singleton import Singleton

import logging
logger = logging.getLogger(__name__)

def push_pull(args):
    path = args.path
    model_dir = args.model_dir
    json_dir: str | None = args.json_dir
    if json_dir is None:
        logger.debug("No json_dir set, using parent of json file passed in...")
        json_dir = str(pathlib.Path(path).parent)
    if not model_dir:
        raise LookupError("Argument '--model-dir' required for 'gedge push-pull' command")
    Singleton(model_dir, json_dir)
    config = _push(path, args.ip_address)
    if not config:
        raise LookupError(f"Could not push model at path {path}")
    _pull(config.path, config.version, args.ip_address, model_dir)

def push(args):
    print("PUSH COMMAND")
    path = args.path
    model_dir = args.model_dir
    json_dir: str | None = args.json_dir
    if json_dir is None:
        logger.debug("No json_dir set, using parent of json file passed in...")
        json_dir = str(pathlib.Path(path).parent)
    Singleton(model_dir, json_dir)
    _push(path, args.ip_address)

def _push(path: str, ip_address: str) -> DataModelConfig | None:
    with open(path, "r") as f:
        res = f.read()
    j = json5.loads(res)
    config = DataModelConfig.from_json5(j) 
    logger.debug(f"Parsed config at json path {path}: {config}")
    with Comm([f"tcp/{ip_address}:7447"]) as comm:
        if not comm.push_model(config, True):
            logger.warning(f"Could not push model at path {path}")
            return None
    logger.info(f"Pushed model to path MODELS/{config.path}")
    return config

def pull(args):
    print("PULL COMMAND")
    path = args.path
    version = args.version
    model_dir = args.model_dir
    if not model_dir:
        raise LookupError("Argument '--model-dir' required for 'gedge pull' command")
    Singleton(model_dir)
    _pull(path, version, args.ip_address, model_dir)

def _pull(path: str, version: int | None, ip_address: str, model_dir: str):
    with Comm([f"tcp/{ip_address}:7447"]) as comm:
        config = comm.pull_model(path, version)
        if not config:
            raise LookupError(f"No model found at path {path} with version {version if version else "latest"}")
    logger.info(f"Pulled config at path {path}, writing to file...")
    logger.debug(f"Config: {config}")
    if not config.to_file(model_dir):
        raise LookupError("Could not convert config to file")
    logger.info(f"Model written to file {str(pathlib.Path(model_dir) / path)}")

def main():
    parser = argparse.ArgumentParser(prog="gedge", description="Handle models in golden-edge", epilog="Try 'gedge --help' for more info")
    parser.add_argument('--ip-address', type=str, default="192.168.4.60", help="IP address where historian lives")
    
    # currently for pushing, we search what we currently have
    parser.add_argument("--model-dir", type=str, help="outptut directory where all pulled models will go")

    subparsers = parser.add_subparsers(title="subcommands", help="subcommand help")

    push_parser = subparsers.add_parser("push", help="Subcommand for pushing models to historian")
    push_parser.add_argument("--json-dir", type=str, default=None, help="directory where we should search for json files (defaults to parent directory of path argument)")
    push_parser.add_argument("path", type=str, help="path to json5 file describing model")
    push_parser.set_defaults(func=push)

    pull_parser = subparsers.add_parser("pull", help="Subcommand for pulling models from historian")
    pull_parser.add_argument("--version", type=int, default=None, help="version of the model to pull (defaults to latest)")
    pull_parser.add_argument("path", type=str, help="path where model lives in the historian (not including MODELS/ prefix)")
    pull_parser.set_defaults(func=pull)

    push_pull_parser = subparsers.add_parser("push-pull", help="Pushes model to historian and pulls it")
    push_pull_parser.add_argument("--json-dir", type=str, default=None, help="directory where we should search for json files (defaults to parent directory of path argument)")
    push_pull_parser.add_argument("path", type=str, help="path to json5 file describing model")
    push_pull_parser.set_defaults(func=push_pull)

    args = parser.parse_args()
    args.func(args)
