import zenoh

NODE = "NODE"
META = "META"
TAGS = "TAGS"
DATA = "DATA"
WRITE = "WRITE"
STATE = "STATE"
METHODS = "METHODS"

def key_join(*components: list[str]):
    return "/".join(components)

def node_key_prefix(prefix: str, name: str):
    return key_join(prefix, NODE, name)

def meta_key_prefix(prefix: str, name: str):
    return key_join(prefix, NODE, name, META)

def tag_data_key_prefix(prefix: str, name: str):
    return key_join(node_key_prefix(prefix, name), TAGS, DATA)

def tag_data_key(prefix: str, name: str, key: str):
    return key_join(node_key_prefix(prefix, name), TAGS, DATA, key)

def tag_write_key_prefix(prefix: str, name: str):
    return key_join(node_key_prefix(prefix, name), TAGS, WRITE)

def tag_write_key(prefix: str, name: str, key: str):
    return key_join(node_key_prefix(prefix, name), TAGS, WRITE, key)

def state_key_prefix(prefix: str, name: str):
    return key_join(node_key_prefix(prefix, name), STATE)

def method_key_perfix(prefix: str, name: str):
    return key_join(node_key_prefix(prefix, name), METHODS)

def liveliness_key_prefix(prefix: str, name: str):
    return node_key_prefix(prefix, name)

def node_name_from_key_expr(key_expr: str | zenoh.KeyExpr):
    components = str(key_expr).split("/")
    return components[components.index(NODE) + 1]

class NodeKeySpace:
    def __init__(self, prefix: str, name: str):
        self._prefix = prefix
        self._name = name
        self._user_key = prefix + "/" + name
        self._set_keys(self.prefix, self.name)

    @classmethod
    def from_user_key(cls, key: str):
        prefix, name = NodeKeySpace.split_user_key(key)
        return cls(prefix, name)

    @staticmethod
    def split_user_key(key: str):
        key = key.strip('/')
        if '/' not in key:
            raise ValueError(f"key {key} must include at least one '/'")
        prefix, _, name = key.rpartition('/')
        return prefix, name

    @staticmethod
    def name_from_key(key_expr: str):
        components = key_expr.split("/")
        return components[components.index(NODE) + 1]
    
    @staticmethod
    def tag_path_from_key(key_expr: str):
        components = key_expr.split("/")
        try:
            i = components.index(DATA)
        except:
            try: 
                i = components.index(WRITE)
            except:
                raise ValueError(f"No tag path found in {key_expr}")
        return "/".join(components[(i + 1):])

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, prefix: str):
        self._prefix = prefix
        self._set_keys(prefix, self.name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name
        self._set_keys(self.prefix, name)

    @property
    def user_key(self):
        return self._user_key

    @user_key.setter
    def user_key(self, user_key: str):
        prefix, name = NodeKeySpace.split_user_key(user_key)
        self.prefix = prefix
        self.name = name
    
    def _set_keys(self, prefix: str, name: str):
        self.node_key_prefix = node_key_prefix(prefix, name)
        self.meta_key_prefix = meta_key_prefix(prefix, name)
        self.state_key_prefix = state_key_prefix(prefix, name)
        self.tag_data_key_prefix = tag_data_key_prefix(prefix, name)
        self.tag_write_key_prefix = tag_write_key_prefix(prefix, name)
        self.liveliness_key_prefix = liveliness_key_prefix(prefix, name)
        self.method_key_prefix = method_key_perfix(prefix, name)
    
    def tag_data_path(self, path: str):
        return tag_data_key(self.prefix, self.name, path)
    
    def tag_write_path(self, path: str):
        return tag_write_key(self.prefix, self.name, path)
    
    def method_path(self, path: str):
        return key_join(self.method_key_prefix, path)
        