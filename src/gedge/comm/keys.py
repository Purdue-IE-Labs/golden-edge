from __future__ import annotations

NODE = "NODE"
META = "META"
TAGS = "TAGS"
DATA = "DATA"
WRITE = "WRITE"
STATE = "STATE"
METHODS = "METHODS"
RESPONSE = "RESPONSE"
SUBNODES = "SUBNODES"

def key_join(*components: str):
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

def method_key_prefix(prefix: str, name: str):
    return key_join(node_key_prefix(prefix, name), METHODS)

def liveliness_key_prefix(prefix: str, name: str):
    return node_key_prefix(prefix, name)

def subnodes_key_prefix(prefix: str, node_name: str):
    return key_join(node_key_prefix(prefix, node_name), SUBNODES)

def method_response_from_call(key_expr: str):
    return key_join(key_expr, RESPONSE)

def overlap(key1: str, key2: str):
    # incredibly simple algorithm to handle * semantics like zenoh does
    # TODO: handle ** and ? in the future
    key1_split = key1.split('/')
    key2_split = key2.split('/')
    if len(key1_split) != len(key2_split):
        return False
    
    for key1_component, key2_component in zip(key1_split, key2_split):
        if key1_component != "*" and key2_component != "*" and key1_component != key2_component:
            return False
    return True

# this defines a key prefix and a name
class NodeKeySpace:
    def __init__(self, prefix: str, name: str):
        self._prefix = prefix
        self._name = name
        self._user_key = key_join(prefix, name)
        self._set_keys(self.prefix, self.name)

    @classmethod
    def from_user_key(cls, key: str):
        prefix, name = NodeKeySpace.split_user_key(key)
        return cls(prefix, name)
    
    @classmethod
    def from_internal_key(cls, key_expr: str):
        prefix = NodeKeySpace.prefix_from_key(key_expr)
        name = NodeKeySpace.name_from_key(key_expr)
        return cls(prefix, name)

    @staticmethod
    def split_user_key(key: str):
        key = key.strip('/')
        if '/' not in key:
            raise ValueError(f"key '{key}' must include at least one '/'")
        prefix, _, name = key.rpartition('/')
        return prefix, name

    @staticmethod
    def name_from_key(key_expr: str):
        components = key_expr.split("/")
        return components[components.index(NODE) + 1]

    @staticmethod
    def prefix_from_key(key_expr: str):
        components = key_expr.split(NODE)
        return components[0]
    
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
        return key_join(*components[(i + 1):])
    
    @staticmethod
    def method_path_from_key(key_expr: str):
        components = key_expr.split("/")
        try:
            i = components.index(METHODS)
        except:
            raise ValueError(f"No method path found in {key_expr}")
        return key_join(*components[(i + 1):])

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
        self.method_key_prefix = method_key_prefix(prefix, name)
        self.subnodes_key_prefix = subnodes_key_prefix(prefix, name)
    
    def tag_data_path(self, path: str):
        return tag_data_key(self.prefix, self.name, path)
    
    def tag_write_path(self, path: str):
        return tag_write_key(self.prefix, self.name, path)
    
    def method_path(self, path: str):
        return key_join(self.method_key_prefix, path)
        
    def method_query(self, path: str, caller_id: str, method_query_id: str):
        return key_join(self.method_path(path), caller_id, method_query_id)
    
    def method_response(self, path: str, caller_id: str, method_query_id: str):
        return key_join(self.method_path(path), caller_id, method_query_id, RESPONSE)
    
    def method_query_listen(self, path: str):
        # the two * signify caller_id and method_query_id, but we should not subscribe to responses
        return key_join(self.method_path(path), "*", "*")
    
    def contains(self, key_expr: str):
        name = self.name_from_key(key_expr)
        prefix = self.prefix_from_key(key_expr)
        return name == self.name and prefix == self.prefix
    
    def __repr__(self) -> str:
        return self.node_key_prefix
    
class SubnodeKeySpace(NodeKeySpace):
    def __init__(self, node_prefix: str, node_name: str, subnode_name: str, subnodes: list[str] = []):
        self._prefix = node_prefix
        self._name = node_name

        self.node_prefix = node_prefix
        self.node_name = node_name
        self.subnode_name = subnode_name
        self.subnodes = subnodes # subnodes before
        self._set_keys(node_prefix, node_name, subnode_name, subnodes)

    # for now, we are not going to worry about the ability to set the 
    # name to a new value and such, we will assume that once the user sets the 
    # name, it's not going to change
    def _set_keys(self, prefix: str, node_name: str, subnode_name: str, subnodes: list[str]):
        sequence = key_join(*[key_join(SUBNODES, s) for s in subnodes + [subnode_name]])
        key_prefix = key_join(node_key_prefix(prefix, node_name), sequence)
        self.subnode_key_prefix = key_prefix
        self.state_key_prefix = key_join(key_prefix, STATE)
        self.tag_data_key_prefix = key_join(key_prefix, TAGS, DATA)
        self.tag_write_key_prefix = key_join(key_prefix, TAGS, WRITE)
        self.method_key_prefix = key_join(key_prefix, METHODS)
        self.subnodes_key_prefix = key_join(key_prefix, SUBNODES)
    
    @classmethod
    def from_node(cls, ks: NodeKeySpace, name: str):
        if isinstance(ks, SubnodeKeySpace):
            prefix = ks.node_prefix
            node_name = ks.node_name
            subnode_name = name
            subnodes = ks.subnodes + [ks.subnode_name]
            return cls(prefix, node_name, subnode_name, subnodes)
        return cls(ks.prefix, ks.name, name, [])
    
    @classmethod
    def from_subnode(cls, ks: SubnodeKeySpace, name: str):
        subnode_name = name
        subnodes = ks.subnodes + [ks.subnode_name]
        return cls(ks.prefix, ks.name, subnode_name, subnodes)

    def tag_data_path(self, path: str):
        return key_join(self.tag_data_key_prefix, path)
    
    def tag_write_path(self, path: str):
        return key_join(self.tag_write_key_prefix, path)
    
    def method_path(self, path: str):
        return key_join(self.method_key_prefix, path)
        
    def method_query(self, path: str, caller_id: str, method_query_id: str):
        return key_join(self.method_path(path), caller_id, method_query_id)
    
    def method_response(self, path: str, caller_id: str, method_query_id: str):
        return key_join(self.method_path(path), caller_id, method_query_id, RESPONSE)
    
    def method_query_listen(self, path: str):
        # the two * signify caller_id and method_query_id, but we should not subscribe to responses
        return key_join(self.method_path(path), "*", "*")
    
    def __repr__(self) -> str:
        return self.subnode_key_prefix

if __name__ == "__main__":
    ks = SubnodeKeySpace("hello", "mom", "subnode2", ["subnode1"])
    print(ks.subnode_key_prefix)
    print(ks.state_key_prefix)
    print(ks.tag_data_path("hello"))
    print(ks.tag_write_path("hello"))
    print(ks.method_key_prefix)
