import gedge
import pytest
import time

@pytest.fixture
def ip_address(pytestconfig):
    return pytestconfig.getoption("ip")

@pytest.fixture
def remote_connection(ip_address):
    config = gedge.NodeConfig("test/tag/writes/writer")
    with gedge.connect(config, ip_address) as session:
        remote = session.connect_to_remote("test/tag/writes/writee")
        yield remote

testData = [
    (5, 200),
    (15, 400),
    (25, 600),
    (10, 200),
    (20, 400)
]

ids = [
    "Test Low",
    "Test Medium",
    "Test High",
    "Test Low to Medium Boundary",
    "Test Medium to High Boundary"
]

@pytest.mark.parametrize("value, code", testData, ids=ids)
@pytest.mark.sanity
def test_sanity(value, code, remote_connection):
    remote = remote_connection
    reply = remote.write_tag("tag/write", value=value)
    assert reply.code == code

@pytest.mark.infinite
def test_infinite(remote_connection):
    remote = remote_connection
    reply = remote.write_tag("tag/write", value=0)
    assert reply.code == 20

def test_afterinfinite(remote_connection):
    remote = remote_connection
    reply = remote.write_tag("tag/write", value = 15)
    assert reply.code == 400