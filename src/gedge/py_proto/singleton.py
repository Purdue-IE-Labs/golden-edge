
# TODO: singletons are awful, but it seems to make sense for a CLI argument here

from typing import Self


class Singleton:
    def __new__(cls, model_dir: str = "") -> Self:
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
            cls.model_dir = model_dir
        return cls.instance
    
    def set_model_dir(self, path: str):
        self.model_dir = path
    
    def get_model_dir(self):
        return self.model_dir