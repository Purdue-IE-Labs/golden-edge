from __future__ import annotations

from gedge import proto
from gedge.node.data_type import DataType
from gedge.node.tag_data import TagData

from typing import Any, Self, TYPE_CHECKING
if TYPE_CHECKING: # pragma: no cover
    from gedge.node.gtypes import TagValue

class Prop:
    def __init__(self, type: DataType, value: TagData):
        '''
        Basic Initialization of a prop object

        Args:
            type (DataType): The type of the prop
            value (TagData): A TagData object containing the value

        Returns:
            Prop: A new Prop object
        
        Example::

            tagData = TagData.from_value(20, DataType.INT)
            prop = Prop(DataType.INT, tagData)
        '''

        self.type = type
        self.value = value
    
    def to_proto(self) -> proto.Prop:
        '''
        Creates a new proto verion of the current Prop object

        Args:
            None (None):
        
        Returns:
            proto.Prop: The newly created proto.Prop object

        Example::

            tagData = TagData.from_value(20, DataType.INT)
            prop = Prop(DataType.INT, tagData)
            propProto = prop.to_proto()
        '''
        return proto.Prop(type=self.type.to_proto(), value=self.value.to_proto()) 
    
    def to_value(self) -> Any:
        '''
        Returns the TagValue of the current Prop object

        Example Implementation: 

        Arguments:
            None (None):
        
        Returns:
            TagValue: The TagValue of the current Prop object

        Example::

            tagData = TagData.from_value(20, DataType.INT)
            prop = Prop(DataType.INT, tagData)
            newTagData = pror.to_value()
        '''
        return self.value.to_py()
    
    @classmethod
    def from_proto(cls, prop: proto.Prop) -> Self:
        '''
        Creates a Prop object from the passed proto.Prop

        Args:
            prop (prop.Proto): The proto object the Prop object is being created from

        Returns:
            Prop: A Prop object
        
        Example::

            tagData = TagData.from_value(20, DataType.INT)
            prop = Prop(DataType.INT, tagData)

            propProto = prop.to_proto()

            newProp = Prop.from_proto(propProto)
            
        '''
        if (not isinstance(prop, proto.Prop)):
            raise ValueError(f"The passed type for from_proto is not the correct type")
        type = DataType.from_proto(prop.type)
        value = TagData.from_proto(prop.value, type)
        return cls(type, value)
    
    @classmethod
    def from_value(cls, value: TagValue) -> Self:
        '''
        Creates a Prop object from the passed value

        Args:
            value (TagValue): The passed value that the Prop is being created from

        Returns:
            Prop: The created Prop object

        Example::

            prop = Prop.from_value(10)
            prop.type == int
            prop.value.to_py() == 10
        '''
        type_ = cls.intuit_type(value)
        value_ = TagData.from_value(value, type_)
        return cls(type_, value_)
    
    @staticmethod
    def intuit_type(value: Any) -> DataType:
        '''
        Returns the DataType type of the passed value

        Args:
            value (any): The value that the data type is being extracted from

        Returns:
            DataType: The corresponding DataType object of the type of the value

        Example:

            Prop.intuit_type(10) == DataType.INT

            Prop.intuit_type("Hello World") == DataType.STRING
        '''
        if isinstance(value, str):
            return DataType.STRING
        elif isinstance(value, bool):
            return DataType.BOOL
        elif isinstance(value, int):
            return DataType.INT
        elif isinstance(value, float):
            return DataType.FLOAT
        elif isinstance(value, list):
            if len(value) == 0:
                return DataType.LIST_INT
            val0 = value[0]
            if isinstance(val0, str):
                return DataType.LIST_STRING
            elif isinstance(val0, bool):
                return DataType.LIST_BOOL
            elif isinstance(val0, int):
                return DataType.LIST_INT
            elif isinstance(val0, float):
                return DataType.LIST_FLOAT
        raise ValueError(f"Illegal type for property. Allowed properties are str, int, float, bool. value is of type {type(value)}")
    
    def __repr__(self):
        return f"{self.value.to_py()}"


class Props:
    def __init__(self, props: dict[str, Prop]):
        '''
        Basic initalization of the Props object

        Args:
            props (dict[str, Prop]): A dictionary of strings and Prop objects

        Returns:
            Props: The created Props object
        
        Example::

            prop_dictionary = {}
            for i in range(0, 10):
                prop = Prop(DataType.INT, TagData.from_value(i, DataType.INT))
                prop_dictionary.update({f"{i}": prop})
            
            props = Props(prop_dictionary)
        '''
        self.props = props
    
    def to_proto(self) -> dict[str, proto.Prop]:
        '''
        Converts the current Props object to a proto dictionary

        Args:
            None: None

        Returns:
            dict[str, proto.Prop]: The created proto object

        Example::

            prop_dictionary = {}
            for i in range(0, 10):
                prop = Prop(DataType.INT, TagData.from_value(i, DataType.INT))
                prop_dictionary.update({f"{i}": prop})
            
            props = Props(prop_dictionary)

            propsProto = props.to_proto()
        '''
        return {key:value.to_proto() for key, value in self.props.items()}
    
    def to_value(self) -> dict[str, Any]:
        '''
        Converts the current Props object to the TagValues of the stored Props

        Args:
            None: None

        Returns:
            dict[str, Any]: The TagValues of the stored Props

        Example::

             prop_dictionary = {}
            for i in range(0, 10):
                prop = Prop(DataType.INT, TagData.from_value(i, DataType.INT))
                prop_dictionary.update({f"{i}": prop})
            
            props = Props(prop_dictionary)

            for i in range(0, 10):
                assert props.to_value().get(f"{i}") == prop_dictionary.get(f"{i}").to_value()
        '''
        return {key:value.to_value() for key, value in self.props.items()}
    
    # 'Any' added because the proto version of a dict is a MessageMap, which means that 
    # Pylance thinks this is an error of types, even though it is not
    @classmethod
    def from_proto(cls, props: dict[str, proto.Prop] | Any) -> Self:
        '''
        Creates a Props object from the passed proto dictionary

        Args:
            props (dict[str, proto.Prop]): The passed proto dictionary being used to create the Props object

        Returns:
            Props: The created Props object

        Example::

            prop_dictionary = {}
            for i in range(0, 10):
                prop = Prop(DataType.INT, TagData.from_value(i, DataType.INT))
                prop_dictionary.update({f"{i}": prop})
            
            props = Props(prop_dictionary)

            propsProto = props.to_proto()

            newProps = Props.from_proto(propsProto)
        '''
        return cls({key:Prop.from_proto(value) for key, value in props.items()})
    
    @classmethod
    def from_value(cls, props: dict[str, Any]) -> Self:
        '''
        Creates a Props object from the passed props dictionary

        Note: For the creation of this Props object the dictionary should **NOT** include a Prop object for each index

        Args:
            props (dict[str, Any]): The dictionary being used to create the new Props object

        Returns:
            Props: The created Props object

        Example::

            prop_dictionary = {}
            for i in range(0, 10):
                # Note how we don't create a Prop object and pass that
                # We just pass the integer to the dictionary
                prop_dictionary.update({f"{i}": i})

            props = Props.from_value(prop_dictionary)
        '''
        return cls({key:Prop.from_value(value) for key, value in props.items()})
    
    @classmethod
    def from_json5(cls, props: Any) -> Self:
        '''
        Creates a Props object from the passed json5 file

        Args:
            props (Any): The json5 file being used to create the Props object

        Returns:
            Props: The created Props object
        '''
        if not isinstance(props, dict):
            raise ValueError(f"invalid props {props}")
        return cls.from_value(props)
    
    @classmethod
    def empty(cls) -> Self:
        '''
        Returns an instance of the current Props class that is completely empty

        Args:
            None: None

        Returns:
            Props: The emptied Props object

        Example::
            
            prop_dictionary = {}
            for i in range(0, 10):
                prop = Prop(DataType.INT, TagData.from_value(i, DataType.INT))
                prop_dictionary.update({f"{i}": prop})
            
            props = Props(prop_dictionary)

            props = props.empty()

            # This evaluates to True
            assert props.props == {}
        '''
        return cls({})
    
    def add_prop(self, key: str, value: Any):
        '''
        Creates a new Prop with the passed value and adds it to the current Props object at the passed key

        Args:
            key (str): The location where the new Prop is being added
            value (Any): The value the new Prop is being created from

        Returns:
            None: None

        Example::

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
        '''
        self.props[key] = Prop.from_value(value)
    
    def __repr__(self):
        return f"{self.props}"
    