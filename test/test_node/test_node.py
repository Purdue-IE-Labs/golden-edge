import gedge
import pytest
from unittest.mock import patch, MagicMock
import json5
import logging

from gedge.node.node import NodeConfig
from gedge.node.node import NodeConfig, Tag, Method
from gedge.node.subnode import SubnodeConfig
from gedge.node.data_type import DataType
from gedge.node.prop import Props
from gedge.node.tag import WriteResponse

# Begin NodeConfig testing

def test_fom_json5():
    #TODO
    pytest.fail("Test has not been created")
    

def test_from_json5_str():
    #TODO
    pytest.fail("Test has not been created")

def test_warn_duplicate_tag(caplog):
    '''
    Node: this is dependent on add_tag
    '''
    instance_str = "instance/str"
    nodeConfig_instance = NodeConfig(instance_str)

    assert nodeConfig_instance.tags == {}

    properties = {
        'tag1': 'int',
        'tag2': 'float',
        'tag3': 'str',
    }

    NodeConfig.add_tag(nodeConfig_instance, "test_path", int, properties)
    
    # Add the same tag again to trigger the warning
    with caplog.at_level(logging.WARNING):  # Captures the logger output
        NodeConfig.add_tag(nodeConfig_instance, "test_path", int, properties)

    assert len(caplog.records) > 0  # At least one log record should exist
    
    # Optionally, check the level of the logged message
    assert caplog.records[0].levelname == "WARNING"  # Ensure the log level is WARNING

def test_add_tag():
    instance_str = "instance/str"
    nodeConfig_instance = NodeConfig(instance_str)

    assert nodeConfig_instance.tags == {}

    properties = {
        'tag1': 'int',
        'tag2': 'float',
        'tag3': 'str',
    }

    NodeConfig.add_tag(nodeConfig_instance, "test_path", int, properties)
    
    expected_tag = Tag("test_path", DataType.INT, Props.from_value(properties), False, [], None)

    assert nodeConfig_instance.tags['test_path'].path == expected_tag.path
    assert nodeConfig_instance.tags['test_path'].type == expected_tag.type
    assert str(nodeConfig_instance.tags['test_path'].props.to_value) == str(expected_tag.props.to_value)
    assert nodeConfig_instance.tags['test_path']._writable == expected_tag._writable
    assert nodeConfig_instance.tags['test_path'].write_handler == expected_tag.write_handler

@pytest.fixture
def root_node():
    instance_str = "instance/str"
    root = NodeConfig(instance_str)

    properties = {
        'tag1': 'int',
        'tag2': 'float',
        'tag3': 'str',
    }

    tags = {
        'tag1': Tag('path1/end', int, properties, False, [], None),
        'tag2': Tag('path2/end', int, properties, False, [], None),
        'tag3': Tag('path3/end', int, properties, False, [], None)
    }

    root.subnodes['subnode1'] = SubnodeConfig('subnode1', root.ks, None, None, None)
    root.subnodes['subnode2'] = SubnodeConfig('subnode2', root.ks, None, None, None)

    # Creating subnodes within subnode1
    subnode1 = root.subnodes['subnode1']
    subnode1.subnodes = {'subsubnode1': SubnodeConfig('subsubnode1', subnode1.ks, None, None, None)}

    return root

# Note: This class contains all of the subnode test functions
class TestSubnode:

    def test_subnode(self, root_node):
        '''
        Test retrieving a valid subnode
        '''
        result = root_node.subnode('subnode1')
        assert result.name == 'subnode1'

    def test_subnode_does_not_exist(self, root_node):
        '''
        Test that a ValueError is raised for a non-existing subnode
        '''
        with pytest.raises(ValueError, match="No subnode subnode3"):
            root_node.subnode('subnode3')


    def test_subnode_nested(self, root_node):
        '''
        Test retrieving a valid subnode via a path (e.g., "subnode1/subsubnode1")
        '''
        result = root_node.subnode('subnode1/subsubnode1')
        assert result.name == 'subsubnode1'

    def test_subnode_nested_does_not_exist(self, root_node):
        '''
        Test that a ValueError is raised when a part of the path doesn't exist
        '''
        with pytest.raises(ValueError, match="No subnode subsubnode2"):
            root_node.subnode('subnode1/subsubnode2')

    def test_subnode_path_invalid(self, root_node):
        '''
        Test that a ValueError is raised when you provide a path-like format with a single name
        '''
        with pytest.raises(ValueError, match="No subnode "):
            root_node.subnode('subnode1/')

def tag_handler():
    print("Yeah, Testing! :)")

def test_add_writetable_tag():
    '''
    Test that add_writable_tag creates a tag that is writable and is equal to an equivalent manually created tag
    
    Dependencies: 
        (node.py) _add_readable_tag
        (tag.py) writable
    '''
    instance_str = "instance/str"
    nodeConfig_instance = NodeConfig(instance_str)

    assert nodeConfig_instance.tags == {}

    properties = {
        'tag1': 'int',
        'tag2': 'float',
        'tag3': 'str',
    }

    responses = [
        (200, {"status": "success", "message": "Request was successful"}),
        (404, {"status": "error", "message": "Not Found"}),
        (500, {"status": "error", "message": "Internal Server Error"}),
    ]

    nodeConfig_instance.add_writable_tag("test_path", int, tag_handler, responses, properties)

    expected_tag = Tag("test_path", DataType.INT, Props.from_value(properties), False, [], None)

    expected_tag.writable(tag_handler, responses)

    assert nodeConfig_instance.tags['test_path'].path == expected_tag.path
    assert nodeConfig_instance.tags['test_path'].type == expected_tag.type
    assert str(nodeConfig_instance.tags['test_path'].props.to_value) == str(expected_tag.props.to_value)
    assert nodeConfig_instance.tags['test_path']._writable == expected_tag._writable
    assert nodeConfig_instance.tags['test_path'].write_handler == expected_tag.write_handler

class TestWriteResponses:

    def test_add_write_response(self):
        '''
        Dependencies: 
            (tag.py) add_write_response
            (node.py) add_writable_tag
        '''

        instance_str = "instance/str"
        nodeConfig_instance = NodeConfig(instance_str)

        properties = {
            'tag1': 'int',
            'tag2': 'float',
            'tag3': 'str'
        }

        responses = [
            (200, {"status": "success", "message": "Request was successful"}),
            (404, {"status": "error", "message": "Not Found"}),
            (500, {"status": "error", "message": "Internal Server Error"}),
        ]

        nodeConfig_instance.add_writable_tag("test_path", int, tag_handler, responses, properties)

        expected_tag = Tag("test_path", DataType.INT, Props.from_value(properties), False, [], None)

        expected_tag.writable(tag_handler, responses)

        additional_response = {
            "message": "Request was successful"
        }

        assert str(nodeConfig_instance.tags['test_path'].props.to_value) == str(expected_tag.props.to_value)

        nodeConfig_instance.add_write_response("test_path", 300, additional_response)

        expected_tag.add_write_response(300, Props.from_value(additional_response))

        assert str(nodeConfig_instance.tags['test_path'].props.to_value) == str(expected_tag.props.to_value)

    def test_add_write_response_no_tag(self):
        '''
        Dependencies: (tag.py) add_write_response
        '''
        #TODO:
        pytest.fail("Test has not been created")
    
    def test_add_write_responses(self):
        #TODO
        pytest.fail("Test has not been created")
    
    def test_add_write_responses_no_tag(self):
        #TODO
        pytest.fail("Test has not been created")

def test_add_tag_write_handler():
    #TODO
    pytest.fail("Test has not been created")

def test_add_tag_write_handler_no_tag():
    #TODO
    pytest.fail("Test has not been created")

def test_add_method_handler():
    #TODO
    pytest.fail("Test has not been created")

def test_add_method_handler_no_tag():
    #TODO
    pytest.fail("Test has not been created")

def test_add_props():
    #TODO
    pytest.fail("Test has not been created")

def test_add_props_no_tag():
    #TODO
    pytest.fail("Test has not been created")

def test_delete_tag():
    #TODO
    pytest.fail("Test has not been created")

def test_delete_tag_no_tag():
    #TODO
    pytest.fail("Test has not been created")

def test_add_method():
    #TODO
    pytest.fail("Test has not been created")

def test_delete_method():
    #TODO
    pytest.fail("Test has not been created")

def test_delete_method_no_method():
    #TODO
    pytest.fail("Test has not been created")

def test_verify_tags():
    #TODO
    pytest.fail("Test has not been created")

def test_verify_tags_no_handler():
    #TODO
    pytest.fail("Test has not been created")

def test_verify_tags_no_responses():
    #TODO
    pytest.fail("Test has not been created")

def test_verify_methods():
    #TODO
    pytest.fail("Test has not been created")

def test_verify_methods_no_handler():
    #TODO
    pytest.fail("Test has not been created")

def test_build_meta():
    #TODO
    pytest.fail("Test has not been created")

def test_connect():
    #TODO
    pytest.fail("Test has not been created")


# Begin NodeSession testing