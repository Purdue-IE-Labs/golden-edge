import gedge
import pytest
from unittest.mock import MagicMock
import json
import zenoh

from gedge.comm.comm import Comm
import base64

def test_serealize():
    mock_proto = MagicMock()

    mock_proto.SerializeToString.return_value = b"some data"

    result = Comm.serialize(Comm, mock_proto)

    expected_result = base64.b64encode(b"some data")

    assert result == expected_result


def test_deserialize():
    mock_proto = MagicMock()

    mock_proto.ParseFromString.return_value = None

    payload = b"some data"

    decoded_data = base64.b64decode(payload)
    
    result = Comm.deserialize(Comm, mock_proto, payload)

    mock_proto.ParseFromString.asssert_called_once_with(decoded_data)

    assert result == mock_proto

'''
def test_send_proto():
    comm_instance = Comm(connections=["some connection"])

    Comm.__enter__(comm_instance)

    mock_key_expr = "some key expr"
    mock_proto = MagicMock()

    initial_sequence_number = 5
    comm_instance.sequence_number = initial_sequence_number

    comm_instance._send_proto()
'''

