# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: type.proto
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
    'type.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\ntype.proto\"\x1d\n\rDataModelType\x12\x0c\n\x04path\x18\x01 \x01(\t\"Y\n\x04Type\x12\x1e\n\tbase_type\x18\x01 \x01(\x0e\x32\t.BaseTypeH\x00\x12)\n\x0f\x64\x61ta_model_type\x18\x02 \x01(\x0b\x32\x0e.DataModelTypeH\x00\x42\x06\n\x04type*\x98\x01\n\x08\x42\x61seType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x07\n\x03INT\x10\x01\x12\x08\n\x04LONG\x10\x02\x12\t\n\x05\x46LOAT\x10\x03\x12\n\n\x06STRING\x10\x04\x12\x08\n\x04\x42OOL\x10\x05\x12\x0c\n\x08LIST_INT\x10\x06\x12\r\n\tLIST_LONG\x10\x07\x12\x0e\n\nLIST_FLOAT\x10\x08\x12\x0f\n\x0bLIST_STRING\x10\t\x12\r\n\tLIST_BOOL\x10\nb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'type_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_BASETYPE']._serialized_start=137
  _globals['_BASETYPE']._serialized_end=289
  _globals['_DATAMODELTYPE']._serialized_start=14
  _globals['_DATAMODELTYPE']._serialized_end=43
  _globals['_TYPE']._serialized_start=45
  _globals['_TYPE']._serialized_end=134
# @@protoc_insertion_point(module_scope)
