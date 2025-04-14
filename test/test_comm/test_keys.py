import gedge
import pytest

from gedge.comm import keys


def test_key_join():
    expected_key = "part0/part1/part2"
    
    assert expected_key == keys.key_join("part0", "part1", "part2")

def test_key_join_empty_param():
    assert '' == keys.key_join()

def test_node_key_prefix():
    expected_key = "prefix/NODE/name"

    assert expected_key == keys.node_key_prefix(prefix="prefix", name="name")

def test_node_key_prefix_empty_param():
    expected_key = "/NODE/"
    assert  expected_key == keys.node_key_prefix(prefix="", name="")
    

def test_meta_key_prefix():
    expected_key = "prefix/NODE/name/META"
    
    assert expected_key == keys.meta_key_prefix(prefix="prefix", name="name")

def test_meta_key_prefix_empty_param():
    expected_key = "/NODE//META"

    assert expected_key == keys.meta_key_prefix(prefix="", name="")

def test_tag_data_key_prefix():
    expected_key = "prefix/NODE/name/TAGS/DATA"
    
    assert expected_key == keys.tag_data_key_prefix(prefix="prefix", name="name")

def test_tag_data_key_prefix_empty_param():
    expected_key = "/NODE//TAGS/DATA"

    assert expected_key == keys.tag_data_key_prefix(prefix="", name="")

def test_tag_data_key():
    expected_key = "prefix/NODE/name/TAGS/DATA/key"
    
    assert expected_key == keys.tag_data_key(prefix="prefix", name="name", key="key")

def test_tag_data_key_empty_param():
    expected_key = "/NODE//TAGS/DATA/"
    
    assert expected_key == keys.tag_data_key(prefix="", name="", key="")

def test_tag_write_key_prefix():
    expected_key = "prefix/NODE/name/TAGS/WRITE"

    assert expected_key == keys.tag_write_key_prefix(prefix="prefix", name="name")

def test_tag_write_key_prefix_empty_param():
    expected_key = "/NODE//TAGS/WRITE"

    assert expected_key == keys.tag_write_key_prefix(prefix="", name="")

def test_tag_write_key():
    expected_key = "prefix/NODE/name/TAGS/WRITE/key"
    
    assert expected_key == keys.tag_write_key(prefix="prefix", name="name", key="key")

def test_tag_write_key_empty_param():
    expected_key = "/NODE//TAGS/WRITE/"

    assert expected_key == keys.tag_write_key(prefix="", name="", key="")

def test_state_key_prefix():
    expected_key = "prefix/NODE/name/STATE"

    assert expected_key == keys.state_key_prefix(prefix="prefix", name="name")

def test_state_key_prefix_empty_param():
    expected_key = "/NODE//STATE"

    assert expected_key == keys.state_key_prefix(prefix="", name="")

def test_method_key_prefix():
    expected_key = "prefix/NODE/name/METHODS"
    
    assert expected_key == keys.method_key_prefix(prefix="prefix", name="name")

def test_method_key_prefix_empty_param():
    expected_key = "/NODE//METHODS"
    
    assert expected_key == keys.method_key_prefix(prefix="", name="")

def test_liveliness_key_prefix():
    expected_key = "prefix/NODE/name"

    assert expected_key == keys.liveliness_key_prefix(prefix="prefix", name="name")

def test_liveliness_key_prefix_empty_param():
    expected_key = "/NODE/"

    assert expected_key == keys.liveliness_key_prefix(prefix="", name="")

def test_subnodes_key_prefix():
    expected_key = "prefix/NODE/node_name/SUBNODES"

    assert expected_key == keys.subnodes_key_prefix(prefix="prefix", node_name="node_name")

def test_subnodes_key_prefix_empty_param():
    expected_key = "/NODE//SUBNODES"

    assert expected_key == keys.subnodes_key_prefix(prefix="", node_name="")

def test_method_response_from_call():
    expected_key = "key_expr/RESPONSE"

    assert expected_key == keys.method_response_from_call(key_expr="key_expr")

def test_method_response_from_call_empty_param():
    expected_key = "/RESPONSE"

    assert expected_key == keys.method_response_from_call(key_expr="")

def test_internal_to_user_key():
    node_key = keys.node_key_prefix(prefix="prefix", name="node")

    print(node_key)

    expected_key = "prefix//node"

    assert expected_key == keys.internal_to_user_key(key_expr=node_key)

def test_internal_to_user_key_empty_param():
    with pytest.raises(ValueError, match="'NODE' is not in list"):
        keys.internal_to_user_key(key_expr="")

class TestOverlap:
    def test_overlap_one_wildcard_true(self):
        assert keys.overlap(key1="*/NODE/name", key2="*/NODE/name") == True

    def test_overlap_more_than_one_wildcard_true(self):
        assert keys.overlap(key1="*/*/name", key2="*/*/name") == True

    def test_overlap_more_than_all_wildcards_true(self):
        assert keys.overlap(key1="*/*/*", key2="*/*/*") == True

    def test_overlap_length_diff(self):
        assert keys.overlap(key1="1/2/3", key2="1/2") == False

    def test_overlap_component_diff(self):
        assert keys.overlap(key1="a/*/c", key2="a/*/d") == False