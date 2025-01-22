from typing import Any, Dict
from gedge.proto import TagData, DataType

class Tag:
    def __init__(self, name: str, type: DataType, properties: Dict[str, Any] = {}):
        self.name = name
        self.type = type
        self.properties = properties

    def convert(self, value: Any) -> Any:
        match self.type:
            case TagData.DataType.INT:
                return int(value)
            case TagData.DataType.FLOAT:
                return float(value)
            case TagData.DataType.STRING:
                return str(value)
            case TagData.DataType.BOOL:
                return bool(value)
            case TagData.DataType.LIST_INT:
                return list([int(x) for x in value])
            case TagData.DataType.LIST_FLOAT:
                return list([float(x) for x in value])
            case TagData.DataType.LIST_STRING:
                return list([str(x) for x in value])
            case TagData.DataType.LIST_BOOL:
                return list([bool(x) for x in value])
        raise ValueError
