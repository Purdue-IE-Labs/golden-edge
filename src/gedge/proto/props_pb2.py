# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: props.proto
# Protobuf Python Version: 6.30.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    30,
    2,
    '',
    'props.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import type_pb2 as type__pb2
from . import data_model_session_pb2 as data__model__session__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0bprops.proto\x1a\ntype.proto\x1a\x18\x64\x61ta_model_session.proto\"^\n\x05Props\x12 \n\x05props\x18\x01 \x03(\x0b\x32\x11.Props.PropsEntry\x1a\x33\n\nPropsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x14\n\x05value\x18\x02 \x01(\x0b\x32\x05.Prop:\x02\x38\x01\"7\n\x04Prop\x12\x13\n\x04type\x18\x01 \x01(\x0b\x32\x05.Type\x12\x1a\n\x05value\x18\x02 \x01(\x0b\x32\x0b.DataObjectb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'props_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_PROPS_PROPSENTRY']._loaded_options = None
  _globals['_PROPS_PROPSENTRY']._serialized_options = b'8\001'
  _globals['_PROPS']._serialized_start=53
  _globals['_PROPS']._serialized_end=147
  _globals['_PROPS_PROPSENTRY']._serialized_start=96
  _globals['_PROPS_PROPSENTRY']._serialized_end=147
  _globals['_PROP']._serialized_start=149
  _globals['_PROP']._serialized_end=204
# @@protoc_insertion_point(module_scope)
