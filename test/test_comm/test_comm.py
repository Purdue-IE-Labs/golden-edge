import sys
import os

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import unittest
from unittest.mock import MagicMock
import base64
from gedge.comm import comm

class TestComm(unittest.TestCase):
    def test_serealize(self):
        mock_proto = MagicMock()

        mock_proto.SerializeToString.return_value = b'\x08\x96\x01'

        result = comm.serialize(mock_proto)

        expected_base64 = base64.b64encode(b'\x08\x96\x01')

        self.assertEqual(result, expected_base64)

if __name__ == '__main__':
    unittest.main()



