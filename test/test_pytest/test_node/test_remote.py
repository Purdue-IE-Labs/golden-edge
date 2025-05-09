import pytest
import gedge
import pathlib

from gedge.node.node import NodeConfig
from gedge.node.subnode import SubnodeConfig
from gedge.node.subnode import RemoteSubConnection


from collections import defaultdict

class TestSanity:
    def test_init(self):
        config = NodeConfig("my/node")
        connectNode = NodeConfig("my/otherNode")

        with gedge.mock_connect(config) as session:
            with session.connect_to_remote(connectNode.key) as remote:
                assert remote.key == connectNode.key

    def test_add_tag_data_callback(self):
        config = NodeConfig("my/node")
        json = '''
            {
                "key": "test/tag/writes/writee",
            }
        '''
        connectNode = NodeConfig.from_json5_str(json)
        tag = connectNode.add_tag("tag/path", int)

        def callback(self):
            print("Callaback girl!!!!!")

        with gedge.mock_connect(config) as session:
            with session.connect_to_remote(connectNode.key) as remote:
                remote.tags[tag.path] = tag
                remote.add_tag_data_callback(tag.path, callback)

    def test_add_state_callback(self):
        config = NodeConfig("my/node")
        json = '''
            {
                "key": "test/tag/writes/writee",
            }
        '''
        connectNode = NodeConfig.from_json5_str(json)

        def callback(self):
            print("Indiana")

        with gedge.mock_connect(config) as session:
            with session.connect_to_remote(connectNode.key) as remote:
                remote.add_state_callback(callback)

    def test_add_meta_callback(self):
        config = NodeConfig("my/node")
        json = '''
            {
                "key": "test/tag/writes/writee",
            }
        '''
        connectNode = NodeConfig.from_json5_str(json)

        def callback(self):
            print("Indiana")

        with gedge.mock_connect(config) as session:
            with session.connect_to_remote(connectNode.key) as remote:
                remote.add_meta_callback(callback)

    def test_add_liveliness_callback(self):
        config = NodeConfig("my/node")
        json = '''
            {
                "key": "test/tag/writes/writee",
            }
        '''
        connectNode = NodeConfig.from_json5_str(json)

        def callback(self):
            print("Indiana")

        with gedge.mock_connect(config) as session:
            with session.connect_to_remote(connectNode.key) as remote:
                remote.add_liveliness_callback(callback)

    def test_tag_bind(self):
        config = NodeConfig("my/node")
        json = '''
            {
                "key": "test/tag/writes/writee",
            }
        '''
        connectNode = NodeConfig.from_json5_str(json)
        tag = connectNode.add_tag("tag/write", int)
        def handler(query: gedge.TagWriteQuery) -> None:
            if query.value > 10:
                query.reply(400)
                return
            query.reply(200)
        
        
        connectNode.add_tag_write_handler("tag/write", handler=handler)

        with gedge.mock_connect(config) as session:
            with session.connect_to_remote(connectNode.key) as remote:
                remote.tags[tag.path] = tag
                tagBind = remote.tag_bind(tag.path)
                tagBind.value = 20


    def test_tag_binds(self):
        config = NodeConfig("my/node")
        json = '''
            {
                "key": "test/tag/writes/writee",
            }
        '''
        connectNode = NodeConfig.from_json5_str(json)
        tagList = []
        paths = []
        for i in range(0, 10):
            tagList.append(connectNode.add_tag(f"tag/path{i}", int))
            paths.append(f"tag/path{i}")

        with gedge.mock_connect(config) as session:
            with session.connect_to_remote(connectNode.key) as remote:
                for i in range(0, 10):
                    remote.tags[f"tag/path{i}"] = tagList[i]
                tagBinds = remote.tag_binds(paths)

                assert len(tagBinds) == 10

    def test_subnode(self):
        config = NodeConfig("my/node")
        json = '''
            {
                "key": "test/tag/writes/writee",
            }
        '''
        connectNode = NodeConfig.from_json5_str(json)

        s0 = SubnodeConfig("subnode0", connectNode.ks, {}, {}, {})
    

        with gedge.mock_connect(config) as session:
            with session.connect_to_remote(connectNode.key) as remote:
                remote.subnodes[s0.name] = s0
                subRemote = remote.subnode(s0.name)

                assert isinstance(subRemote, RemoteSubConnection)
                assert subRemote.ks == s0.ks


    def test_write_tag(self):
        pytest.fail("Yeah Dawg")

    def test_write_tag_async(self):
        pytest.fail("Yeah Dawg but Async")

    