import gedge
import pytest

from gedge.comm import keys


def test_key_join():
    expected_key = "part0/part1/part2"
    
    assert expected_key == keys.key_join("part0", "part1", "part2")

def test_key_join_none_param():
    assert '' == keys.key_join()

def test_node_key_prefix():
    expected_key = "I/love/NODESSSSSSS/NODE/My_Favorite_Node :)"

    assert expected_key == keys.node_key_prefix(prefix="I/love/NODESSSSSSS", name="My_Favorite_Node :)")

def test_node_key_prefix_none_param():
    #TODO
    pytest.fail("Test has not been created")

def test_meta_key_prefix():
    expected_key = "Me when Meta/NODE/This is a Meta Name/META"
    
    assert expected_key == keys.meta_key_prefix(prefix="Me when Meta", name="This is a Meta Name")

def test_meta_key_prefix_no_param():
    #TODO
    pytest.fail("Test has not been created")

def test_tag_data_key_prefix():
    expected_key = "I be testing, aw yeah/NODE/Jonas :)/TAGS/DATA"
    
    assert expected_key == keys.tag_data_key_prefix(prefix="I be testing, aw yeah", name="Jonas :)")

def test_tag_data_key_prefix_no_param():
    #TODO
    pytest.fail("Test has not been created")

def test_tag_data_key():
    print(keys.tag_data_key(prefix="", name="", key=""))
    
    #TODO
    pytest.fail("Test has not been created")

def test_tag_data_key_no_param():
    #TODO
    pytest.fail("Test has not been created")

def test_tag_write_key_prefix():
    #TODO
    pytest.fail("Test has not been created")

def test_tag_write_key_prefix_no_param():
    #TODO
    pytest.fail("Test has not been created")

def test_tag_write_key():
    #TODO
    pytest.fail("Test has not been created")

def test_tag_write_key_no_param():
    #TODO
    pytest.fail("Test has not been created")

def test_state_key_prefix():
    #TODO
    pytest.fail("Test has not been created")

def test_state_key_prefix_no_param():
    #TODO
    pytest.fail("Test has not been created")

def test_method_key_prefix():
    #TODO
    pytest.fail("Test has not been created")

def test_method_key_prefix_no_param():
    #TODO
    pytest.fail("Test has not been created")

def test_liveliness_key_prefix():
    #TODO
    pytest.fail("Test has not been created")

def test_liveliness_key_prefix_no_param():
    #TODO
    pytest.fail("Test has not been created")

def test_subnodes_key_prefix():
    #TODO
    pytest.fail("Test has not been created")

def test_subnodes_key_prefix_no_param():
    #TODO
    pytest.fail("Test has not been created")

def test_method_response_from_call():
    #TODO
    pytest.fail("Test has not been created")

def test_method_response_from_call_no_param():
    #TODO
    pytest.fail("Test has not been created")

def test_internal_to_user_key():
    #TODO
    pytest.fail("Test has not been created")

def test_internal_to_user_key_no_param():
    #TODO
    pytest.fail("Test has not been created")

def test_overlap():
    #TODO
    pytest.fail("Test has not been created")

def test_overlap_no_param():
    #TODO
    pytest.fail("Test has not been created")
