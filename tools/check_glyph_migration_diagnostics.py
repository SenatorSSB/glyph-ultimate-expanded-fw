#!/usr/bin/env python3
'''Differential diagnostic proof using exact baseline and candidate sources.

No physical bytes are inferred. Full namespace cases use source-native validators.
Direct Migration cases cover exits masked by earlier namespace admission predicates.
'''
import argparse,copy,ctypes,hashlib,json,os,re,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--senscope',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
p.add_argument('--nor-baseline',type=Path);p.add_argument('--nor-candidate',type=Path)
a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
corpus=a.senscope/'contracts/glyph-package-v1'
os.environ.update(GLYPH_PACKAGE_CORPUS=str(corpus),GLYPH_PACKAGE_RESEARCH=str(a.senscope/'tools/research'),PYTHONDONTWRITEBYTECODE='1')
# The same adapter drives both independently compiled snapshots. Test-only access
# exposes the exact private Migration function, never a second implementation.
def build(repo,label):
 d=a.out/label;d.mkdir();source=(repo/'src/core/PackageNamespaceClassifier.cpp').read_text().replace('class Classifier {','class Classifier { public:')
 (d/'classifier.cpp').write_text(source)
 ffi=(repo/'tools/fixtures/glyph_package_v1/classifier_ffi.cpp').read_text()
 ffi=ffi.replace('#include "core/PackageNamespaceClassifier.hpp"','#include "classifier.cpp"')
 ffi=ffi.replace('extern "C" const char* classify', 'static p::Classification last;\nextern "C" const char* classify')
 ffi=ffi.replace('out[0]=int(result.logical);','last=result;out[0]=int(result.logical);')
 ffi+='''
extern "C" void facts(uint64_t*out){out[0]=int(last.logical);out[1]=int(last.floor);out[2]=last.write_fenced;out[3]=last.incarnation;out[4]=last.generation;out[5]=last.package_sequence;out[6]=last.high_token;}
extern "C" const char* migration(Callbacks*c,const uint8_t*prefix,p::ConfigFacts*config,int*out){
 static p::ClassificationWorkspace w;static unsigned char a[3908],b[3908],ctrl[3924],intent[512],record[4128];
 w={};std::memcpy(a,prefix,3908);p::RootFacts root{};root.prefix=a;root.format=2;
 Reader reader(*c);p::ClassifierOwners owners{w,a,b,ctrl,intent,record};p::Classifier classifier(reader,owners);out[0]=classifier.Migration(root,*config);
 return reader.ObservationFailed()?"checked I/O uncertainty":classifier.why;
}
'''
 (d/'ffi.cpp').write_text(ffi)
 lib=d/'classifier.dylib';cmd=['c++','-std=c++17','-O1','-Wall','-Wextra','-Werror','-dynamiclib','-I',str(repo/'include'),str(d/'ffi.cpp'),str(repo/'src/core/PackageStorageFormat.cpp'),'-o',str(lib)]
 log=subprocess.run(cmd,capture_output=True,text=True);(d/'build.log').write_text(log.stdout+log.stderr);assert log.returncode==0,log.stderr
 return lib
libs=[build(a.baseline,'baseline'),build(a.candidate,'candidate')]
# Reuse the frozen adapter definitions without executing its standalone campaign.
adapter=(a.baseline/'tools/fixtures/glyph_package_v1/verify_classifier.py').read_text().split('\ntry:\n vectors=')[0]
adapter=adapter.replace('def run_case(disk,mounted=True,read_fail_at=None):','def run_case(disk,mounted=True,read_fail_at=None,direct=False,fault=None):\n events=[]\n counters={}\n def event(kind,*args):\n  events.append((kind,*args));counters[kind]=counters.get(kind,0)+1\n  return fault==(kind,counters[kind])')
# All callback observations are traced; only original storage callbacks are faulted.
injections={'mount':"  event('mount')",'obj':"  if event('object',i):return 0",'extent':"  if event('extent',path.decode()):return 2",'read':"  if event('read',path.decode(),offset,n):return 0",'config':"  event('config',path.decode(),maximum)",'row':"  event('row',path.decode(),index)",'rgb':"  event('rgb',path.decode(),index)",'native':"  event('native',path.decode(),index,n)",'legacy':"  event('legacy',n)",'append':"  event('append',base.decode(),current.decode())"}
adapter=adapter.replace(' def mount():return mounted',' def mount():\n  return mounted').replace(' def legacy(ptr,n):return',' def legacy(ptr,n):\n  return')
for name,body in injections.items():
 adapter,count=re.subn(r'( def '+name+r'\([^\n]*\):\n)',lambda m:m[1]+body+'\n',adapter)
 assert count==1,('untraced callback',name,count)
adapter=adapter.replace("callbacks=Callbacks(mount,obj,extent,read,config,row,rgb,native,legacy,append);out=(ctypes.c_int*3)();diagnostic=lib.classify(ctypes.byref(callbacks),out).decode()",'''callbacks=Callbacks(mount,obj,extent,read,config,row,rgb,native,legacy,append);out=(ctypes.c_int*3)()
 if direct:
  cfg=Facts();assert config(b'/config-v2.bin',8191,ctypes.pointer(cfg));events.clear();counters.clear()
  prefix=(ctypes.c_ubyte*3908).from_buffer_copy(disk['/ultimate-v2-0.bin'])
  diagnostic=lib.migration(ctypes.byref(callbacks),prefix,ctypes.byref(cfg),out).decode()
  return bool(out[0]),diagnostic,events
 diagnostic=lib.classify(ctypes.byref(callbacks),out).decode()''')
adapter=adapter.replace('return actual,diagnostic','facts=(ctypes.c_uint64*7)();lib.facts(facts);return tuple(facts),diagnostic,events')
namespaces=[]
for library in libs:
 os.environ['GLYPH_PACKAGE_CLASSIFIER_LIB']=str(library);ns={'__file__':str(a.baseline/'tools/fixtures/glyph_package_v1/verify_classifier.py')};exec(compile(adapter,'retained_adapter','exec'),ns)
 ns['lib'].migration.argtypes=[ctypes.POINTER(ns['Callbacks']),ctypes.POINTER(ctypes.c_ubyte),ctypes.POINTER(ns['Facts']),ctypes.POINTER(ctypes.c_int)];ns['lib'].migration.restype=ctypes.c_char_p;ns['lib'].facts.argtypes=[ctypes.POINTER(ctypes.c_uint64)];namespaces.append(ns)
m=namespaces[0]['model'];sys.path[:0]=[str(corpus/'proof'),str(corpus/'wire')];import glyph_package_fixtures as f
cases=[]
def add(name,disk,reason=None):cases.append((name,disk,reason))
def roots(d,edit,receipt=True):
 r=bytearray(d['/ultimate-v2-0.bin']);edit(r)
 if receipt:r[200:232]=m.migration_receipt(r)
 m.put32(r,3904,m.crc(r[:3904]));d['/ultimate-v2-0.bin']=d['/ultimate-v2-1.bin']=bytes(r);d['/ultimate-v2.ctrl']=f.source_control(bytes(r))
 if receipt:
  _,tree=m.config_body(d['/config-v2.bin']);f.put(tree,209,r[200:232].hex());d['/config-v2.bin']=f.config_file(tree)
 return d
def editroot(name,offset,value,reason,version=2,receipt=True):
 d=f.completed_migration(version);roots(d,lambda r:m.put32(r,offset,value),receipt);add(name,d,reason)
add('kind2-positive',f.completed_migration(2));add('kind3-positive',f.completed_migration(3))
d=f.completed_migration(3);del d['/ultimate-dir-0.bin'];del d['/ultimate-dir-1.bin'];add('kind3-sources-absent-permitted',d)
d=f.completed_migration();roots(d,lambda r:m.put32(r,20,0),False);add('state-zero',d)
editroot('state-unsupported',20,3,'migration: state',receipt=False)
editroot('state-pending',20,1,'migration: state',receipt=False)
editroot('receipt-formula',200,123,'migration: receipt formula',receipt=False)
d=f.completed_migration();_,tree=m.config_body(d['/config-v2.bin']);f.put(tree,209,'77'*32);d['/config-v2.bin']=f.config_file(tree);add('config-receipt',d,'migration: Config receipt')
d=f.completed_migration();del d['/ultimate-migration.src'];add('source-absent',d,'migration: source object unavailable')
d=f.completed_migration();d['/ultimate-migration.src']+=b'x';add('source-hash',d,'migration: source hash')
# Mutate historical roots, updating their CRC and the compact source hash when
# needed so later predicates are reached without relaxing the verifier.
def oldcase(name,edit,reason,mirror=True,hash_source=True):
 d=f.completed_migration(3);b=bytearray(d['/ultimate-dir-0.bin']);edit(b);m.put32(b,2616,m.crc(b[:2616]));d['/ultimate-dir-0.bin']=bytes(b)
 if mirror:d['/ultimate-dir-1.bin']=bytes(b)
 if hash_source:roots(d,lambda r:r.__setitem__(slice(88,120),m.sha(b)))
 add(name,d,reason)
oldcase('legacy-not-completed',lambda b:m.put32(b,24,1),'migration: legacy root')
oldcase('legacy-incarnation',lambda b:m.put32(b,12,99),'migration: legacy root incarnation')
oldcase('legacy-generation',lambda b:m.put32(b,8,99),'migration: legacy root generation')
oldcase('legacy-slots-gap',lambda b:m.put32(b,8,3),'migration: legacy root slots',mirror=False,hash_source=False)
oldcase('legacy-slots-conflict',lambda b:m.put32(b,16,2),'migration: legacy root slots',mirror=False,hash_source=False)
oldcase('legacy-hash',lambda b:m.put32(b,16,2),'migration: legacy root hash',hash_source=False)
oldcase('legacy-ids',lambda b:(m.put32(b,16,2),m.put32(b,2608,2)),'migration: legacy migrated entries')
editroot('legacy-revision',128,2,'migration: legacy migrated entries',3)
editroot('legacy-count',84,2,'migration: legacy migrated count',3)
editroot('legacy-count-overflow',84,0,'migration: legacy migrated entries',3)
# Each migrated-record false exit is independent of the source blob proof.
path='/ultimate-00000001-00000001.bin'
d=f.completed_migration();del d[path];add('revision-absent',d,'migration: revision unavailable')
for name,offset,value,reason in [('format-magic',0,0,'revision format'),('format-version',4,0,'revision format'),('format-kind',4,131073,'revision format'),('identity-inc',8,99,'revision identity'),('identity-id',12,2,'revision identity'),('identity-rev',16,2,'revision identity'),('extent',20,1,'revision extent'),('header-crc',24,0,'revision header CRC'),('payload-crc',28,0,'revision payload CRC')]:
 d=f.completed_migration();b=bytearray(d[path]);m.put32(b,offset,value);d[path]=bytes(b);add(name,d,'migration: '+reason)
d=f.completed_migration();d[path]=d[path][:32];add('revision-short',d,'migration: revision format')
d=f.completed_migration();d[path]+=bytes(5000);add('revision-oversize',d,'migration: revision unavailable')
d=f.completed_migration();b=bytearray(d[path]);b[32:]=bytes(len(b)-32);m.put32(b,28,m.crc(b[32:]));m.put32(b,24,m.crc(b[:24]));d[path]=bytes(b);add('profile-invalid',d,'migration: profile validation')
d=f.completed_migration();roots(d,lambda r:r.__setitem__(slice(136,168),bytes([1])*32));add('payload-hash',d,'migration: payload hash')
records=[]
def compare(name,disk,reason=None,direct=False,fault=None):
 before=copy.deepcopy(disk);results=[n['run_case'](disk,direct=direct,fault=fault) for n in namespaces];x,y=results
 assert disk==before,'namespace mutated'
 assert x[0]==y[0],(name,'material',x,y)
 assert x[2]==y[2],(name,'read order',x,y)
 if reason is not None and direct and fault is None:assert not x[0] and y[1]==reason,(name,x,y)
 if x[1]!=y[1]:assert y[1].startswith('migration: '),(name,x,y)
 if fault and y[1]=='checked I/O uncertainty':assert x[1]==y[1]
 records.append(dict(name=name,direct=direct,fault=fault,material=x[0],baseline_reason=x[1],candidate_reason=y[1],trace_sha256=hashlib.sha256(json.dumps(x[2]).encode()).hexdigest(),unchanged_namespace=True))
 return y
for name,disk,reason in cases:
 compare(name,disk,reason,direct=True);result=compare(name,disk,reason)
 if reason:assert result[0][:3]==(0,0,1),(name,result)
 # Every original direct-read/extent/object seam is faulted once, including
 # rereads, and compared against the baseline without injecting any new probe.
 for direct in (False,True):
  result=namespaces[0]['run_case'](disk,direct=direct);counts={}
  for event in result[2]:
   kind=event[0];counts[kind]=counts.get(kind,0)+1
   if kind in ('read','extent','object'):
    fault=(kind,counts[kind]);r=compare(name,disk,direct=direct,fault=fault)
    if not direct:assert r[0][:3]==(0,0,1),(name,fault,r)
# Existing immutable package/migration corpus, including committed/partial states.
vectors=json.loads((corpus/'storage-vectors.json').read_text())
for v in vectors['cases']:compare('corpus/'+v['name'],{p:bytes.fromhex(h) for p,h in v['disk'].items()})
nor_records=[]
if a.nor_baseline or a.nor_candidate:
 assert a.nor_baseline and a.nor_candidate
 import struct
 sys.path.insert(0,str(a.candidate/'tools/fixtures/glyph_package_v1/transaction'));from run import dump_namespace
 def process(cmd):
  c=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
  assert c.returncode==0,(cmd,c.stdout,c.stderr)
 for name,disk,reason in cases:
  work=a.out/'nor'/name;work.mkdir(parents=True);dump_namespace(disk,work/'seed.namespace');process([a.nor_baseline,'seed',work/'seed.namespace',work/'seed.nor'])
  seed=(work/'seed.nor').read_bytes();cuts=[18446744073709551615]
  if reason is None:cuts.extend([0,1,10])
  for cut in cuts:
   result=[]
   for label,binary in [('baseline',a.nor_baseline),('candidate',a.nor_candidate)]:
    out=work/(label+'-'+str(cut));out.mkdir();process([binary,'migration-diagnostic',work/'seed.nor',cut,out])
    facts=json.loads((out/'classification.json').read_text());stats=json.loads((out/'summary.json').read_text())
    assert stats['programs']==stats['erases']==0 and stats['unchanged']
    assert (out/'after.nor').read_bytes()==seed
    assert (out/'namespace.bin').read_bytes()==(work/'seed.namespace').read_bytes()
    result.append(facts)
   x,y=result
   if cut==18446744073709551615 and reason is None:cuts.extend(sorted({x['seams']-1,x['seams']//2,2*x['seams']//3}-{0,1,10}))
   assert {k:v for k,v in x.items() if k!='diagnostic'}=={k:v for k,v in y.items() if k!='diagnostic'},(name,cut,x,y)
   if x['diagnostic']!=y['diagnostic']:assert y['diagnostic'].startswith('migration: ')
   if cut!=18446744073709551615:assert y['observation_failed'] and y['diagnostic']=='checked I/O uncertainty',(name,cut,y)
   nor_records.append(dict(name=name,cut=cut,baseline=x,candidate=y,raw_nor_identical=True,filesystem_identical=True,programs=0,erases=0))
 (a.out/'nor-results.json').write_text(json.dumps(nor_records,indent=2)+'\n')
(a.out/'results.json').write_text(json.dumps(records,indent=2)+'\n')
summary=dict(result='PASS',focused_namespaces=len(cases),corpus_cases=len(vectors['cases']),comparisons=len(records),material_fields=['logical','floor','write_fenced','incarnation','generation','package_sequence','high_token'],equal_read_traces=True,unchanged_namespace=True,nor_comparisons=len(nor_records),hardware_operations=0,limits='Direct Migration covers predicates masked by earlier source admission; NOR proof is a separate production-adapter gate.')
(a.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
