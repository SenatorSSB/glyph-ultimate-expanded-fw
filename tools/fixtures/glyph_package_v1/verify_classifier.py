#!/usr/bin/env python3
import ctypes,json,sys,functools
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
CORPUS=Path(__import__('os').environ['GLYPH_PACKAGE_CORPUS'])
sys.path[:0]=[str(CORPUS/'proof'),str(CORPUS/'wire'),__import__('os').environ['GLYPH_PACKAGE_RESEARCH']]
import glyph_package_storage as model
from source_native_oracle import SourceNativeOracle
class Facts(ctypes.Structure):
 _fields_=[(n,ctypes.c_uint32) for n in ('body_bytes','crc','rows','rgbs','store_format','incarnation','root_format','managed_format','sequence','embedded_profiles','reference_id','reference_generation','reference_row')]+[('reference_token',ctypes.c_uint64)]+[(n,ctypes.c_ubyte*32) for n in ('sha','reference_digest','migration_receipt')]+[(n,ctypes.c_bool) for n in ('any_row_marker','newer_row_marker','source_valid','reference_digest_valid')]
class Row(ctypes.Structure):
 _fields_=[(n,ctypes.c_uint32) for n in ('mode','id','engine','marker','rgb','legacy','custom','keyboard')]+[('sha',ctypes.c_ubyte*32)]
P=ctypes.POINTER
MOUNT=ctypes.CFUNCTYPE(ctypes.c_int)
OBJ=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_size_t,P(ctypes.c_char),P(ctypes.c_size_t),P(ctypes.c_int))
EXT=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_char_p,P(ctypes.c_size_t))
READ=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_char_p,ctypes.c_size_t,P(ctypes.c_ubyte),ctypes.c_size_t)
CONF=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_char_p,ctypes.c_uint,P(Facts))
ROW=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_char_p,ctypes.c_size_t,P(Row))
RGB=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_char_p,ctypes.c_size_t,P(ctypes.c_ubyte))
NATIVE=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_char_p,ctypes.c_size_t,P(ctypes.c_ubyte),ctypes.c_size_t)
LEGACY=ctypes.CFUNCTYPE(ctypes.c_int,P(ctypes.c_ubyte),ctypes.c_size_t)
APPEND=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_char_p,ctypes.c_char_p)
class Callbacks(ctypes.Structure):
 _fields_=[('mounted',MOUNT),('object',OBJ),('extent',EXT),('read',READ),('config',CONF),('row',ROW),('rgb',RGB),('native',NATIVE),('legacy',LEGACY),('append',APPEND)]
lib=ctypes.CDLL(__import__('os').environ['GLYPH_PACKAGE_CLASSIFIER_LIB']);lib.classify.argtypes=[P(Callbacks),P(ctypes.c_int)];lib.classify.restype=ctypes.c_char_p
assert lib.facts_size()==ctypes.sizeof(Facts),(lib.facts_size(),ctypes.sizeof(Facts))
print('workspace bytes',lib.workspace_size())
oracle=SourceNativeOracle(CORPUS/'wire')
model.CONFIG_VALIDATOR=oracle.check_config;model.NATIVE_VALIDATOR=oracle.check;model.LEGACY_PROFILE_VALIDATOR=oracle.check_profile
logical=['UNRESOLVED','NONE','PROVEN_ABORTED','INCOMPLETE','COMMITTED'];floor=['UNRESOLVED','UNSUPPORTED','NO_MANAGED','SUPPORTED']
def run_case(disk,mounted=True,read_fail_at=None):
 read_calls=0
 names=sorted(disk)
 inventory,encode=model.config_wire()
 @functools.lru_cache(maxsize=None)
 def body(path):return model.config_body(disk[path],65536)
 @functools.lru_cache(maxsize=None)
 def decoded_root(name):
  raw=disk[name][16:] if name.endswith('.ctrl') else disk[name]
  return model.decode_root(raw)
 def setbytes(dest,value):
  if isinstance(value,str):value=bytes.fromhex(value)
  if value==0:value=b''
  if len(value)>len(dest):raise ValueError('extent')
  ctypes.memset(ctypes.addressof(dest),0,len(dest));ctypes.memmove(dest,value,len(value))
 @MOUNT
 def mount():return mounted
 @OBJ
 def obj(i,out,sz,eof):
  if i>=len(names):eof[0]=1;return 1
  ctypes.memmove(out,names[i].encode()+b'\0',len(names[i])+1);sz[0]=len(disk[names[i]]) if disk[names[i]] is not None else 0;eof[0]=0;return 1
 @EXT
 def extent(path,out):
  path=path.decode()
  if path not in disk:return 1
  if disk[path] is None:return 2
  out[0]=len(disk[path]);return 0
 @READ
 def read(path,offset,out,n):
  nonlocal read_calls
  read_calls+=1
  if read_calls==read_fail_at:return 0
  path=path.decode();b=disk.get(path)
  if b is None or offset+n>len(b):return 0
  ctypes.memmove(out,b[offset:offset+n],n);return 1
 @CONF
 def config(path,maximum,out):
  try:
   path=path.decode();b,t=body(path);
   if len(b)>maximum:return 0
   f=out.contents
   f.body_bytes=len(b);f.crc=model.crc(b);f.rows=len(model.repeats(t,1));f.rgbs=len(model.repeats(t,5));f.store_format=model.field(t,202);f.incarnation=model.field(t,203);f.root_format=model.field(t,210);f.managed_format=model.field(t,211);f.sequence=model.field(t,212);f.embedded_profiles=len(model.repeats(t,201));f.reference_id=model.field(t,206);f.reference_generation=model.field(t,207);f.reference_row=model.field(t,208);f.reference_token=model.field(t,204)
   setbytes(f.sha,model.sha(b));setbytes(f.reference_digest,model.field(t,205));setbytes(f.migration_receipt,model.field(t,209));f.any_row_marker=any(model.field(r,206) for r in model.repeats(t,1));f.newer_row_marker=any(model.field(r,206)>1 for r in model.repeats(t,1));f.source_valid=bool(callable(model.CONFIG_VALIDATOR) and model.CONFIG_VALIDATOR(b))
   digest=model.field(t,205,'');f.reference_digest_valid=isinstance(digest,str) and len(digest)==64
   return 1
  except (ValueError,KeyError,IndexError,TypeError):return 0
 @ROW
 def row(path,index,out):
  try:
   b,t=body(path.decode());r=model.repeats(t,1)[index];f=out.contents
   for name,number in [('mode',1),('id',204),('engine',205),('marker',206),('rgb',8),('legacy',203),('custom',6),('keyboard',7)]:setattr(f,name,model.field(r,number))
   setbytes(f.sha,model.sha(encode(r,'GameModeConfig')));return 1
  except (ValueError,KeyError,IndexError):return 0
 @RGB
 def rgb(path,index,out):
  try:
   b,t=body(path.decode());h=model.sha(encode(model.repeats(t,5)[index],'RgbConfig'));ctypes.memmove(out,h,32);return 1
  except (ValueError,KeyError,IndexError):return 0
 @NATIVE
 def native(path,index,record,n):
  try:
   b=ctypes.string_at(record,n);ident=model.u32(b,12);cfg,t=body(path.decode());r=model.repeats(t,1)[index];rgb1=model.field(r,8);rgb=model.repeats(t,5)[rgb1-1] if rgb1 else None
   for name in ['/ultimate-v2-0.bin','/ultimate-v2-1.bin','/ultimate-v2.ctrl']:
    if name not in disk:continue
    raw=disk[name][16:] if name.endswith('.ctrl') else disk[name]
    if len(raw)!=4420:continue
    root=decoded_root(name)
    for e in root['entries']:
     if e['id']==ident:return bool(callable(model.NATIVE_VALIDATOR) and model.NATIVE_VALIDATOR(e,encode(r,'GameModeConfig'),encode(rgb,'RgbConfig') if rgb is not None else b'',b))
   return 0
  except (ValueError,KeyError,IndexError):return 0
 @LEGACY
 def legacy(ptr,n):return bool(callable(model.LEGACY_PROFILE_VALIDATOR) and model.LEGACY_PROFILE_VALIDATOR(ctypes.string_at(ptr,n)))
 @APPEND
 def append(base,current):
  try:
   a,at=body(base.decode());b,bt=body(current.decode());intent=model.decode_control(disk['/ultimate-v2.ctrl'])[1]['intent'];model.validate_append_config(a,b,intent);return 1
  except (ValueError,KeyError,IndexError):return 0
 callbacks=Callbacks(mount,obj,extent,read,config,row,rgb,native,legacy,append);out=(ctypes.c_int*3)();diagnostic=lib.classify(ctypes.byref(callbacks),out).decode()
 actual=(logical[out[0]],bool(out[1]),floor[out[2]])
 if read_fail_at is not None and read_calls>=read_fail_at:assert actual==('UNRESOLVED',True,'UNRESOLVED'),(read_fail_at,read_calls,actual,diagnostic)
 return actual,diagnostic
try:
 vectors=json.loads((CORPUS/'storage-vectors.json').read_text());passed=0;failed=[]
 for v in vectors['cases']:
  disk={p:bytes.fromhex(h) for p,h in v['disk'].items()};actual,diagnostic=run_case(disk)
  if actual!=tuple(v['expected']):failed.append((v['name'],v['expected'],actual,diagnostic))
  else:passed+=1
 print('retained cases',passed,'PASS;',len(failed),'FAIL')
 for row in failed:print(row)
 assert not failed
 committed={p:bytes.fromhex(h) for p,h in next(v for v in vectors['cases'] if v['name']=='second-no-rgb/COMMITTED')['disk'].items()}
 # Late failures after the first successful full namespace pass stay unresolved.
 for cut in range(1,250):
  actual,diagnostic=run_case(committed,read_fail_at=cut)
  assert actual in [('UNRESOLVED',True,'UNRESOLVED'),('COMMITTED',False,'SUPPORTED')],(cut,actual,diagnostic)
 print("late-read failure cuts249 PASS")
 import reachable_states, glyph_package_fixtures
 original_classify=model.classify
 def draft_classify(disk,**observation):
  a,diagnostic=run_case(disk,mounted=observation.get("mounted",True) and observation.get("configuration_ok",True) and observation.get("namespace_ok",True));return dict(logical=a[0],write_fenced=a[1],floor=a[2],diagnostic=diagnostic)
 model.classify=draft_classify
 print("reachable",reachable_states.replay(model,glyph_package_fixtures),"PASS")
 import unittest,test_glyph_package_contract as corpus_tests
 class DraftStorageContract(corpus_tests.StorageContract):
  @classmethod
  def setUpClass(cls):
   cls.native=oracle;cls.base=glyph_package_fixtures.baseline();cls.first,cls.vector=glyph_package_fixtures.package_plan(cls.base,True);cls.second,cls.vector2=glyph_package_fixtures.package_plan(cls.first['COMMITTED'],False,200)
  @classmethod
  def tearDownClass(cls):pass
 print("Running immutable storage contract tests through C++ classifier")
 tests=unittest.defaultTestLoader.loadTestsFromTestCase(DraftStorageContract)
 tested=unittest.TextTestRunner(verbosity=1).run(tests)
 assert tested.wasSuccessful()
 model.classify=original_classify
finally:oracle.close()
