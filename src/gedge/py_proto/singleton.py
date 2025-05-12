from __future__ import annotations

# TODO: singletons are awful, but it seems to make sense for a CLI argument here

from typing import Self, TYPE_CHECKING

if TYPE_CHECKING:
    from gedge.py_proto.data_model_config import DataModelConfig


class Singleton:
    '''
    Singleton to hold CLI arguments

    Parameters:
        model_dir: str - root directory where models will go  
        json5_dir: str - root directory to search for other json5 models
    Returns:
        self: Singleton instance
        
    Example:  
    gedge --model_dir "./foo" pull bar/baz  
    result: ./foo/bar/baz/v1.json5  
    '''

    def __new__(cls, model_dir: str | None = None, json5_dir: str | None = None, models: dict[str, DataModelConfig] = {}) -> Self:
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
            cls.model_dir = model_dir
            cls.json5_dir = json5_dir
            cls.models = models
        return cls.instance
    
    def set_model_dir(self, path: str) -> None:
        self.model_dir = path
    
    def get_model_dir(self) -> str | None:
        return self.model_dir
    
    def set_json5_dir(self, path: str) -> None:
        self.json5_dir = path
    
    def get_json5_dir(self) -> str | None:
        return self.json5_dir
    
    def add_model(self, config: DataModelConfig) -> None:
        self.models[config.path] = config
    
    def get_model(self, path: str) -> DataModelConfig | None:
        if path in self.models:
            return self.models[path]
        return None