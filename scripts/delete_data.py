import requests
import dotenv
import pathlib
import os
import json
import sys

node = sys.argv[1]

prefix, _, name = node.rpartition("/")

here = pathlib.Path(__file__).parents[1] / ".env"
dotenv.load_dotenv(dotenv_path=here)

headers = {
    "Authorization": f"Token {os.getenv("INFLUXDB_TOKEN")}",
    "Content-Type": "application/json"
}
data = {
    "start": "2020-03-01T00:00:00Z",
    "stop": "2025-11-14T00:00:00Z",
    "predicate": f"_measurement=\"{prefix}/NODE/{name}/META\""
}

response = requests.post("http://localhost:8086/api/v2/delete?org=ielabs&bucket=meta", headers=headers, data=json.dumps(data))
print(response.status_code)
print(response.text)

data = {
    "start": "2020-03-01T00:00:00Z",
    "stop": "2025-11-14T00:00:00Z",
    "predicate": f"_measurement=\"stuff/META\""
}

response = requests.post("http://localhost:8086/api/v2/delete?org=ielabs&bucket=meta", headers=headers, data=json.dumps(data))
print(response.status_code)
print(response.text)

# .\influx.exe delete --bucket "method" --start "2020-03-01T00:00:00Z" --stop "2025-11-14T00:00:00Z" --org "ielabs" --skip-verify --token "..."
