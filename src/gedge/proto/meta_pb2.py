# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: meta.proto
# Protobuf Python Version: 5.28.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    0,
    '',
    'meta.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import tag_data_pb2 as tag__data__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nmeta.proto\x1a\x0etag_data.proto\"\xe3\x01\n\x04Meta\x12\x17\n\x04tags\x18\x04 \x03(\x0b\x32\t.Meta.Tag\x12\x1d\n\x07methods\x18\x05 \x03(\x0b\x32\x0c.Meta.Method\x1a\x08\n\x06Method\x1a\x98\x01\n\x03Tag\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x17\n\x04type\x18\x02 \x01(\x0e\x32\t.DataType\x12-\n\nproperties\x18\x03 \x03(\x0b\x32\x19.Meta.Tag.PropertiesEntry\x1a;\n\x0fPropertiesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x17\n\x05value\x18\x02 \x01(\x0b\x32\x08.TagData:\x02\x38\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'meta_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_META_TAG_PROPERTIESENTRY']._loaded_options = None
  _globals['_META_TAG_PROPERTIESENTRY']._serialized_options = b'8\001'
  _globals['_META']._serialized_start=31
  _globals['_META']._serialized_end=258
  _globals['_META_METHOD']._serialized_start=95
  _globals['_META_METHOD']._serialized_end=103
  _globals['_META_TAG']._serialized_start=106
  _globals['_META_TAG']._serialized_end=258
  _globals['_META_TAG_PROPERTIESENTRY']._serialized_start=199
  _globals['_META_TAG_PROPERTIESENTRY']._serialized_end=258
# @@protoc_insertion_point(module_scope)
