#!/usr/bin/env python3
"""Read immutable expected bytes; write only temporary draft-side build products."""
import ctypes,json,os,struct,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CORPUS=Path(os.environ['GLYPH_PACKAGE_CORPUS'])
sys.dont_write_bytecode=True
sys.path.insert(0,str(CORPUS/'proof'))
import glyph_package_storage as model
lib=ctypes.CDLL(os.environ['GLYPH_PACKAGE_FORMAT_LIB'])
lib.charge.argtypes=[ctypes.c_ulonglong,ctypes.POINTER(ctypes.c_ulonglong)]
lib.make_record.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t]+[ctypes.c_uint]*6+[ctypes.c_ulonglong,ctypes.c_void_p,ctypes.c_void_p]
vectors=json.loads((CORPUS/'storage-vectors.json').read_text())
counts={'layout':0,'retained_root':0,'intent_mutation':0,'resealed_root_mutation':0,'record_encode':0,'file_charge':0}
for v in vectors['layouts']:
    b=bytes.fromhex(v['hex'])
    assert getattr(lib,v['kind']+'_valid')(b,len(b))==1,v['name']
    counts['layout']+=1
    if v['kind']=='root':
        # Exercise the vocabulary and reserved fields with matching outer CRC.
        for offset in range(4416):
            changed=bytearray(b);changed[offset]^=1
            struct.pack_into('<I',changed,4416,zlib.crc32(changed[:4416]))
            try:model.decode_root(changed);expected=True
            except ValueError:expected=False
            assert bool(lib.root_valid(bytes(changed)))==expected,(v['name'],offset)
            counts['resealed_root_mutation']+=1
        intent=b[3904:4416]
        for offset in range(512):
            changed=bytearray(intent);changed[offset]^=1
            try:model.decode_intent(changed);expected=True
            except ValueError:expected=False
            assert bool(lib.intent_valid(bytes(changed)))==expected,(v['name'],offset)
            counts['intent_mutation']+=1
    if v['kind']=='record':
        parsed=model.decode_record(b);header=ctypes.create_string_buffer(128)
        assert lib.make_record(header,parsed['body'],len(parsed['body']),parsed['incarnation'],parsed['id'],parsed['row'],parsed['rgb'],parsed['publication_generation'],parsed['publication_sequence'],parsed['token'],parsed['digest'],parsed['baseline_config_sha'])
        assert header.raw==b[:128],v['name'];counts['record_encode']+=1
for v in vectors['cases']:
    for path,h in v['disk'].items():
        b=bytes.fromhex(h)
        if len(b)==4420 and b[:6]==b'PDS2\x03\x00':
            try:model.decode_root(b);expected=True
            except ValueError:expected=False
            assert bool(lib.root_valid(b))==expected,(v['name'],path)
            counts['retained_root']+=1
for n in range(1,524289):
    charged=ctypes.c_ulonglong()
    assert lib.charge(n,ctypes.byref(charged)) and charged.value==model.file_charge(n),n
    counts['file_charge']+=1
print(json.dumps({'result':'PASS','counts':counts},sort_keys=True))
