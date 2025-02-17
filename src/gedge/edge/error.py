
class ConfigError(Exception):
    pass

class SessionError(Exception):
    pass

class TagLookupError(Exception):
    def __init__(self, path: str, node: str):
        message = f"Tag {path} not found on node {node}"
        super().__init__(message)

class MethodLookupError(Exception):
    def __init__(self, path: str, node: str):
        message = f"Method {path} not found on node {node}"
        super().__init__(message)

class NodeLookupError(Exception):
    def __init__(self, key: str):
        message = f"Node not found at key {key}"
        super().__init__(message)