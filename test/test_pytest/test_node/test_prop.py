import pytest
import gedge

from gedge.node.prop import Prop
from gedge.node.data_type import DataType
from gedge.node.tag_data import TagData

class TestProp:
    class TestSanity:
        def test_to_proto(self):
            tagData = TagData.from_value(20, DataType.INT)
            prop = Prop(DataType.INT, tagData)

            propProto = prop.to_proto()

            assert propProto.type == prop.type.to_proto()
            assert propProto.value == prop.value.to_proto()

        def test_to_value(self):
            tagData = TagData.from_value(20, DataType.INT)
            prop = Prop(DataType.INT, tagData)

            assert prop.to_value() == tagData.to_py()

        def test_from_proto(self):
            # Create the proto object
            tagData = TagData.from_value(20, DataType.INT)
            prop = Prop(DataType.INT, tagData)

            propProto = prop.to_proto()

            newProp = Prop.from_proto(propProto)

            assert newProp.type == prop.type
            assert newProp.value.to_py() == prop.value.to_py()
        
        @pytest.mark.parametrize("value, type", [
            ("Hello world", DataType.STRING),
            (20, DataType.INT),
            (20.1, DataType.FLOAT),
            (True, DataType.BOOL),
            ([1, 2, 3, 4, 5], DataType.LIST_INT),
            (["Hi", "Hello", "Hi again"], DataType.LIST_STRING),
            ([1.1, 2.2, 3.3, 4.4], DataType.LIST_FLOAT),
            ([True, False, True, False], DataType.LIST_BOOL),
            (DataType,"Error")
        ], ids=(
            "String",
            "Int",
            "Float",
            "Bool",
            "List of Ints",
            "List of Strings",
            "List of Floats",
            "List of Bools",
            "Error",
        ))
        def test_from_value(self, value, type):
            if (type == "Error"):
                with pytest.raises(ValueError, match="Illegal type for property. Allowed properties are str, int, float, bool. value is of type <class 'enum.EnumType'>"):
                    Prop.from_value(value)
            else:
                prop = Prop.from_value(value)

                assert prop.type == type
                if (type == DataType.FLOAT):
                    assert round(prop.value.to_py(), 1) == value
                    assert prop.value.to_py() == value
                elif(type == DataType.LIST_FLOAT):
                    for x in range(0, len(value)):
                        assert prop.value.to_py()[x] == value[x]
                else:
                    assert prop.value.to_py() == value

        @pytest.mark.parametrize("value, type", [
            ("Hello world", DataType.STRING),
            (20, DataType.INT),
            (20.1, DataType.FLOAT),
            (True, DataType.BOOL),
            ([1, 2, 3, 4, 5], DataType.LIST_INT),
            (["Hi", "Hello", "Hi again"], DataType.LIST_STRING),
            ([1.1, 2.2, 3.3, 4.4], DataType.LIST_FLOAT),
            ([True, False, True, False], DataType.LIST_BOOL),
            (DataType,"Error"),
            ([], DataType.LIST_INT)
        ],ids=(
            "String",
            "Int",
            "Float",
            "Bool",
            "List of Ints",
            "List of Strings",
            "List of Floats",
            "List of Bools",
            "Error",
            "Empty List"
        ))
        def test_intuit_type(self, value, type):
            if (type == "Error"):
                with pytest.raises(ValueError, match="Illegal type for property. Allowed properties are str, int, float, bool. value is of type <class 'enum.EnumType'>"):
                    Prop.intuit_type(value)
            else:
                assert type == Prop.intuit_type(value)

        @pytest.mark.parametrize("value", [
            ("Hello world"),
            (20),
            (20.1),
            (True),
            ([1, 2, 3, 4, 5]),
            (["Hi", "Hello", "Hi again"]),
            ([1.1, 2.2, 3.3, 4.4]),
            ([True, False, True, False]),
        ], ids=(
            "String",
            "Int",
            "Float",
            "Bool",
            "List of Ints",
            "List of Strings",
            "List of Floats",
            "List of Bools",
        ))
        def test_repr(self, value):
            prop = Prop.from_value(value)

            assert str(prop) == str(value)


    class TestEmpty:
        def test_init(self):
            prop = Prop(None, None)
        
        def test_to_proto(self):
            prop = Prop(type=None, value=None)

            prop.to_proto()

        def test_to_value(self):
            prop = Prop(None, None)

            prop.to_value()

        def test_from_proto(self):
            prop = Prop.from_proto(None)

        def test_from_value(self):
            with pytest.raises(ValueError, match="Illegal type for property. Allowed properties are str, int, float, bool. value is of type <class 'NoneType'>"):
                prop = Prop.from_value(None)


from gedge.node.prop import Props

class TestProps:
    class TestSanity:
        def test_init(self):
            prop_dictionary = {}
            for i in range(0, 10):
                prop = Prop(DataType.INT, TagData.from_value(i, DataType.INT))
                prop_dictionary.update({f"{i}": prop})
            
            props = Props(prop_dictionary)

            for i in range(0, 10):
                assert props.props.get(f"{i}") == prop_dictionary[f"{i}"]

        def test_to_proto(self):
            prop_dictionary = {}
            for i in range(0, 10):
                prop = Prop(DataType.INT, TagData.from_value(i, DataType.INT))
                prop_dictionary.update({f"{i}": prop})
            
            props = Props(prop_dictionary)

            propsProto = props.to_proto()

            for i in range(0, 10):
                assert propsProto.get(f"{i}") == props.props[f"{i}"].to_proto()

        def test_to_value(self):
            prop_dictionary = {}
            for i in range(0, 10):
                prop = Prop(DataType.INT, TagData.from_value(i, DataType.INT))
                prop_dictionary.update({f"{i}": prop})
            
            props = Props(prop_dictionary)

            for i in range(0, 10):
                assert props.to_value().get(f"{i}") == prop_dictionary.get(f"{i}").to_value()

        def test_from_proto(self):
            # Generate the proto
            prop_dictionary = {}
            for i in range(0, 10):
                prop = Prop(DataType.INT, TagData.from_value(i, DataType.INT))
                prop_dictionary.update({f"{i}": prop})
            
            props = Props(prop_dictionary)

            propsProto = props.to_proto()

            newProps = Props.from_proto(propsProto)

            for i in range(0, 10):
                assert newProps.props.get(f"{i}").to_value() == props.props.get(f"{i}").to_value()

        def test_from_value(self):
            prop_dictionary = {}
            for i in range(0, 10):
                prop_dictionary.update({f"{i}": i})

            props = Props.from_value(prop_dictionary)

            for i in range(0, 10):
                assert props.props.get(f"{i}").to_value() == prop_dictionary.get(f"{i}")
        
        def test_from_json5(self):
            prop_dictionary = {}
            for i in range(0, 10):
                prop_dictionary.update({f"{i}": i})

            props = Props.from_json5(prop_dictionary)

            for i in range(0, 10):
                assert props.props.get(f"{i}").to_value() == prop_dictionary.get(f"{i}")

        def test_empty(self):
            prop_dictionary = {}
            for i in range(0, 10):
                prop = Prop(DataType.INT, TagData.from_value(i, DataType.INT))
                prop_dictionary.update({f"{i}": prop})
            
            props = Props(prop_dictionary)

            for i in range(0, 10):
                assert props.props.get(f"{i}") == prop_dictionary.get(f"{i}")

            props = props.empty()

            assert props.props == {}

        def test_add_prop(self):
            prop_dictionary = {}
            for i in range(0, 10):
                prop = Prop(DataType.INT, TagData.from_value(i, DataType.INT))
                prop_dictionary.update({f"{i}": prop})
            
            props = Props(prop_dictionary)

            for i in range(0, 10):
                assert props.props.get(f"{i}") == prop_dictionary.get(f"{i}")

            props.add_prop("11", 11)

            prop_dictionary.update({"11": Prop(DataType.INT, TagData.from_value(11, DataType.INT))})

            for i in range(0, 11):
                assert props.props.get(f"{i}") == prop_dictionary.get(f"{i}")

        def test_repr(self):
            prop_dictionary = {}
            for i in range(0, 10):
                prop = Prop(DataType.INT, TagData.from_value(i, DataType.INT))
                prop_dictionary.update({f"{i}": prop})
            
            props = Props(prop_dictionary)

            assert str(props) == str(prop_dictionary)



