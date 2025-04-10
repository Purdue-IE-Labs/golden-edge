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

def test_send_proto():
    # Set up mock data
    comm_instance = Comm(connections=["tcp/localhost:7447"])
    mock_key_expr = "some_key_expr"  # This could be any string for the test
    mock_proto = MagicMock()  # Mocking the ProtoMessage

    # Mock the return value of the sequence number before sending the proto
    initial_sequence_number = 5
    comm_instance.sequence_number = initial_sequence_number

    # Mock the serialize method to return some dummy serialized data
    comm_instance.serialize.return_value = b"dummy_serialized_data"

    # Now, simulate the `gedge.connect` context manager using unittest.mock
    with unittest.mock.patch('gedge.connect', return_value=MagicMock()) as mock_connect:
        # Simulate the session object returned by `gedge.connect`
        mock_session = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_session

        # Enter the context (setup session)
        comm_instance.__enter__()

        # Call _send_proto
        comm_instance._send_proto(mock_key_expr, mock_proto)

        # Exit the context (close session)
        comm_instance.__exit__(None, None, None)

        # Ensure the sequence number was incremented
        # Check that `sequence_number.increment()` was called once
        comm_instance.sequence_number.increment.assert_called_once()

         # Verify that the sequence number has increased by 1
        new_sequence_number = comm_instance.sequence_number
        assert new_sequence_number == initial_sequence_number + 1

        # Verify that `put` was called with the expected arguments (key, data, encoding, attachment)
        mock_session.put.assert_called_once_with(
            mock_key_expr, 
            b"dummy_serialized_data", 
            encoding="application/protobuf", 
            attachment=bytes(comm_instance.sequence_number)
        )




    