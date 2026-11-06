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
# Proposed addition before existing verify_format.py's final result print.
# Differential bindings for the existing admission/geometry responsibility.
lib.admission_need.argtypes=[ctypes.POINTER(ctypes.c_ulonglong),ctypes.POINTER(ctypes.c_uint),ctypes.c_int,ctypes.POINTER(ctypes.c_ulonglong)]
lib.exact_geometry.argtypes=[ctypes.POINTER(ctypes.c_ulonglong),ctypes.POINTER(ctypes.c_uint)]
wide_names=['used','free','total','protected','token','high_token']
small_names=['rows','rgbs','count','high_id','generation','sequence','namespace_files','config_bytes','record_bytes']
def admission_actual(values):
    wide=(ctypes.c_ulonglong*6)(*(values[k] for k in wide_names))
    small=(ctypes.c_uint*9)(*(values[k] for k in small_names))
    need=ctypes.c_ulonglong()
    ok=bool(lib.admission_need(wide,small,values['with_rgb'],ctypes.byref(need)))
    return ok,need.value
base_admission=dict(used=0,free=524288,total=524288,protected=0,token=100,high_token=0,
                   rows=1,rgbs=0,count=0,high_id=0,generation=7,sequence=0,
                   namespace_files=4,config_bytes=120,record_bytes=750,with_rgb=False)
admission_cases=[dict(base_admission)]
for name,values in {
 'rows':[0,1,29,30,31,2**32-1], 'rgbs':[0,1,29,30,31,2**32-1],
 'count':[0,1,63,64,65,2**32-1], 'high_id':[0,1,2**32-2,2**32-1],
 'generation':[0,1,2**32-2,2**32-1], 'sequence':[0,1,2**32-2,2**32-1],
 'token':[0,1,99,100,2**64-1], 'high_token':[0,99,100,101,2**64-1],
 'namespace_files':[0,1,16,17,255,256,257,2**32-1],
 'config_bytes':[0,1,255,256,257,4063,4064,4065,8191,8192,2**32-1],
 'record_bytes':[0,128,129,255,256,257,3468,3469,3470,2**32-1],
 'protected':[0,4096,524288,2**64-1],
}.items():
    for value in values:
        for with_rgb in [False,True]:
            admission_cases.append(dict(base_admission,**{name:value,'with_rgb':with_rgb}))
# All aligned free extents, plus exact protected-space threshold boundaries.
for used in range(0,524289,4096):
    admission_cases.append(dict(base_admission,used=used,free=524288-used))
_,base_need=model.admission(**base_admission)
for protected in [524288-base_need-1,524288-base_need,524288-base_need+1]:
    admission_cases.append(dict(base_admission,protected=protected))
counts['admission_arithmetic']=0
for values in admission_cases:
    try: expected=model.admission(**values)
    except ValueError: expected=None
    actual=admission_actual(values)
    if expected is None: assert not actual[0],values
    else: assert actual==expected,(values,actual,expected)
    counts['admission_arithmetic']+=1
# Geometry is a separate frozen predicate; arithmetic never grants source or
# namespace authority. Mutate each pinned component independently.
geometry=[524288,0,524288,4096,256,256,128,256,31]
def geometry_actual(v):
    return bool(lib.exact_geometry((ctypes.c_ulonglong*3)(*v[:3]),(ctypes.c_uint*6)(*v[3:])))
assert geometry_actual(geometry)
counts['exact_geometry']=1
for used in range(0,524289,4096):
    values=list(geometry);values[1:3]=[used,524288-used]
    assert geometry_actual(values);counts['exact_geometry']+=1
for index,original in enumerate(geometry):
    for changed in {0,1,original-1 if original else 1,original+1,(2**64-1 if index<3 else 2**32-1)}-{original}:
        values=list(geometry);values[index]=changed
        assert not geometry_actual(values),(index,changed)
        counts['exact_geometry']+=1
for n in [0,2**64-1,2**64-256,2**63,2**63-1]:
    charged=ctypes.c_ulonglong()
    try: expected=model.file_charge(n)
    except ValueError: expected=None
    actual=bool(lib.charge(n,ctypes.byref(charged)))
    assert actual==(expected is not None),(n,actual,expected)
    if actual: assert charged.value==expected
    counts['file_charge']+=1

print(json.dumps({'result':'PASS','counts':counts},sort_keys=True))
