import pytest
import gedge
import pathlib
from collections import defaultdict

class TestSanity:

    def test_add_tag_data_callback(self):
    
        def tag_handler(query: gedge.TagWriteQuery) -> None:
            if query.value > 10:
                query.reply(400)
                return
            query.reply(200)
        

        here = pathlib.Path(__file__).parent
    
        config = gedge.NodeConfig.from_json5(str(here / "test_writee.json5"))
    
        config.add_tag_write_handler("tag/write", handler=tag_handler)

        node = gedge.mock_connect(config)

        remote = node.connect_to_remote("test/tag/writes/writee")

        comm = remote._comm

        assert comm.subscribers == defaultdict(list)

        def tag_data_callback_handler():
            print("Yeah dawg")

        remote.add_tag_data_callback("tag/write", tag_data_callback_handler)        

        assert comm.subscribers != []

    def test_add_state_callback(self):
        
        here = pathlib.Path(__file__).parent
    
        config = gedge.NodeConfig.from_json5(str(here / "test_writee.json5"))

        config.tags['tag/write']._writable = False

        node = gedge.mock_connect(config)

        remote = node.connect_to_remote("test/tag/writes/writee")

        comm = remote._comm

        assert comm.subscribers == defaultdict(list)

        def state_callback_handler():
            print("Yeah dawg")

        remote.add_state_callback(state_callback_handler)

        assert comm.subscribers != []

    def test_add_meta_callback(self):
        
        here = pathlib.Path(__file__).parent
    
        config = gedge.NodeConfig.from_json5(str(here / "test_writee.json5"))

        config.tags['tag/write']._writable = False

        node = gedge.mock_connect(config)

        remote = node.connect_to_remote("test/tag/writes/writee")

        comm = remote._comm

        assert comm.subscribers == defaultdict(list)

        def meta_callback_handler():
            print("Yeah dawg")

        remote.add_meta_callback(meta_callback_handler)

        assert comm.subscribers != []

    # MockComm doesn't have a session attribute, so liveliness callback can't be initialized
    @pytest.mark.skip
    def test_add_liveliness_callback(self):
        
        here = pathlib.Path(__file__).parent
    
        config = gedge.NodeConfig.from_json5(str(here / "test_writee.json5"))

        config.tags['tag/write']._writable = False

        node = gedge.mock_connect(config)

        remote = node.connect_to_remote("test/tag/writes/writee")

        comm = remote._comm

        assert comm.subscribers == defaultdict(list)

        def liveliness_callback_handler():
            print("Yeah dawg")

        remote.add_liveliness_callback(liveliness_callback_handler)

        assert comm.subscribers != []


    # MockComm doesn't have a session attribute, so TagBind can't be initialized

    @pytest.mark.skip
    def test_tag_binds(self):

        # Create some tags

        def tag_handler(query: gedge.TagWriteQuery) -> None:
            if query.value > 10:
                query.reply(400)
                return
            query.reply(200)
        

        here = pathlib.Path(__file__).parent
    
        config = gedge.NodeConfig.from_json5(str(here / "test_writee.json5"))
    
        config.add_tag_write_handler("tag/write", handler=tag_handler)

        config.add_tag("tag1/write", int, {"desc": "testing a tag write",})

        config.add_tag("tag2/write", int, {"desc": "testing a tag write",})

        config.add_tag("tag3/write", int, {"desc": "testing a tag write",})

        config.add_tag("tag4/write", int, {"desc": "testing a tag write",})

        node = gedge.mock_connect(config)

        remote = node.connect_to_remote("test/tag/writes/writee")

        remote.tag_binds(["tag/write","tag1/write","tag2/write","tag3/write","tag4/write"])


        pytest.fail("Yeah dawg")

    # MockComm doesn't have a session attribute, so TagBind can't be initialized

    @pytest.mark.skip
    def test_tag_bind(self):

        # Create some tags

        def tag_handler(query: gedge.TagWriteQuery) -> None:
            if query.value > 10:
                query.reply(400)
                return
            query.reply(200)
        

        here = pathlib.Path(__file__).parent
    
        config = gedge.NodeConfig.from_json5(str(here / "test_writee.json5"))
    
        config.add_tag_write_handler("tag/write", handler=tag_handler)

        node = gedge.mock_connect(config)

        remote = node.connect_to_remote("test/tag/writes/writee")

        remote.tag_bind("tag/write")


        pytest.fail("Yeah dawg")