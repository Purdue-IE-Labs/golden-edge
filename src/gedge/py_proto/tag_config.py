from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
import os

from gedge import proto

from typing import Any, Self, TYPE_CHECKING

from gedge.comm.keys import key_join
from gedge.node.method_response import ResponseConfig
from gedge.py_proto.conversions import list_from_json5, list_from_proto
from gedge.py_proto.data_model_config import DataModelConfig
from gedge.py_proto.tag_group_config import TagGroupConfig
from gedge.py_proto.tag_write_config import TagWriteConfig
if TYPE_CHECKING:
    from gedge.py_proto.data_model_config import DataItemConfig
    from gedge.node.gtypes import TagWriteHandler

@dataclass
class Tag:
    config: DataItemConfig

    # this is so that we can specify tags of models as writable without specifying 
    # the entire thing as writable
    # if this tag is a base type, we access the response configs by self.write_config[self.path].responses
    # TODO: eventually support wildcards here? 
    # TODO: not TagWriteHandler | None but we provide a default one that just raises an exception?
    write_config: dict[str, tuple[list[ResponseConfig], TagWriteHandler | None]]
    group_config: dict[str, str] # maps a path on this tag to a group. If the tag is a base_type, tag.group[tag.path] is the group name

    @property
    def path(self) -> str:
        return self.config.path
    
    def get_config(self, path: str) -> DataItemConfig:
        # get a nested DataItemConfig from a path that could include multiple models
        # example: tag/1 is a tag with items, one of them being pump, which has a base, which has a girth
        # path = tag/1/pump/base/girth
        # if we get items with pu/ and pump/, we want to take pump
        # start with res = tag/1
        if path == self.path:
            return self.config

        def _get_config(model: DataModelConfig, curr_path: str) -> DataItemConfig:
            matches = [item for item in model.items if path.startswith(key_join(curr_path, item.path))]
            if not matches:
                raise ValueError
            best_match = max(matches, key = lambda item: len(os.path.commonprefix([path, key_join(curr_path, item.path)])))

            # base case
            if path == key_join(curr_path, best_match.path):
                return best_match

            m = best_match.load_model()
            if not m:
                raise ValueError
            config = _get_config(m, key_join(curr_path, best_match.path))
            return config

        m = self.load_model()
        if not m:
            raise ValueError
        return _get_config(m, self.path)

    @classmethod
    def from_json5(cls, j: Any, writable: bool | None = None) -> Self:
        from gedge.py_proto.data_model_config import DataItemConfig
        if not isinstance(j, dict):
            raise ValueError(f"invalid tag, expected dict, got {j}")
        if "model_file" in j:
            raise ValueError("Cannot provide path to json5 model file in node config! Use model_path.")
        if "model" in j:
            raise ValueError("Cannot provide model definition in node config! Use model_path.")
        config = DataItemConfig.from_json5(j)

        w = writable
        if w is None:
            w = j.get("writable", False)
        
        if w and config.is_model_ref():
            raise ValueError(f"model {config.path} cannot be writable, only tags of it")

        responses = []
        if w: 
            responses = list_from_json5(ResponseConfig, j.get("responses", []))
            return cls(config, {config.path: (responses, None)}, {})
        return cls(config, {}, {})
    
    def is_valid_path(self, path: str) -> bool:
        # get a nested DataItemConfig from a path that could include multiple models
        # example: tag/1 is a tag with items, one of them being pump, which has a base, which has a girth
        # path = tag/1/pump/base/girth
        # if we get items with pu/ and pump/, we want to take pump
        # start with res = tag/1
        if path == self.path:
            return True

        def _is_valid(model: DataModelConfig, curr_path: str) -> bool:
            matches = [item for item in model.items if path.startswith(key_join(curr_path, item.path))]
            if not matches:
                return False
            best_match = max(matches, key = lambda item: len(os.path.commonprefix([path, key_join(curr_path, item.path)])))

            # base case
            if path == key_join(curr_path, best_match.path):
                return True

            m = best_match.load_model()
            if not m:
                return False
            return _is_valid(m, key_join(curr_path, best_match.path))

        m = self.load_model()
        if not m:
            return False
        return _is_valid(m, self.path)
    
    def add_writable_config_json5(self, j: Any):
        # assumption that this is a valid path
        if isinstance(j, str):
            self.write_config[j] = ([], None)
            return
        path = j["path"]
        responses = list_from_json5(ResponseConfig, j.get("responses", []))
        self.write_config[path] = (responses, None)
    
    def add_group(self, path: str, group_path: str):
        self.group_config[path] = group_path
    
    def is_base_type(self):
        return self.config.is_base_type()
    
    def is_model_ref(self):
        return self.config.is_model_ref()
    
    def is_writable(self):
        return self.is_writable_base_tag() or self.is_writable_model_tag()
    
    def is_writable_base_tag(self):
        return self.is_base_type() and self.path in self.write_config
    
    def is_writable_model_tag(self):
        return self.is_model_ref() and len(self.write_config) > 0
    
    def load_model(self) -> DataModelConfig | None:
        return self.config.type.load_model()
    
    def add_write_handler(self, path: str, handler: TagWriteHandler):
        if path not in self.write_config:
            raise LookupError(f"invalid path to add a writable tag, {path}")
        responses, _ = self.write_config[path]
        self.write_config[path] = (responses, handler)

# def get_config_from_path(tags: dict[str, Tag], path: str) -> DataItemConfig:
#     best_match = max(list(tags.keys()), key = lambda p : len(os.path.commonprefix([p, path])))
#     tag = tags[best_match]
#     return tag.get_config(path)

@dataclass
class TagConfig:
    tags: dict[str, Tag]

    @property
    def paths(self) -> list[str]:
        return list(self.tags.keys())

    def to_proto(self) -> proto.TagConfig:
        data_config = []
        write_config = []
        group_config = []
        for tag in self.tags.values():
            data_config.append(tag.config.to_proto())
            for path, responses in tag.write_config.items():
                write_config.append(TagWriteConfig(path, responses[0]).to_proto())
        groups = self.all_groups()
        for group_path, list_paths in groups.items():
            print(group_path, list_paths)
            group_config.append(TagGroupConfig(group_path, list_paths).to_proto())
        return proto.TagConfig(data_config=data_config, write_config=write_config, group_config=group_config)

    @classmethod
    def from_proto(cls, tag_config: proto.TagConfig) -> Self:
        from gedge.py_proto.data_model_config import DataItemConfig
        data_config = list(tag_config.data_config)
        write_config = list(tag_config.write_config)
        group_config = list(tag_config.group_config)
        d_map = {d.path:d for d in data_config}
        w_map = {w.path:w for w in write_config}
        g_map = {g.path:g for g in group_config} # group path : list(paths)

        tags: list[Tag] = []
        for path, config in d_map.items():
            t = Tag(DataItemConfig.from_proto(config), {}, {})
            included = {w.path: w for w in w_map.values() if w.path.startswith(path)}
            for path, conf in included.items():
                t.write_config[path] = (list_from_proto(ResponseConfig, conf.responses), None)
            tags.append(t)
        
        tc = cls({t.path: t for t in tags})
        for group_conf in g_map.values():
            g_path = group_conf.path
            paths = list(group_conf.items)
            for path in paths:
                t = tc.get_tag(path)
                t.group_config[path] = g_path
        print(tc.all_groups())
        return tc
    
    @classmethod
    def from_json5(cls, tags: Any, writable_tags: Any, group_tags: Any) -> Self:
        if not isinstance(tags, list):
            raise ValueError(f"invalid tags, tags must be a list, got {tags}")
        if not isinstance(writable_tags, list):
            raise ValueError(f"writable tags")
        if not isinstance(group_tags, list):
            raise ValueError("group tags")
        ts: list[Tag] = [Tag.from_json5(t) for t in tags]
        self = cls({t.path: t for t in ts})
        self.add_writable_config_json5(writable_tags)
        self.add_group_config_json5(group_tags)
        return self
    
    def add_group_config_json5(self, j: list):
        # TODO: handle wildcards
        # TODO: check before connection if any are part of more than one group
        for group in j:
            group = TagGroupConfig.from_json5(group)
            for path in group.items:
                t = [t for t in self.tags.values() if path.startswith(t.path)][0]
                if not t.is_valid_path(path):
                    raise LookupError(f"invalid group path {path}")
                c = t.get_config(path)
                if c.is_model_ref():
                    # TODO: expand this to include all its tags
                    raise ValueError(f"model {path} cannot be writable, only tags of it")
                t.add_group(path, group.path)
    
    def add_writable_config_json5(self, j: list):
        for config in j:
            if isinstance(config, str):
                path = config
            else:
                path = config["path"]
            t = [t for t in self.tags.values() if path.startswith(t.path)][0]
            if not t.is_valid_path(path):
                raise LookupError(f"invalid writable path {path}")
            c = t.get_config(path)
            if c.is_model_ref():
                raise ValueError(f"model {path} cannot be writable, only tags of it")
            t.add_writable_config_json5(config)
    
    def all_writable_tags(self) -> dict[str, tuple[list[ResponseConfig], TagWriteHandler | None]]:
        d = {}
        for t in self.tags.values():
            d.update(t.write_config)
        return d
    
    # maps a group to the paths that are in it
    def all_groups(self) -> dict[str, list[str]]:
        d = defaultdict(list)
        for t in self.tags.values():
            for path, group_path in t.group_config.items():
                d[group_path].append(path)
        return d
    
    def get_group_members(self, group_path: str) -> list[str]:
        groups = self.all_groups()
        return groups.get(group_path, [])
    
    def get_group_member_configs(self, group_path: str) -> dict[str, DataItemConfig]:
        paths = self.get_group_members(group_path)
        print(group_path, paths)
        configs = {}
        for path in paths:
            configs[path] = self.get_config(path)
        return configs
    
    def get_groups(self, paths: list[str]) -> list[str]:
        res = set()
        for path in paths:
            t = self.get_tag(path)
            if path in t.group_config:
                res.add(t.group_config[path])
        return list(res)
    
    def get_group(self, path: str) -> str | None:
        t = self.get_tag(path)
        if path in t.group_config:
            return t.group_config[path]
        return None
    
    def is_valid_path(self, path: str) -> bool:
        for t in self.tags.values():
            if t.is_valid_path(path):
                return True
        return False
    
    def is_valid_group_path(self, path: str) -> bool:
        print(self.all_groups())
        return path in self.all_groups().keys()

    def add_tag(self, tag: Tag):
        self.tags[tag.path] = tag
    
    def tag_list(self,):
        return self.tags.values()
    
    def add_write_handler(self, path: str, handler: TagWriteHandler):
        if path not in self.all_writable_tags():
            raise LookupError(f"path {path} not writable")
        t = self.get_tag(path)
        t.add_write_handler(path, handler)
    
    def get_tag(self, path: str) -> Tag:
        if path in self.tags:
            return self.tags[path]
        return [t for t in self.tags.values() if t.is_valid_path(path)][0]

    def get_config(self, path: str) -> DataItemConfig:
        return self.get_tag(path).get_config(path)

    def __setitem__(self, path: str, tag: Tag):
        self.tags[path] = tag
    
    def __getitem__(self, path: str):
        return self.tags[path]
    
    def __iter__(self):
        yield from self.tags