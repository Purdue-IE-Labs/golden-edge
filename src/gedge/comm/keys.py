import zenoh

def node_key_prefix(prefix: str, name: str):
    node_key_prefix = prefix + f"/NODE/{name}"
    return node_key_prefix

def meta_key_prefix(prefix: str, name: str):
    meta_key_prefix = prefix + f"/NODE/{name}/META"
    return meta_key_prefix

def tag_data_key_prefix(prefix: str, name: str):
    return node_key_prefix(prefix, name) + "/TAGS/DATA"

def tag_data_key(prefix: str, name: str, key: str):
    return node_key_prefix(prefix, name) + f"/TAGS/DATA/{key}"

def tag_write_key_prefix(prefix: str, name: str):
    return node_key_prefix(prefix, name) + "/TAGS/WRITE"

def state_key_prefix(prefix: str, name: str):
    return node_key_prefix(prefix, name) + "/STATE"

def liveliness_key_prefix(prefix: str, name: str):
    return node_key_prefix(prefix, name)

def node_name_from_key_expr(key_expr: str | zenoh.KeyExpr):
    components = str(key_expr).split("/")
    return components[components.index("NODE") + 1]

class NodeKeySpace:
    def __init__(self, prefix: str, name: str):
        self._prefix = prefix
        self._name = name

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
    
    def _set_keys(self, prefix: str, name: str):
        self.node_key_prefix = node_key_prefix(prefix, name)
        self.meta_key_prefix = meta_key_prefix(prefix, name)
        self.state_key_prefix = meta_key_prefix(prefix, name)
        self.tag_data_key_prefix = tag_data_key_prefix(prefix, name)
        self.tag_write_key_prefix = tag_write_key_prefix(prefix, name)
        self.liveliness_key_prefix = liveliness_key_prefix(prefix, name)