import gedge
import pytest

from gedge.comm import keys
from gedge.comm.keys import NodeKeySpace

class TestInitialize:
    params = [
        ("prefix", "name"),
        ("", "name"),
        ("prefix", ""),
        ("", "")
    ]

    params_special = [
        ("prefix", "name"),
        ("", "name"),
        ("prefix", ""),
        ("", ""),
        ("EMPTY", "EMPTY")
    ]

    ids = [
        "All Filled",
        "No Prefix",
        "No Name",
        "No Arguments"
    ]

    ids_special = [
        "All Filled",
        "No Prefix",
        "No Name",
        "No Arguments",
        "Completely Empty"
    ]

    @pytest.mark.parametrize("prefix, name", params, ids=ids)
    def test_basic_initialization(self, prefix, name):
        instance = NodeKeySpace(prefix=prefix, name=name)

        assert instance.prefix == f"{prefix}"
        assert instance.name == f"{name}"
        assert instance.user_key == f"{prefix}/{name}"

        assert instance.node_key_prefix == f"{prefix}/NODE/{name}"
        assert instance.meta_key_prefix == f"{prefix}/NODE/{name}/META"
        assert instance.state_key_prefix == f"{prefix}/NODE/{name}/STATE"
        assert instance.tag_data_key_prefix == f"{prefix}/NODE/{name}/TAGS/DATA"
        assert instance.tag_write_key_prefix == f"{prefix}/NODE/{name}/TAGS/WRITE"
        assert instance.liveliness_key_prefix == f"{prefix}/NODE/{name}"
        assert instance.method_key_prefix == f"{prefix}/NODE/{name}/METHODS"
        assert instance.subnodes_key_prefix == f"{prefix}/NODE/{name}/SUBNODES"

    @pytest.mark.parametrize("prefix, name", params, ids=ids)
    def test_from_user_key(self, prefix, name):
        if (prefix == '' and name == ''):
            with pytest.raises(ValueError, match="key '' must include at least one '/'"):
                NodeKeySpace.from_user_key(f"{prefix}/{name}")
        elif (prefix == ''):
            with pytest.raises(ValueError, match="key 'name' must include at least one '/'"):
                NodeKeySpace.from_user_key(f"{prefix}/{name}")
        elif (name == ''):
            with pytest.raises(ValueError, match="key 'prefix' must include at least one '/'"):
                NodeKeySpace.from_user_key(f"{prefix}/{name}")
        else:
            instance = NodeKeySpace.from_user_key(f"{prefix}/{name}")

            assert instance.prefix == prefix
            assert instance.name == name
            assert instance.user_key == f"{prefix}/{name}"

            assert instance.node_key_prefix == f"{prefix}/NODE/{name}"
            assert instance.meta_key_prefix == f"{prefix}/NODE/{name}/META"
            assert instance.state_key_prefix == f"{prefix}/NODE/{name}/STATE"
            assert instance.tag_data_key_prefix == f"{prefix}/NODE/{name}/TAGS/DATA"
            assert instance.tag_write_key_prefix == f"{prefix}/NODE/{name}/TAGS/WRITE"
            assert instance.liveliness_key_prefix == f"{prefix}/NODE/{name}"
            assert instance.method_key_prefix == f"{prefix}/NODE/{name}/METHODS"
            assert instance.subnodes_key_prefix == f"{prefix}/NODE/{name}/SUBNODES"

    @pytest.mark.parametrize("prefix, name", params_special, ids=ids_special)
    def test_from_internal_key(self, prefix, name):
        if (prefix == "EMPTY" and name == "EMPTY"):
            with pytest.raises(ValueError, match="'NODE' is not in list"):
                NodeKeySpace.from_internal_key("")
        instance = NodeKeySpace.from_internal_key(f"{prefix}/NODE/{name}")

        assert instance.prefix == prefix
        assert instance.name == name
        assert instance.user_key == f"{prefix}/{name}"

        assert instance.node_key_prefix == f"{prefix}/NODE/{name}"
        assert instance.meta_key_prefix == f"{prefix}/NODE/{name}/META"
        assert instance.state_key_prefix == f"{prefix}/NODE/{name}/STATE"
        assert instance.tag_data_key_prefix == f"{prefix}/NODE/{name}/TAGS/DATA"
        assert instance.tag_write_key_prefix == f"{prefix}/NODE/{name}/TAGS/WRITE"
        assert instance.liveliness_key_prefix == f"{prefix}/NODE/{name}"
        assert instance.method_key_prefix == f"{prefix}/NODE/{name}/METHODS"
        assert instance.subnodes_key_prefix == f"{prefix}/NODE/{name}/SUBNODES"

def test_split_user_key_valid():
    expected = ("prefix", "name")
    assert expected == NodeKeySpace.split_user_key("prefix/name")

def test_split_user_key_no_slash():
    with pytest.raises(ValueError, match="key 'prefixname' must include at least one '/'"):
        NodeKeySpace.split_user_key("prefixname")

def test_name_from_key_full_path():
    expected = "name"
    assert expected == NodeKeySpace.name_from_key("prefix/NODE/name")

def test_name_from_key_partial_path():
    expected = "name"
    assert expected == NodeKeySpace.name_from_key("/NODE/name")

def test_name_from_key_no_path():
    with pytest.raises(ValueError, match="'NODE' is not in list"):
        NodeKeySpace.name_from_key("")

def test_prefix_from_key_full_path():
    expected = "prefix"
    assert expected == NodeKeySpace.prefix_from_key("prefix/NODE/name")

def test_prefix_from_key_partial_path():
    expected = "prefix"
    assert expected == NodeKeySpace.prefix_from_key("prefix/NODE/")

def test_prefix_from_key_no_path():
    expected = ""
    assert expected == NodeKeySpace.prefix_from_key("")

def test_internal_to_user_key_full_path():
    expected = "prefix/name"
    assert expected == NodeKeySpace.internal_to_user_key("prefix/NODE/name")

def test_internal_to_user_key_partial_front_path():
    expected = "prefix/"
    assert expected == NodeKeySpace.internal_to_user_key("prefix/NODE/")

def test_internal_to_user_key_partial_back_path():
    expected = "/name"
    assert expected == NodeKeySpace.internal_to_user_key("/NODE/name")

def test_internal_to_user_key_no_path():
    with pytest.raises(ValueError, match="'NODE' is not in list"):
        NodeKeySpace.internal_to_user_key("")

def test_tag_path_from_key():
    expected = "key"
    assert expected == NodeKeySpace.tag_path_from_key("prefix/NODE/name/TAGS/WRITE/key")

    expected = "key"
    assert expected == NodeKeySpace.tag_path_from_key("prefix/NODE/name/TAGS/DATA/key")

    expected = ""
    assert expected == NodeKeySpace.tag_path_from_key("prefix/NODE/name/TAGS/WRITE")

    expected = ""
    assert expected == NodeKeySpace.tag_path_from_key("prefix/NODE/name/TAGS/DATA")

def test_tag_path_from_key_no_data_or_write():
    with pytest.raises(ValueError, match="No tag path found in "):
        NodeKeySpace.tag_path_from_key("")

def test_method_path_from_call_key():
    expected = "key0/key1"
    assert expected == NodeKeySpace.method_path_from_call_key("prefix/NODE/name/METHODS/key0/key1/key2/key3/key4")
    
    expected = "key0"
    assert expected == NodeKeySpace.method_path_from_call_key("prefix/NODE/name/METHODS/key0/key1/key2/key3")

    expected = ""
    assert expected == NodeKeySpace.method_path_from_call_key("prefix/NODE/name/METHODS/key0/key1/key2")

    expected = ""
    assert expected == NodeKeySpace.method_path_from_call_key("prefix/NODE/name/METHODS/key0/key1")

    expected = ""
    assert expected == NodeKeySpace.method_path_from_call_key("prefix/NODE/name/METHODS/key0")

    expected = ""
    assert expected == NodeKeySpace.method_path_from_call_key("prefix/NODE/name/METHODS")

def test_method_path_from_call_key_no_method():
    with pytest.raises(ValueError, match="No method path found in prefix/NODE/name"):
        NodeKeySpace.method_path_from_call_key("prefix/NODE/name")

def test_method_path_from_response_key():
    expected = "key0"
    assert expected == NodeKeySpace.method_path_from_response_key("prefix/NODE/name/METHODS/key0/key1/key2/key3/key4")

    expected = ""
    assert expected == NodeKeySpace.method_path_from_response_key("prefix/NODE/name/METHODS")

def test_method_path_from_response_key_no_method():
    with pytest.raises(ValueError, match="No method path found in prefix/NODE/name"):
        NodeKeySpace.method_path_from_response_key("prefix/NODE/name")

def test_user_key_from_key():
    expected = "prefix/name"
    assert expected == NodeKeySpace.user_key_from_key("prefix/NODE/name")

    expected = "prefix/name"
    assert expected == NodeKeySpace.user_key_from_key("prefix/NODE/name/METHODS/key0/key1")

def test_user_key_from_key_no_param():
    with pytest.raises(ValueError, match="Invalid key expr "):
        NodeKeySpace.user_key_from_key("")

def test_tag_data_path():
    instance = NodeKeySpace.from_user_key("prefix/name")

    expected = "prefix/NODE/name/TAGS/DATA/path"
    assert expected == instance.tag_data_path("path")

def test_tag_write_path():
    instance = NodeKeySpace.from_user_key("prefix/name")

    expected = "prefix/NODE/name/TAGS/WRITE/path"
    assert expected == instance.tag_write_path("path")

def test_method_path():
    instance = NodeKeySpace.from_user_key("prefix/name")

    expected = "prefix/NODE/name/METHODS/path"
    assert expected == instance.method_path("path")

def test_method_query():
    instance = NodeKeySpace.from_user_key("prefix/name")

    expected = "prefix/NODE/name/METHODS/path/caller_id/method_id"
    assert expected == instance.method_query("path", "caller_id", "method_id")

def test_method_response():
    instance = NodeKeySpace.from_user_key("prefix/name")

    expected = "prefix/NODE/name/METHODS/path/caller_id/method_id/RESPONSE"
    assert expected == instance.method_response("path", "caller_id", "method_id")

def test_method_query_listen():
    instance = NodeKeySpace.from_user_key("prefix/name")

    expected = "prefix/NODE/name/METHODS/path/*/*"
    assert expected == instance.method_query_listen("path")

def test_contains_true():
    instance = NodeKeySpace.from_user_key("prefix/name")
    assert instance.contains("prefix/NODE/name") == True

def test_contains_false():
    instance = NodeKeySpace.from_user_key("prefix/other name")
    assert instance.contains("prefix/NODE/name") == False

def test_contains_no_node():
    instance = NodeKeySpace.from_user_key("prefix/name")

    with pytest.raises(ValueError, match="'NODE' is not in list"):
        instance.contains("prefix/name")
    