import zenoh

def node_key_prefix(prefix: str, name: str):
    node_key_prefix = prefix + f"/NODE/{name}"
    return node_key_prefix

def meta_key_prefix(prefix: str, name: str):
    meta_key_prefix = prefix + f"/NODE/{name}/META"
    return meta_key_prefix

def tag_data_key_prefix(prefix: str, name: str):
    return node_key_prefix(prefix, name) + "/TAGS/DATA"

def tag_data_key_expr(prefix: str, name: str, tag_key_expr: str):
    return node_key_prefix(prefix, name) + f"/TAGS/DATA/{tag_key_expr}"

def tag_write_key_prefix(prefix: str, name: str):
    return node_key_prefix(prefix, name) + "/TAGS/WRITE"

def state_key_prefix(prefix: str, name: str):
    return node_key_prefix(prefix, name) + "/STATE"

def liveliness_key_prefix(prefix: str, name: str):
    return node_key_prefix(prefix, name)

def node_name_from_key_expr(key_expr: str | zenoh.KeyExpr):
    components = str(key_expr).split("/")
    return components[components.index("NODE") + 1]