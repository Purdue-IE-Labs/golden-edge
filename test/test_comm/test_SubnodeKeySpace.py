import gedge
import pytest

from gedge.comm import keys
from gedge.comm.keys import NodeKeySpace
from gedge.comm.keys import SubnodeKeySpace

class TestInitialize:
    def test_all_filled(self):
        parent_instance = NodeKeySpace.from_user_key("prefix/name")
        subnode_instance = SubnodeKeySpace(parent_instance, "subname")

        assert subnode_instance.prefix == parent_instance.prefix
        assert subnode_instance.name == parent_instance.name
        assert subnode_instance.user_key == "prefix/name"
        assert subnode_instance.subnode_name == "subname"
        assert subnode_instance._parent == parent_instance
        
        assert subnode_instance.subnode_key_prefix == "prefix/NODE/name/SUBNODES/subname"
        assert subnode_instance.state_key_prefix == "prefix/NODE/name/SUBNODES/subname/STATE"
        assert subnode_instance.tag_data_key_prefix == "prefix/NODE/name/SUBNODES/subname/TAGS/DATA"
        assert subnode_instance.tag_write_key_prefix == "prefix/NODE/name/SUBNODES/subname/TAGS/WRITE"
        assert subnode_instance.method_key_prefix == "prefix/NODE/name/SUBNODES/subname/METHODS"
        assert subnode_instance.subnodes_key_prefix == "prefix/NODE/name/SUBNODES/subname/SUBNODES"
    
    def test_no_parent(self):
        with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'prefix'"):
            SubnodeKeySpace(None, "subname")

    def test_no_name(self):
        parent_instance = NodeKeySpace.from_user_key("prefix/name")
        subnode_instance = SubnodeKeySpace(parent_instance, "")

        assert subnode_instance.prefix == parent_instance.prefix
        assert subnode_instance.name == parent_instance.name
        assert subnode_instance.user_key == "prefix/name"
        assert subnode_instance.subnode_name == ""
        assert subnode_instance._parent == parent_instance
        
        assert subnode_instance.subnode_key_prefix == "prefix/NODE/name/SUBNODES/"
        assert subnode_instance.state_key_prefix == "prefix/NODE/name/SUBNODES//STATE"
        assert subnode_instance.tag_data_key_prefix == "prefix/NODE/name/SUBNODES//TAGS/DATA"
        assert subnode_instance.tag_write_key_prefix == "prefix/NODE/name/SUBNODES//TAGS/WRITE"
        assert subnode_instance.method_key_prefix == "prefix/NODE/name/SUBNODES//METHODS"
        assert subnode_instance.subnodes_key_prefix == "prefix/NODE/name/SUBNODES//SUBNODES"