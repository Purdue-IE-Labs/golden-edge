import pytest
import gedge
import pathlib

from gedge.node.node import NodeConfig
from gedge.node.subnode import SubnodeConfig
from gedge.node.subnode import RemoteSubConnection
from gedge.node.data_type import DataType
from gedge.node.error import TagLookupError, MethodLookupError

import time


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

    def test_all_callbacks(self):
        config = NodeConfig("my/node")
        json = '''
            {
                "key": "test/tag/writes/writee",
            }
        '''
        connectNode = NodeConfig.from_json5_str(json)
        tag = config.add_tag("test/path", int)

        def state_callback(self):
            print("State Callaback girl!!!!!")

        def meta_callback(self):
            print("Meta Callaback girl!!!!!")

        def liveliness_callback(self):
            print("Liveliness Callaback girl!!!!!")

        def tag_data_callback(self):
            print("Tag Data Callaback girl!!!!!")

        with gedge.mock_connect(config) as session:
            with session.connect_to_remote(connectNode.key, state_callback, meta_callback, liveliness_callback, {tag.path: tag_data_callback}) as remote:
                remote.tags[tag.path] = tag
                # Some sort of assertion???

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
        writer = NodeConfig.from_json5_str('''{"key": "test/tag/bind/writer"}''')
        writee = NodeConfig.from_json5_str('''{"key": "test/tag/bind/writee"}''')
        
        def handler(query: gedge.TagWriteQuery) -> None:
            if query.value > 10:
                query.reply(400)
                return
            query.reply(200)

        tag = writee.add_writable_tag("tag/write", DataType.INT, handler, [
            (200, {"desc": "tag updated with value"}), 
            (400, {"desc": "invalid value (>10)"})])
    
        with gedge.mock_connect(writee) as writeeSession:            
            with gedge.mock_connect(writer, writeeSession._comm) as writerSession:
                with writerSession.connect_to_remote(writee.key) as remote:
                    remote.tags[tag.path] = tag
                    # remote.tags[tag.path].write_handler = handler
                    tagBind = remote.tag_bind(tag.path)
                    tagBind.value = 20

                    #I don't exactly know how to tst this more


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

    def test_subnode_no_slash(self):
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

    def test_subnode_slash(self):
        from gedge.node.subnode import SubnodeSession
        otherNode = NodeConfig("test/node")
        config = NodeConfig("my/node")

        subnode0 = SubnodeConfig("subnode0", config.ks, {}, {}, {})

        subnode1 = SubnodeConfig("subnode1", config.ks, {}, {}, {})
        subnode0.subnodes["subnode1"] = subnode1

        config.subnodes[subnode0.name] = subnode0


        with gedge.mock_connect(config) as session:
            with session.connect_to_remote(otherNode.key) as remote:
                from gedge.node.subnode import RemoteSubConnection    

                subRemote = remote.subnode("subnode0/subnode1")

                assert isinstance(subRemote, RemoteSubConnection)
                assert str(subRemote.ks) == "test/NODE/node/SUBNODES/subnode0/SUBNODES/subnode1"
                assert subRemote._comm is session._comm

    
    def test_write_tag(self):
        writer = NodeConfig.from_json5_str('''{"key": "test/tag/bind/writer"}''')
        writee = NodeConfig.from_json5_str('''{"key": "test/tag/bind/writee"}''')

        def handler(query: gedge.TagWriteQuery) -> None:
            if query.value > 10:
                query.reply(400)
                return
            query.reply(200)

        tag = writee.add_writable_tag("tag/write", DataType.INT, handler, [
            (200, {"desc": "tag updated with value"}), 
            (400, {"desc": "invalid value (>10)"})])


        with gedge.mock_connect(writee) as writeeSession:            
            with gedge.mock_connect(writer, writeeSession._comm) as writerSession:
                with writerSession.connect_to_remote(writee.key) as remote:
                    remote.tags["tag/write"] = tag
                    reply = remote.write_tag("tag/write", value=9)
                    assert reply.code == 200
                    assert reply.error == ""
    
    @pytest.mark.asyncio
    async def test_write_tag_async(self):
        writer = NodeConfig.from_json5_str('''{"key": "test/tag/bind/writer"}''')
        writee = NodeConfig.from_json5_str('''{"key": "test/tag/bind/writee"}''')

        def handler(query: gedge.TagWriteQuery) -> None:
            if query.value > 10:
                query.reply(400)
                return
            query.reply(200)

        tag = writee.add_writable_tag("tag/write", DataType.INT, handler, [
            (200, {"desc": "tag updated with value"}), 
            (400, {"desc": "invalid value (>10)"})])


        with gedge.mock_connect(writee) as writeeSession:            
            with gedge.mock_connect(writer, writeeSession._comm) as writerSession:
                with writerSession.connect_to_remote(writee.key) as remote:
                    remote.tags["tag/write"] = tag
                    reply = await remote.write_tag_async("tag/write", value=9)
                    assert reply.code == 200
                    assert reply.error == ""

    def test_call_method(self, capsys):
        def handler(query: gedge.MethodQuery):
            name = query.params["name"]
            speed = query.params["speed"]
            if len(name) > 30:
                query.reply(401)
                return
            if speed < 0 or speed > 100:
                query.reply(400, body={"res1": speed})
                return
            if name == 'EXCEPTION':
                raise ValueError("exception thrown in method handler")
            query.reply(200, body={"res1": speed})
            time.sleep(2)
            query.reply(200, body={"res1": speed})
        
        here = pathlib.Path(__file__).parent
        callee = gedge.NodeConfig.from_json5(str(here / "test_callee.json5"))
        callee.add_method_handler("call/method", handler=handler)
        

        caller = NodeConfig.from_json5_str('''{"key": "test/method/calls/caller"}''')

        def my_callback(reply):
            print("Callback received:")

            if reply.error:
                print(f"Error: {reply.code}, {reply.error}")
            else:
                print(f"Success: {reply.code}, {reply.props}, {reply.body}")

        with gedge.mock_connect(callee) as calleeSession:
            with gedge.mock_connect(caller, calleeSession._comm) as callerSession:
                with callerSession.connect_to_remote(callee.key) as remote:
                    remote.methods = callee.methods
                    remote.call_method("call/method", my_callback, name="Jonas", speed=0)
                    time.sleep(2.1)
                    captured = capsys.readouterr()
                    assert "Callback received:" in captured.out

    @pytest.mark.parametrize("name, speed, timeout, code", [
        ("Jonas", 0, 5000, 200),
        ("Really really really really really long name", 0, 5000, 401),
        ("Suitable Name", 5000, 500, 400),
        ("Suitable Name", 0, -1, 200)
    ], ids=["Normal", "Invalid Name", "Invalid speed", "Negative Timetout"])
    def test_call_method_iter(self, name, speed, timeout, code):
        def handler(query: gedge.MethodQuery):
            name = query.params["name"]
            speed = query.params["speed"]
            if len(name) > 30:
                query.reply(401)
                return
            if speed < 0 or speed > 100:
                query.reply(400, body={"res1": speed})
                return
            if name == 'EXCEPTION':
                raise ValueError("exception thrown in method handler")
            query.reply(200, body={"res1": speed})
        
        # pytest.fail("Yeah Dawg")
        here = pathlib.Path(__file__).parent
        callee = gedge.NodeConfig.from_json5(str(here / "test_callee.json5"))
        callee.add_method_handler("call/method", handler=handler)
        

        caller = NodeConfig.from_json5_str('''{"key": "test/method/calls/caller"}''')

        with gedge.mock_connect(callee) as calleeSession:
            with gedge.mock_connect(caller, calleeSession._comm) as callerSession:
                with callerSession.connect_to_remote(callee.key) as remote:
                    remote.methods = callee.methods
                    responses = []
                    if (timeout < 0):
                        with pytest.raises(TimeoutError, match="Timeout of method call at path call/method exceeded"):
                            responses = list(remote.call_method_iter("call/method", timeout, name=name, speed=speed))
                        return
                    else:
                        responses = list(remote.call_method_iter("call/method", timeout, name=name, speed=speed))
                    assert len(responses) == 2
                    assert responses[0].code == code
                    assert responses[1].code == 10

class TestEmpty:
    def test_add_tag_data_callback(self):
        config = NodeConfig("my/node")
        json = '''
            {
                "key": "test/tag/writes/writee",
            }
        '''
        connectNode = NodeConfig.from_json5_str(json)
        tag = config.add_tag("tag/path", int)

        def callback(self):
            print("Callaback girl!!!!!")

        with gedge.mock_connect(config) as session:
            with session.connect_to_remote(connectNode.key) as remote:
                with pytest.raises(TagLookupError, match="Tag None not found on node writee"):
                    remote.add_tag_data_callback(None, callback)

    def test_tag_bind(self):
        writer = NodeConfig.from_json5_str('''{"key": "test/tag/bind/writer"}''')
        writee = NodeConfig.from_json5_str('''{"key": "test/tag/bind/writee"}''')
        
        def handler(query: gedge.TagWriteQuery) -> None:
            if query.value > 10:
                query.reply(400)
                return
            query.reply(200)

        tag = writee.add_writable_tag("tag/write", DataType.INT, handler, [
            (200, {"desc": "tag updated with value"}), 
            (400, {"desc": "invalid value (>10)"})])
    
        with gedge.mock_connect(writee) as writeeSession:            
            with gedge.mock_connect(writer, writeeSession._comm) as writerSession:
                with writerSession.connect_to_remote(writee.key) as remote:
                    with pytest.raises(TagLookupError, match= "Tag None not found on node writee"):
                        tagBind = remote.tag_bind(None)

    def test_subnode_slash(self):
        from gedge.node.subnode import SubnodeSession
        otherNode = NodeConfig("test/node")
        config = NodeConfig("my/node")

        subnode0 = SubnodeConfig("subnode0", config.ks, {}, {}, {})

        subnode1 = SubnodeConfig("subnode1", config.ks, {}, {}, {})
        subnode0.subnodes["subnode1"] = subnode1

        config.subnodes[subnode0.name] = subnode0


        with gedge.mock_connect(config) as session:
            with session.connect_to_remote(otherNode.key) as remote:
                from gedge.node.subnode import RemoteSubConnection    

                with pytest.raises(ValueError, match="No subnode "):
                    subRemote = remote.subnode("subnode0/")

    def test_subnode_no_slash(self):
        from gedge.node.subnode import SubnodeSession
        otherNode = NodeConfig("test/node")
        config = NodeConfig("my/node")

        subnode0 = SubnodeConfig("subnode0", config.ks, {}, {}, {})

        subnode1 = SubnodeConfig("subnode1", config.ks, {}, {}, {})
        subnode0.subnodes["subnode1"] = subnode1

        config.subnodes[subnode0.name] = subnode0


        with gedge.mock_connect(config) as session:
            with session.connect_to_remote(otherNode.key) as remote:
                from gedge.node.subnode import RemoteSubConnection    

                with pytest.raises(ValueError, match="No subnode subnode12345"):
                    subRemote = remote.subnode("subnode12345")

    def test_write_tag_no_path(self):
        writer = NodeConfig.from_json5_str('''{"key": "test/tag/bind/writer"}''')
        writee = NodeConfig.from_json5_str('''{"key": "test/tag/bind/writee"}''')

        def handler(query: gedge.TagWriteQuery) -> None:
            if query.value > 10:
                query.reply(400)
                return
            query.reply(200)

        tag = writee.add_writable_tag("tag/write", DataType.INT, handler, [
            (200, {"desc": "tag updated with value"}), 
            (400, {"desc": "invalid value (>10)"})])


        with gedge.mock_connect(writee) as writeeSession:            
            with gedge.mock_connect(writer, writeeSession._comm) as writerSession:
                with writerSession.connect_to_remote(writee.key) as remote:
                    remote.tags["tag/write"] = tag
                    with pytest.raises(TagLookupError, match="Tag None not found on node writee"):
                        reply = remote.write_tag(None, value=9)

    def test_write_tag_no_value(self):
        writer = NodeConfig.from_json5_str('''{"key": "test/tag/bind/writer"}''')
        writee = NodeConfig.from_json5_str('''{"key": "test/tag/bind/writee"}''')

        def handler(query: gedge.TagWriteQuery) -> None:
            if query.value > 10:
                query.reply(400)
                return
            query.reply(200)

        tag = writee.add_writable_tag("tag/write", DataType.INT, handler, [
            (200, {"desc": "tag updated with value"}), 
            (400, {"desc": "invalid value (>10)"})])


        with gedge.mock_connect(writee) as writeeSession:            
            with gedge.mock_connect(writer, writeeSession._comm) as writerSession:
                with writerSession.connect_to_remote(writee.key) as remote:
                    remote.tags["tag/write"] = tag
                    reply = remote.write_tag("tag/write", value=None)
                    
                    # Should we include an additional check or something for this???

    def test_call_method(self, capsys):
        def handler(query: gedge.MethodQuery):
            name = query.params["name"]
            speed = query.params["speed"]
            if len(name) > 30:
                query.reply(401)
                return
            if speed < 0 or speed > 100:
                query.reply(400, body={"res1": speed})
                return
            if name == 'EXCEPTION':
                raise ValueError("exception thrown in method handler")
            query.reply(200, body={"res1": speed})
            time.sleep(2)
            query.reply(200, body={"res1": speed})
        
        here = pathlib.Path(__file__).parent
        callee = gedge.NodeConfig.from_json5(str(here / "test_callee.json5"))
        callee.add_method_handler("call/method", handler=handler)
        

        caller = NodeConfig.from_json5_str('''{"key": "test/method/calls/caller"}''')

        def my_callback(reply):
            print("Callback received:")

            if reply.error:
                print(f"Error: {reply.code}, {reply.error}")
            else:
                print(f"Success: {reply.code}, {reply.props}, {reply.body}")

        with gedge.mock_connect(callee) as calleeSession:
            with gedge.mock_connect(caller, calleeSession._comm) as callerSession:
                with callerSession.connect_to_remote(callee.key) as remote:
                    remote.methods = callee.methods
                    with pytest.raises(MethodLookupError, match="Method  not found on node callee"):
                        remote.call_method("", my_callback, name="Jonas", speed=0)

    def test_call_method_iter_missing_method(self):
        def handler(query: gedge.MethodQuery):
            name = query.params["name"]
            speed = query.params["speed"]
            if len(name) > 30:
                query.reply(401)
                return
            if speed < 0 or speed > 100:
                query.reply(400, body={"res1": speed})
                return
            if name == 'EXCEPTION':
                raise ValueError("exception thrown in method handler")
            query.reply(200, body={"res1": speed})
        
        # pytest.fail("Yeah Dawg")
        here = pathlib.Path(__file__).parent
        callee = gedge.NodeConfig.from_json5(str(here / "test_callee.json5"))
        callee.add_method_handler("call/method", handler=handler)
        

        caller = NodeConfig.from_json5_str('''{"key": "test/method/calls/caller"}''')

        with gedge.mock_connect(callee) as calleeSession:
            with gedge.mock_connect(caller, calleeSession._comm) as callerSession:
                with callerSession.connect_to_remote(callee.key) as remote:
                    with pytest.raises(MethodLookupError, match="Method call/method not found on node callee"):
                        responses = list(remote.call_method_iter("call/method", name=0, speed=0))

    def test_call_method_iter_missing_param(self):
        def handler(query: gedge.MethodQuery):
            name = query.params["name"]
            speed = query.params["speed"]
            if len(name) > 30:
                query.reply(401)
                return
            if speed < 0 or speed > 100:
                query.reply(400, body={"res1": speed})
                return
            if name == 'EXCEPTION':
                raise ValueError("exception thrown in method handler")
            query.reply(200, body={"res1": speed})
        
        # pytest.fail("Yeah Dawg")
        here = pathlib.Path(__file__).parent
        callee = gedge.NodeConfig.from_json5(str(here / "test_callee.json5"))
        callee.add_method_handler("call/method", handler=handler)
        

        caller = NodeConfig.from_json5_str('''{"key": "test/method/calls/caller"}''')

        with gedge.mock_connect(callee) as calleeSession:
            with gedge.mock_connect(caller, calleeSession._comm) as callerSession:
                with callerSession.connect_to_remote(callee.key) as remote:
                    remote.methods = callee.methods
                    with pytest.raises(LookupError, match="Parameter speed defined in config but not included in method call for method call/method"):
                        responses = list(remote.call_method_iter("call/method", name="Jonas"))



