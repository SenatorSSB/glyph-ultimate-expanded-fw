#!/usr/bin/env python3
'''Differential diagnostic proof using exact baseline and candidate sources.

No physical bytes are inferred. Full namespace cases use source-native validators.
Direct Migration cases cover exits masked by earlier namespace admission predicates.
'''
import argparse,copy,ctypes,hashlib,json,os,re,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--senscope',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
p.add_argument('--witness',type=Path,required=True);p.add_argument('--nor-baseline',type=Path);p.add_argument('--nor-candidate',type=Path)
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

# Exact source-native publication roots. Host payloads below independently pass
# production legacy validators; replay does not claim historical payload validity.
old=(a.witness/'completed-slot0.bin').read_bytes();new=(a.witness/'completed-slot1.bin').read_bytes()
assert m.u32(old,24)==1 and m.u32(new,24)==2 and m.u32(old,8)+1==m.u32(new,8)
def bind(d,source):
 roots(d,lambda r:r.__setitem__(slice(88,120),m.sha(source)))
 return d
def pair():
 d=f.completed_migration(3);d['/ultimate-dir-0.bin']=old;d['/ultimate-dir-1.bin']=new
 return bind(d,new)
def edit(d,slot,offset,value,crc=True):
 p='/ultimate-dir-%d.bin'%slot;b=bytearray(d[p]);m.put32(b,offset,value)
 if crc:m.put32(b,2616,m.crc(b[:2616]))
 d[p]=bytes(b);return d
# (name, namespace, repaired acceptance, behavior change allowed)
cases=[]
def case(name,d,ok=False,changed=False):cases.append((name,d,ok,changed))
case('writer-state1-state2',pair(),True,True)
d=pair();del d['/ultimate-dir-0.bin'];case('only-selected-completed',d,True)
d=pair();d['/ultimate-dir-0.bin']=(a.witness/'post-update-slot0.bin').read_bytes();d['/ultimate-dir-1.bin']=(a.witness/'post-update-slot1.bin').read_bytes();bind(d,d['/ultimate-dir-0.bin']);case('both-completed-source-native',d,True)
case('older-state0-unsupported',edit(pair(),0,24,0))
for state in [0,1]:
 d=edit(pair(),1,24,state);bind(d,d['/ultimate-dir-1.bin']);case('source-state'+str(state),d)
d=pair();bind(d,old);case('source-hash-older',d)
case('generation-gap',edit(pair(),0,8,4))
case('equal-generation-conflict',edit(pair(),0,8,2))
case('incarnation-mismatch',edit(pair(),0,12,99))
d=pair();bind(d,old);case('completed-marker-wrong-hash',d)
for slot in [0,1]:
 case('crc-invalid-'+str(slot),edit(pair(),slot,52,7,False))
 d=pair();d['/ultimate-dir-%d.bin'%slot]=d['/ultimate-dir-%d.bin'%slot][:-1];case('malformed-'+str(slot),d)
for offset in [120,128]:
 d=pair();roots(d,lambda r:m.put32(r,offset,2));case('missing-id-revision-'+str(offset),d)
case('older-future-state',edit(pair(),0,24,3))
case('state1-nontransition-rank',edit(pair(),0,48,7))
case('state1-nontransition-digest',edit(pair(),0,20,7))
d=pair();d['/ultimate-dir-0.bin'],d['/ultimate-dir-1.bin']=d['/ultimate-dir-1.bin'],d['/ultimate-dir-0.bin'];case('wrong-writer-parity',d)
# Many generations/parities retain exactly the two-byte-layout transition family.
for generation in range(2,20):
 d=pair();a0=bytearray(old);a1=bytearray(new)
 for b,g in [(a0,generation-1),(a1,generation)]:m.put32(b,8,g);m.put32(b,2616,m.crc(b[:2616]))
 d['/ultimate-dir-%d.bin'%(generation&1)]=bytes(a0);d['/ultimate-dir-%d.bin'%((generation+1)&1)]=bytes(a1)
 # The v2 generation bounds both source generations.
 roots(d,lambda r:m.put32(r,8,generation+1));bind(d,a1);case('reachable-generation-'+str(generation),d,True,True)
records=[]
def compare(name,d,ok,changed):
 before=copy.deepcopy(d);x,y=[n['run_case'](d) for n in namespaces];assert d==before
 assert (y[0][:3]==(1,2,0))==ok,(name,x,y)
 if changed:
  assert x[0][:3]==(0,0,1) and y[0][:3]==(1,2,0),(name,x,y)
 else:assert x[0]==y[0],(name,x,y)
 records.append(dict(name=name,baseline=x[:2],candidate=y[:2],changed=changed,unchanged_namespace=True))
 return y
for name,d,ok,changed in cases:
 y=compare(name,d,ok,changed)
 # Fault every candidate object/extent/read, including newly required rereads.
 counters={}
 for event in y[2]:
  kind=event[0];counters[kind]=counters.get(kind,0)+1
  if kind in ('object','extent','read'):
   r=namespaces[1]['run_case'](d,fault=(kind,counters[kind]));assert r[0][:3]==(0,0,1),(name,event,r)
   assert r[1]=='checked I/O uncertainty',(name,event,r)
   records.append(dict(name=name,fault=(kind,counters[kind]),fenced=True))
vectors=json.loads((corpus/'storage-vectors.json').read_text())
for v in vectors['cases']:
 d={p:bytes.fromhex(h) for p,h in v['disk'].items()};x,y=[n['run_case'](d) for n in namespaces];assert x[0]==y[0],(v['name'],x,y)
 records.append(dict(name='corpus/'+v['name'],unchanged=True))
# Preserve complete exact fixture bytes as well as the executable witness.
(a.out/'fixtures.json').write_text(json.dumps([{ 'name':n,'disk':{p:b.hex() for p,b in d.items()},'accepted':ok,'changed':ch} for n,d,ok,ch in cases],indent=2)+'\n')
(a.out/'results.json').write_text(json.dumps(records,indent=2)+'\n')
summary=dict(result='PASS',namespaces=len(cases),corpus_cases=len(vectors['cases']),checks=len(records),newly_accepted_family='exact older1/newer2 completion transition only',hardware_operations=0)
(a.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
