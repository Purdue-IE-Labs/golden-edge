import gedge
import pytest

from gedge.node.data_type import DataType
from gedge import proto

class TestSanity:
    
    @pytest.mark.parametrize("type", [
        (int),
        (float),
        (str),
        (bool),
        (list[int]),
        (list[float]),
        (list[str]),
        (list[bool]),
        (DataType.INT),
        (DataType.LONG),
        (DataType.FLOAT),
        (DataType.STRING),
        (DataType.BOOL),
        (DataType.LIST_INT),
        (DataType.LIST_LONG),
        (DataType.LIST_FLOAT),
        (DataType.LIST_STRING),
        (DataType.LIST_BOOL),
        (None)
    ], ids=(
        "int",
        "float",
        "str",
        "bool",
        "list[int]",
        "list[float]",
        "list[str]",
        "list[bool]",
        "DataType.INT",
        "DataType.LONG",
        "DataType.FLOAT",
        "DataType.STRING",
        "DataType.BOOL",
        "DataType.LIST_INT",
        "DataType.LIST_LONG",
        "DataType.LIST_FLOAT",
        "DataType.LIST_STRING",
        "DataType.LIST_BOOL",
        "None"
    ))
    def test_from_type(self, type):
        # Creates a DataType instance from type
        if type is None:
            with pytest.raises(ValueError, match="Illegal type None for tag"):
                instance = DataType.from_type(type)
                return
        instance = DataType.from_type(type)

        # The passed type as a string
        parsed_string = f"{type}"

        parsed_string = parsed_string.replace("<class '", "")
        parsed_string = parsed_string.replace("'>", "")

        # Converts the passed type to uppercase
        parsed_string = parsed_string.upper()

        # Replaces any left brackets with an underscore
        parsed_string = parsed_string.replace('[', '_')

        # Parses all right brackets
        parsed_string = parsed_string.replace(']', '')

        # Determines if the the parsed type contains "STRING"
        if (parsed_string.find("STRING") == -1):

            # Replaces all instances of "STR" with "STRING"
            parsed_string = parsed_string.replace("STR", "STRING")

        # Parses all instances of "DATATYPE." in the passed type
        parsed_string = parsed_string.replace("DATATYPE.", "")

        assert isinstance(instance, DataType)
        assert str(instance) == f"DataType.{parsed_string}"

    @pytest.mark.parametrize("proto_enum, expected_value", [
        (proto.DataType.INT, DataType.INT),
        (proto.DataType.LONG, DataType.LONG),
        (proto.DataType.FLOAT, DataType.FLOAT),
        (proto.DataType.STRING, DataType.STRING),
        (proto.DataType.BOOL, DataType.BOOL),
        (proto.DataType.LIST_INT, DataType.LIST_INT),
        (proto.DataType.LIST_LONG, DataType.LIST_LONG),
        (proto.DataType.LIST_FLOAT, DataType.LIST_FLOAT),
        (proto.DataType.LIST_STRING, DataType.LIST_STRING),
        (proto.DataType.LIST_BOOL, DataType.LIST_BOOL),
    ])
    def test_from_proto(self, proto_enum, expected_value):
        instance = DataType.from_proto(proto_enum)
        assert isinstance(instance, DataType)
        assert instance == expected_value

    @pytest.mark.parametrize("type, expected_value", [
        ("int", DataType.INT),
        ("long", DataType.LONG),
        ("float", DataType.FLOAT),
        ("string", DataType.STRING),
        ("bool", DataType.BOOL),
        ("list[int]", DataType.LIST_INT),
        ("list[long]", DataType.LIST_LONG),
        ("list[float]", DataType.LIST_FLOAT),
        ("list[string]", DataType.LIST_STRING),
        ("list[bool]", DataType.LIST_BOOL),
        ("dict[any]", None)
    ])
    def test_from_json5(self, type, expected_value):
        if expected_value is None:
            with pytest.raises(ValueError, match="Invalid type None"):
                instance = DataType.from_json5(type)
                return        
        instance = DataType.from_json5(type)
        assert isinstance(instance, DataType)
        assert instance == expected_value

    @pytest.mark.parametrize("proto_enum, expected_value", [
        (proto.DataType.INT, DataType.INT),
        (proto.DataType.LONG, DataType.LONG),
        (proto.DataType.FLOAT, DataType.FLOAT),
        (proto.DataType.STRING, DataType.STRING),
        (proto.DataType.BOOL, DataType.BOOL),
        (proto.DataType.LIST_INT, DataType.LIST_INT),
        (proto.DataType.LIST_LONG, DataType.LIST_LONG),
        (proto.DataType.LIST_FLOAT, DataType.LIST_FLOAT),
        (proto.DataType.LIST_STRING, DataType.LIST_STRING),
        (proto.DataType.LIST_BOOL, DataType.LIST_BOOL),
    ])
    def test_to_proto_from_proto(self, proto_enum, expected_value):
        instance = DataType.from_proto(proto_enum)
        assert instance == expected_value
        assert instance.to_proto() == proto_enum


    # Round trip, make a DataType object, get the to_proto then make another with from_proto and see if it works
