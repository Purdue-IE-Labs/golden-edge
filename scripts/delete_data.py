import requests
import dotenv
import pathlib
import os
import json
import sys

if len(sys.argv) <= 1:
    sys.exit("USAGE: python delete_data.py [bucket]")

headers = {
    "Authorization": f"Token {os.getenv("INFLUXDB_TOKEN")}",
    "Content-Type": "application/json"
}
data = {
    "start": "2019-03-01T00:00:00Z",
    "stop": "2030-11-14T00:00:00Z",
}

bucket = sys.argv[1]

if len(sys.argv) > 2:
    node = sys.argv[2]
    prefix, _, name = node.rpartition("/")
    here = pathlib.Path(__file__).parents[1] / ".env"
    dotenv.load_dotenv(dotenv_path=here)
    data["predicate"] = f"_measurement=\"{prefix}/NODE/{name}/META\""

response = requests.post(f"http://localhost:8086/api/v2/delete?org=ielabs&bucket={bucket}", headers=headers, data=json.dumps(data))
print(response.status_code)
print(response.text)

# To use the CLI
# .\influx.exe delete --bucket "method" --start "2020-03-01T00:00:00Z" --stop "2025-11-14T00:00:00Z" --org "ielabs" --skip-verify --token "..."
