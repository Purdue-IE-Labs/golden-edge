# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: params_config.proto
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
    'params_config.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import data_object_config_pb2 as data__object__config__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13params_config.proto\x1a\x18\x64\x61ta_object_config.proto\"{\n\x0cParamsConfig\x12)\n\x06params\x18\x01 \x03(\x0b\x32\x19.ParamsConfig.ParamsEntry\x1a@\n\x0bParamsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12 \n\x05value\x18\x02 \x01(\x0b\x32\x11.DataObjectConfig:\x02\x38\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'params_config_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_PARAMSCONFIG_PARAMSENTRY']._loaded_options = None
  _globals['_PARAMSCONFIG_PARAMSENTRY']._serialized_options = b'8\001'
  _globals['_PARAMSCONFIG']._serialized_start=49
  _globals['_PARAMSCONFIG']._serialized_end=172
  _globals['_PARAMSCONFIG_PARAMSENTRY']._serialized_start=108
  _globals['_PARAMSCONFIG_PARAMSENTRY']._serialized_end=172
# @@protoc_insertion_point(module_scope)
