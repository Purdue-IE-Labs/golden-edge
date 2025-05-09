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

class TestSanity:
    def test_split_user_key(self):
        assert ("prefix", "name") == NodeKeySpace.split_user_key("prefix/name")

    def test_name_from_key(self):
        assert "name" == NodeKeySpace.name_from_key("prefix/NODE/name")

    def test_prefix_from_key(self):
        assert "prefix" == NodeKeySpace.prefix_from_key("prefix/NODE/name")

    def test_internal_to_user_key(self):
        assert "prefix/name" == NodeKeySpace.internal_to_user_key("prefix/NODE/name")

    def test_tag_path_from_key(self):
        assert "path/after/tag" == NodeKeySpace.tag_path_from_key("prefix/NODE/name/TAGS/DATA/path/after/tag")
        assert "path/after/tag" == NodeKeySpace.tag_path_from_key("prefix/NODE/name/TAGS/WRITE/path/after/tag")

    def test_method_path_from_call_key(self):
        assert "my/method/1" == NodeKeySpace.method_path_from_call_key("prefix/NODE/name/METHODS/my/method/1/caller_id/method_id")

    def test_method_path_from_response_key(self):
        assert "my/method/1" == NodeKeySpace.method_path_from_response_key("prefix/NODE/name/METHODS/my/method/1/caller_id/method_id/RESPONSE")

    def test_user_key_from_key(self):
        assert "prefix/name" == NodeKeySpace.user_key_from_key("prefix/NODE/name/TAGS/DATA/path/after/tag")

    @pytest.fixture
    def create_instance(self):
        instance = NodeKeySpace("prefix", "name")
        return instance
    
    def test_prefix_setter(self, create_instance):
        previous_key = create_instance.node_key_prefix
        create_instance.prefix = "new_prefix"
        assert create_instance.node_key_prefix != previous_key

    def test_name_setter(self, create_instance):
        previous_key = create_instance.node_key_prefix
        create_instance.name = "new_name"
        assert create_instance.node_key_prefix != previous_key

    def test_user_key_setter(self, create_instance):
        previous_key = create_instance.node_key_prefix
        create_instance.user_key = "new_prefix/new_name"
        assert create_instance.node_key_prefix != previous_key

    def test_tag_data_path(self, create_instance):
        assert "prefix/NODE/name/TAGS/DATA/path" == create_instance.tag_data_path("path")

    def test_tag_write_path(self, create_instance):
        assert "prefix/NODE/name/TAGS/WRITE/path" == create_instance.tag_write_path("path")

    def test_method_path(self, create_instance):
        assert "prefix/NODE/name/METHODS/path" == create_instance.method_path("path")

    def test_method_query(self, create_instance):
        assert "prefix/NODE/name/METHODS/path/caller_id/method_query_id" == create_instance.method_query("path", "caller_id", "method_query_id")

    def test_method_response(self, create_instance):
        assert "prefix/NODE/name/METHODS/path/caller_id/method_query_id/RESPONSE" == create_instance.method_response("path", "caller_id", "method_query_id")

    def test_method_query_listen(self, create_instance):
        assert "prefix/NODE/name/METHODS/path/*/*" == create_instance.method_query_listen("path")

    def test_contains(self, create_instance):
        assert create_instance.contains("prefix/NODE/name") == True
        assert create_instance.contains("prefix/NODE/not name") == False
        
        with pytest.raises(ValueError, match="'NODE' is not in list"):
            create_instance.contains("")
        
        with pytest.raises(ValueError, match="'NODE' is not in list"):
            create_instance.contains("prefix/name")


class TestEmpty:
    def test_split_user_key(self):
        with pytest.raises(ValueError, match="key '' must include at least one '/'"):
            NodeKeySpace.split_user_key("")

    def test_name_from_key(self):
        with pytest.raises(ValueError, match="'NODE' is not in list"):
            NodeKeySpace.name_from_key("")

    def test_prefix_from_key(self):
        with pytest.raises(ValueError, match="'NODE' is not in list"):
            NodeKeySpace.prefix_from_key("")

    def test_internal_to_user_key(self):
        with pytest.raises(ValueError, match="'NODE' is not in list"):
            NodeKeySpace.internal_to_user_key("")

    def test_tag_path_from_key(self):
        with pytest.raises(ValueError, match="No tag path found in "):
            NodeKeySpace.tag_path_from_key("")
    
    def test_method_path_from_call_key(self):
        with pytest.raises(ValueError, match="No method path found in "):
            NodeKeySpace.method_path_from_call_key("")

    def test_method_path_from_response_key(self):
        with pytest.raises(ValueError, match="No method path found in "):
            NodeKeySpace.method_path_from_response_key("")

    def test_user_key_from_key(self):
        with pytest.raises(ValueError, match="Invalid key expr"):
            NodeKeySpace.user_key_from_key("")

    @pytest.fixture
    def create_instance(self):
        instance = NodeKeySpace("prefix", "name")
        return instance

    def test_data_path(self, create_instance: NodeKeySpace):
        assert create_instance.tag_data_key_prefix + "/" == create_instance.tag_data_path("")

    def test_tag_write_path(self, create_instance: NodeKeySpace):
        assert create_instance.tag_write_key_prefix + "/" == create_instance.tag_write_path("")

    def test_method_path(self, create_instance: NodeKeySpace):
        assert create_instance.method_key_prefix + "/" == create_instance.method_path("")

    def test_method_query(self, create_instance: NodeKeySpace):
        assert create_instance.method_key_prefix + "///" == create_instance.method_query("", "", "")

    def test_method_response(self, create_instance: NodeKeySpace):
        assert create_instance.method_key_prefix + "////RESPONSE" == create_instance.method_response("", "", "")

    def test_method_query_listen(self, create_instance: NodeKeySpace):
        assert create_instance.method_key_prefix + "//*/*" == create_instance.method_query_listen("")

    def test_contains(self, create_instance: NodeKeySpace):
        with pytest.raises (ValueError, match="'NODE' is not in list"):
            create_instance.contains("")

class TestRoundTrip:
    
    @pytest.mark.parametrize("prefix, name", [
        ("thing1", "thing2"),
    ], ids=(
        "Simple Key",
    ))
    def test_user_to_internal(self, prefix, name):
        user_key = f"{prefix}/{name}"
        instance = NodeKeySpace.from_user_key(user_key)
        internal_key = instance.node_key_prefix
        created_user_key = instance.internal_to_user_key(internal_key)
        assert user_key == created_user_key

    @pytest.mark.parametrize("internal_key", [
        ("Cat/NODE/in the hat"),
        ("Method/SUBNODES/subprefix/NODE/name")
    ],ids=(
        "Simple Key",
        "Node at the end"
    ))
    def test_internal_to_user(self, internal_key):
        instance = NodeKeySpace.from_internal_key(internal_key)
        assert internal_key == instance.node_key_prefix

    def test_method_query(self):
        instance = NodeKeySpace("prefix", "name")
        method_path = "path/to/method"
        caller_id = "ring ring"
        method_id = "mid (lol) 879"

        query_key = instance.method_query(method_path, caller_id, method_id)
        path_from_query = instance.method_path_from_call_key(query_key)
        assert path_from_query == method_path

    def test_method_response(self):
        instance = NodeKeySpace("prefix", "name")
        method_path = "path/to/method"
        caller_id = "ring ring, your phone is ringing"
        method_id = "mid (lol) 2478"
        response_key = instance.method_response(method_path, caller_id, method_id)
        path_from_response = instance.method_path_from_response_key(response_key)
        assert path_from_response == method_path

    def test_tag_data(self):
        instance = NodeKeySpace("prefix", "name")
        tag_path = "tag/youre/it"
        tag_key = instance.tag_data_path(tag_path)
        path_from_data = instance.tag_path_from_key(tag_key)
        assert path_from_data == tag_path

    def test_tag_write(self):
        instance = NodeKeySpace("prefix", "name")
        tag_path = "tag/youre/it"
        tag_key = instance.tag_write_path(tag_path)
        path_from_data = instance.tag_path_from_key(tag_key)
        assert path_from_data == tag_path
    
    @pytest.mark.parametrize("key", [
        ("pre-0/NODE/name-0/SUBNODES/pre-1/NODE/name-1/SUBNODES/pre/NODE/name"),
        ("red fish/NODE/blue fish"),
        ("Gibberish:asjhgdsjhafhjsdfyaretsujrebfjdsgubrfuydsfuygfusdbudsfb/prefix/NODE/name"),
    ], ids=(
        "Long Key",
        "Simple Key",
        "Gibberish"
    ))
    def test_any_key_to_user_key(self, key):
        user_key = NodeKeySpace.user_key_from_key(key)
        instance = NodeKeySpace.from_user_key(user_key)
        assert instance.user_key == user_key

class TestNumerousNodes:
    def test_user_key(self):
        instance = NodeKeySpace.from_user_key("NODE/NODE")
        assert "NODE/NODE/NODE" == instance.node_key_prefix

    @pytest.mark.skip
    def test_internal_key(self):
        instance = NodeKeySpace.from_internal_key("NODE/NODE/NODE/NODE/NODE/NODE")
        assert "NODE/NODE/NODE/NODE/NODE/NODE" == instance.node_key_prefix
    
    @pytest.mark.skip
    def test_user_key_from_key(self):
        user_key = NodeKeySpace.user_key_from_key("NODE/NODE/NODE/NODE/NODE/NODE/NODE/NODE/NODE/NODE/NODE")
        assert user_key == "NODE/NODE"