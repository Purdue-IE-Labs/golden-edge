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
    '''
    Joins the passed components

    Example Implementation:
        key = key_join("part0", "part1", "part2")
        key ==> "part0/part1/part2"

    Arguments:
        *components (tuple[str, ...]): The list of components to be joined

    Returns:
        str: The passed components with a slash between each component 
    '''
    return "/".join(components)

def node_key_prefix(prefix: str, name: str):
    '''
    Creates a node key prefix with the passed prefix and name

    Example Implementation:
        key = node_key_prefix("prefix", "name")
        key ==> "prefix/NODE/name"

    Arguments:
        prefix (str): The prefix of the node
        name (str): The name of the node

    Returns:
        str: The joined node key
    '''
    return key_join(prefix, NODE, name)

def meta_key_prefix(prefix: str, name: str):
    '''
    Creates a meta key prefix with the passed prefix and name

    Example Implementation:
        key = meta_key_prefix("prefix", "name")
        key ==> "prefix/NODE/name/META"
    
    Arguments:
        prefix (str): The prefix of the node
        name (str): The name of the node

    Returns:
        str: The joined meta key
    '''
    return key_join(prefix, NODE, name, META)

def tag_data_key_prefix(prefix: str, name: str):
    '''
    Creates a tag data key prefix with the passed prefix and name

    Example Implementation:
        key = tag_data_key_prefix("prefix", "name")
        key ==> "prefix/NODE/name/TAGS/DATA"

    Arguments:
        prefix (str): The prefix of the node
        name (str): The name of the node

    Returns:
        str: The joined tag data key prefix
    '''
    return key_join(node_key_prefix(prefix, name), TAGS, DATA)

def tag_data_key(prefix: str, name: str, key: str):
    '''
    Creates a tag data key with the passsed prefix, name, and key

    Example Implementation:
        key = tag_data_key("prefix", "name", "key")
        key ==> "prefix/NODE/name/TAGS/DATA/key"

    Arguments:
        prefix (str): The prefix of the node
        name (str): The name of the node
        key (str): The key of the tag

    Returns:
        str: The joined tag data key
    '''
    return key_join(node_key_prefix(prefix, name), TAGS, DATA, key)

def tag_write_key_prefix(prefix: str, name: str):
    '''
    Creates a tag write key prefix with the passed prefix and name

    Example Implementation:
        key = tag_write_key_prefix("prefix", "name")
        key ==> "prefix/NODE/name/TAGS/WRITE"

    Arguments:
        prefix (str): The prefix of the node
        name (str): The name of the node

    Returns:
        str: The joined tag write key prefix
    '''
    return key_join(node_key_prefix(prefix, name), TAGS, WRITE)

def tag_write_key(prefix: str, name: str, key: str):
    '''
    Creates a tag write key with the passed prefix, name, and key

    Example Implementation:
        key = tag_write_key("prefix", "name", "key")
        key ==> "prefix/NODE/name/TAGS/WRITE/key"

    Arguments:
        prefix (str): The prefix of the node
        name (str): The name of the node
        key (str): The key of the tag

    Returns:
        str: The joined tag write key
    '''
    return key_join(node_key_prefix(prefix, name), TAGS, WRITE, key)

def state_key_prefix(prefix: str, name: str):
    '''
    Creates a state key prefix with the passed prefix and name

    Example Implementation:
        key = state_key_prefix("prefix", "name")
        key ==> "prefix/NODE/name/STATE"
    
    Arguments:
        prefix (str): The prefix of the node
        name (str): The name of the node

    Returns:
        str: The joined state key prefix
    '''
    return key_join(node_key_prefix(prefix, name), STATE)

def method_key_prefix(prefix: str, name: str):
    '''
    Creates a method key prefix with the passed prefix and name

    Example Implementation:
        key = method_key_prefix("prefix", "name")
        key ==> "prefix/NODE/name/METHODS"

    Arguments:
        prefix (str): The prefix of the node
        name (str): The name of the node

    Returns:
        str: The joined method key prefix
    '''
    return key_join(node_key_prefix(prefix, name), METHODS)

def liveliness_key_prefix(prefix: str, name: str):
    '''
    Creates a liveliness key prefix with the passed prefix and name

    Example Implementation:
        key = liveliness_key_prefix("prefix", "name")
        key ==> "prefix/NODE/name"

    Arguments:
        prefix (str): The prefix of the node
        name (str): The name of the node

    Returns:
        str: The joined liveliness key prefix
    '''
    return node_key_prefix(prefix, name)

def subnodes_key_prefix(prefix: str, node_name: str):
    '''
    Creates a subnodes key prefix with the passed prefix and node_name

    Example Implementation:
        key = subnodes_key_prefix("prefix", "node_name")
        key ==> "prefix/NODE/node_name/SUBNODES"

    Arguments:
        prefix (str): The prefix of the node
        name (str): the name of the node

    Returns:
        str: The joined subnodes key prefix
    '''
    return key_join(node_key_prefix(prefix, node_name), SUBNODES)

def method_response_from_call(key_expr: str):
    '''
    Creates a method response from call key with the passed key expression

    Example Implementation:
        key = method_response_from_call("key_expr")
        key ==> "key_expr/RESPONSE"

    Arguments:
        key_expr (str): The key expression of the node the method belongs to

    Returns:
        str: The joined method response from call key
    '''
    return key_join(key_expr, RESPONSE)

def internal_to_user_key(key_expr: str):
    '''
    Creates a user key from the passed key expression corresponding to a given node

    Arguments:
        key_expr (str): The key expression of the node

    Returns:
        str: The joined user key
    '''
    prefix = NodeKeySpace.prefix_from_key(key_expr)
    name = NodeKeySpace.name_from_key(key_expr)
    return key_join(prefix, name)

def overlap(key1: str, key2: str):
    '''
    Returns a boolean representing the overlap of two keys given wildcarding

    Example Implementation:
        overlap("a/\\*/c", "a/b/c")
        This would return true since the wildcard in the first key could be a b
        overlap("a/b", "a/\\*/c")
        This would return false since the lengths of the two components are different
        overlap("a/\\*/c", "a/\\*/d")
        This would return false since the non-wildcards components don't match
        

    Arguments:
        key1 (str): The first key being compared
        key2 (str): The second key being compared

    Returns:
        bool: Whether the keys overlap or not
    '''
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
        '''
        Creates a new NodeKeySpace object using the passed user key

        Arguments:
            key (str): The user key used create NodeKeySpace

        Returns:
            NodeKeySpace: The new NodeKeySpace object

        '''
        prefix, name = NodeKeySpace.split_user_key(key)
        return cls(prefix, name)
    
    @classmethod
    def from_internal_key(cls, key_expr: str):
        '''
        Creates a new NodeKeySpace object using the passed internal key

        Arguments:
            key_expr (str): The internal key used to create the NodeKeySpace

        Returns:
            NodeKeySpace: The new NodeKeySpace object
        '''
        prefix = NodeKeySpace.prefix_from_key(key_expr)
        name = NodeKeySpace.name_from_key(key_expr)
        return cls(prefix, name)

    @staticmethod
    def split_user_key(key: str):
        '''
        Splits the passed user key into a prefix and name

        Note: The split key is returned in the order: prefix, name
        
        Arguments:
                key (str): The user key being split
        
        Returns:
                tuple[str, str]: The parsed
        '''
        key = key.strip('/')
        if '/' not in key:
            raise ValueError(f"key '{key}' must include at least one '/'")
        prefix, _, name = key.rpartition('/')
        return prefix, name

    @staticmethod
    def name_from_key(key_expr: str):
        '''
        Splits the passed internal key and returns the name element

        Note: This function is dependent on NODE being in the path

        Arguments:
            key_expr (str): The internal key containing the name

        Returns:
            str: The parsed name
        '''
        components = key_expr.split("/")
        return components[components.index(NODE) + 1]

    @staticmethod
    def prefix_from_key(key_expr: str):
        '''
        Splits the passed internal key and returns the prefix element

        Note: This function is dependent on NODE being in the path

        Arguments:
            key_expr (str): The internal key containing the prefix

        Returns:
            str: The parsed prefix
        '''
        if 'NODE' not in key_expr:
            raise ValueError("'NODE' is not in list")
        components = key_expr.split("/NODE")
        return components[0]
    
    @staticmethod
    def internal_to_user_key(key_expr: str):
        '''
        Splits the passed internal key and returnes a joined user key

        Note: This function is dependent on NODE being in the path

        Arguments:
            key_expr (str): The internal key containing the user key

        Returns:
            str: The parsed user key

        '''
        prefix = NodeKeySpace.prefix_from_key(key_expr)
        name = NodeKeySpace.name_from_key(key_expr)
        return key_join(prefix, name)
    
    @staticmethod
    def tag_path_from_key(key_expr: str):
        '''
        Splits the passed internal key and returns a joined tag path

        Note: This function is dependent on DATA or WRITE being in the path

        Arguments:
            key_expr (str): The internal key containing the tag path

        Returns:
            str: The parsed tag path
        '''
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
    def method_path_from_call_key(key_expr: str):
        '''
        Splits the passed internal key and returns a joined method path

        Note: This function is dependent on METHODS being in the path

        Arguments:
            key_expr (str): The internal key containing the method path

        Returns:
            str: The parsed method path
        '''
        components = key_expr.split("/")
        try:
            i = components.index(METHODS)
        except:
            raise ValueError(f"No method path found in {key_expr}")
        return key_join(*components[(i + 1):(len(components) - 2)])

    @staticmethod
    def method_path_from_response_key(key_expr: str):
        '''
        Splits the passed response key and returns a joined method path

        Note: This function is dependent on METHODS being in the path

        Arguments:
            key_expr (str): The response key containing the method path

        Returns:
            str: The parsed method path
        '''
        key_expr = NodeKeySpace.method_path_from_call_key(key_expr)
        components = key_expr.split("/")
        return key_join(*components[:-1])
    
    @staticmethod
    def user_key_from_key(key_expr: str):
        '''
        Splits the passed internal key and returns a joined user key

        Note: This function is dependent on NODE being in the path

        Arguments:
            key_expr (str): The internal key containing the the user key


        Returns:
            str: The parsed user key
        '''
        components = key_expr.split("/")
        try:
            i = components.index(NODE)
        except:
            raise ValueError(f"Invalid key expr {key_expr}")
        return key_join(*components[:i], components[i + 1])

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
        '''
        Sets all of the keys for the NodeKeySpace object

        Note: These keys include: node, meta, state, tag_data, tag_write, liveliness, method, and subnodes
        '''
        self.node_key_prefix = node_key_prefix(prefix, name)
        self.meta_key_prefix = meta_key_prefix(prefix, name)
        self.state_key_prefix = state_key_prefix(prefix, name)
        self.tag_data_key_prefix = tag_data_key_prefix(prefix, name)
        self.tag_write_key_prefix = tag_write_key_prefix(prefix, name)
        self.liveliness_key_prefix = liveliness_key_prefix(prefix, name)
        self.method_key_prefix = method_key_prefix(prefix, name)
        self.subnodes_key_prefix = subnodes_key_prefix(prefix, name)
    
    def tag_data_path(self, path: str):
        '''
        Creates a tag data path key using the passed path

        Arguments:
            path (str): The path being appended to the end of the tag data key

        Returns:
            (str): The tag_data_key_prefix with path appended to the end 
        '''
        return key_join(self.tag_data_key_prefix, path)
    
    def tag_write_path(self, path: str):
        '''
        Creates a tag write path key using the passed path

        Arguments:
            path (str): The path being appended to the end of the tag write key

        Returns:
            (str): The tag_write_key_prefix with path appended to the end 
        '''
        return key_join(self.tag_write_key_prefix, path)
    
    def method_path(self, path: str):
        '''
        Creates a method path key using the passed path

        Arguments:
            path (str): The path being appended to the end of the method key

        Returns:
            (str): The method_key_prefix with path appended to the end 
        '''
        return key_join(self.method_key_prefix, path)
        
    def method_query(self, path: str, caller_id: str, method_query_id: str):
        '''
        Creates a method query key using the passed path, caller_id, and method_query_id

        Arguments:
            path (str): The path being appended to the end of the method key
            caller_id (str): The id of the caller for the query
            method_query_id (str): The id of the method being queried

        Returns:
            (str): The method_key_prefix with path, caller_id, and method_query_id appended to the end 
        '''
        return key_join(self.method_path(path), caller_id, method_query_id)
    
    def method_response(self, path: str, caller_id: str, method_query_id: str):
        '''
        Creates a method response key using the passed path, caller_id, and method_query_id

        Arguments:
            path (str): The path being appended to the end of the method key
            caller_id (str): The id of the caller for the query
            method_query_id (str): The id of the method being queried

        Returns:
            (str): The method_key_prefix with path, caller_id, method_query_id, and RESPONSE appended to the end 
        '''
        return key_join(self.method_path(path), caller_id, method_query_id, RESPONSE)
    
    def method_query_listen(self, path: str):
        '''
        Creates a method response key using the passed path

        Note: The two asterisks signify caller_id and method_id, but show that there is not a subscription to responses

        Arguments:
            path (str): The path being appended to the end of the method key

        Returns:
            (str): The method_key_prefix with path and two asterisks appended to the end 
        '''
        # the two * signify caller_id and method_query_id, but we should not subscribe to responses
        return key_join(self.method_path(path), "*", "*")
    
    def contains(self, key_expr: str):
        '''
        Checks if the curent NodeKeySpace contains the passed internal key

        Arguments:
            key_expr (str): The internal key being compared to

        Returns:
            bool: Whether the current NodeKeySpace contains the passed internal key
        '''
        name = self.name_from_key(key_expr)
        prefix = self.prefix_from_key(key_expr)
        return name == self.name and prefix == self.prefix
    
    def __repr__(self) -> str:
        return self.node_key_prefix
    
class SubnodeKeySpace(NodeKeySpace):
    def __init__(self, parent: NodeKeySpace, subnode_name: str):
        self._prefix = parent.prefix
        self._name = parent.name
        self._user_key = key_join(self._prefix, self._name)
        self._subnode_name = subnode_name
        self._parent = parent
        self._set_sub_keys(subnode_name)
    
    @property
    def subnode_name(self):
        return self._subnode_name
    
    @subnode_name.setter
    def subnode_name(self, value):
        self._subnode_name = value
        self._set_sub_keys(value)

    def _set_keys(self, prefix: str, name: str):
        '''
        Sets all of the keys for the parent NodeKeySpace object and then the child SubnodeKeySpace object

        Note: These keys include: node, meta, state, tag_data, tag_write, liveliness, method, and subnodes
        '''
        self._parent._set_keys(prefix, name)
        self._set_sub_keys(self.subnode_name)

    def _set_sub_keys(self, subnode_name: str):
        '''
        Sets all of the keys for the SubnodeKeySpace object

        Note: This is essentially _set_keys, it includes the parent key, SUBNODES, the subnode name, and then the corresponding keys for the SubnodeKeySpace
        '''
        key_prefix = key_join(self._parent.__repr__(), SUBNODES, subnode_name)
        self.subnode_key_prefix = key_prefix
        self.state_key_prefix = key_join(key_prefix, STATE)
        self.tag_data_key_prefix = key_join(key_prefix, TAGS, DATA)
        self.tag_write_key_prefix = key_join(key_prefix, TAGS, WRITE)
        self.method_key_prefix = key_join(key_prefix, METHODS)
        self.subnodes_key_prefix = key_join(key_prefix, SUBNODES)

    def __repr__(self) -> str:
        return self.subnode_key_prefix
