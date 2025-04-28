def pytest_addoption(parser):
    parser.addoption("--ip", action="store", default="192.168.4.60")