# gedge scripts

This directory provides utility scripts for developing `gedge`.

# delete_data.py

In the event that the protobuf changes or something else gets into a bad state
in the historian, we may want to wipe it. To do so, run

```
python ./scripts/delete_data.py [bucket] [optional node key]
```

If a node key is not passed in, the script deletes every entry in "bucket".
Otherwise, it deletes only those entries associated with a specific node.
Buckets defined in the historian are:

1. model
2. meta
3. state
4. tag_data
5. tag_write
6. method

# generate_proto.py

This script generates all the protobuf python files and puts them in `./src/gedge/proto/`. It also
corrects an issue with protobuf python file generation detailed [here](https://github.com/protocolbuffers/protobuf/issues/1491).
To run: `python ./scripts/generate_proto.py`.

# load_dotenv.py

If you have a `.env` file in your project (for influxdb tokens, for example), you can load those environment variables
into your shell by running `python ./scripts/load_dotenv.py`
