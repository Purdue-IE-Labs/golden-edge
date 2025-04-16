import argparse
import pathlib
import json5
import gedge

import gedge.comm
import gedge.comm.comm
from gedge.py_proto.data_model_config import DataModelConfig

def push(args):
    print("PUSH COMMAND")
    path = args.path

    with gedge.comm.comm.Comm([f"tcp/{args.ip_address}:7447"]) as comm:
        with open(path, "r") as f:
            res = f.read()
        j = json5.loads(res)
        config = DataModelConfig.from_json5(j) 
        print(config)
        proto_config = config.to_proto()
        print(type(proto_config))
        comm._send_proto(f"MODELS/{config.path}", proto_config)

def pull(args):
    print("PULL COMMAND")
    path = args.path

    with gedge.comm.comm.Comm([f"tcp/{args.ip_address}:7447"]) as comm:
        config = comm.pull_model(path)
        here = pathlib.Path(__file__).parents[3] / "test" / "test_models" / "model_pulled.json5"
        j = config.to_json5()
        with open(str(here), "w") as f:
            json5.dump(j, f, indent=4)

def main():
    parser = argparse.ArgumentParser(prog="gedge", description="Handle models in golden-edge", epilog="Try 'gedge --help' for more info")
    parser.add_argument('--ip-address', type=str, default="192.168.4.60")

    subparsers = parser.add_subparsers(title="subcommands", help="subcommand help")

    push_parser = subparsers.add_parser("push")
    push_parser.add_argument("path", type=str, help="path to json5 file describing file")
    push_parser.set_defaults(func=push)

    pull_parser = subparsers.add_parser("pull")
    pull_parser.add_argument("path", type=str, help="path where model lives in the historian")
    pull_parser.set_defaults(func=pull)

    args = parser.parse_args()

    print(args)
    print(args.ip_address)
    print(args.path)
    args.func(args)
