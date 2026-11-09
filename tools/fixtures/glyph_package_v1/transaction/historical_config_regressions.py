"""Exact precompact family acceptance, bounded negatives and untouched NOR proof.

No fixture or observation attests the actual controller filesystem.
"""
import argparse,copy,hashlib,json,os,struct,subprocess,sys,zlib
from pathlib import Path
from run import dump_namespace
from storage_fence_regressions import response

def var(n):
 b=bytearray()
 while n>127:b.append((n&127)|128);n>>=7
 b.append(n);return bytes(b)
def field(n,value):return var(n*8)+var(value)
def msg(n,body):return var(n*8+2)+var(len(body))+body
def wrap(b):return struct.pack('<II',len(b),zlib.crc32(b))+b

def main():
 p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--corpus',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(exist_ok=False,parents=True)
 env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'}
 def run(argv,**kw):
  c=subprocess.run(list(map(str,argv)),env=env,capture_output=True,text=True,timeout=90,**kw)
  assert c.returncode==0,(argv,c.stdout,c.stderr)
  return c
 sys.dont_write_bytecode=True;sys.path[:0]=[str(a.corpus/'proof'),str(a.corpus/'wire'),str(a.corpus.parents[1]/'tools/research')]
 import glyph_package_storage as m
 import glyph_package_fixtures as f
 import config_pb2 as cfg
 from source_native_oracle import SourceNativeOracle
 oracle=SourceNativeOracle(a.corpus/'wire');m.CONFIG_VALIDATOR=oracle.check_config;m.NATIVE_VALIDATOR=oracle.check;m.LEGACY_PROFILE_VALIDATOR=oracle.check_profile
 fixture=Path(__file__).parents[1]/'historical_config'
 historical=(fixture/'minimal.pb').read_bytes();assert hashlib.sha256(historical).hexdigest()=='191856fe3a60529575e2305f839327d6186e909f35b2acfa52b794132b077de2'
 # This exact independently old-descriptor-encoded body is the only supported
 # family. Multiple source-valid structures exercise nested old representation.
 positive=[historical]
 embedded=cfg.Config.FromString(historical);profile=embedded.ultimate_profiles.add(schema_version=1)
 for i in range(28):
  table=profile.tables.add(table_id=i)
  for _ in range(9):table.coordinates.add(x=128,y=128)
 embedded.game_mode_configs[0].ultimate_profile_config=1
 positive.append(embedded.SerializeToString(deterministic=True))
 negative={
  'historically-invalid-empty-rgb-target':historical[:22]+msg(5,msg(1,b''))+historical[22:],
  'historically-invalid-colored-rgb-target':historical[:22]+msg(5,msg(1,field(2,1)))+historical[22:],
  'wrong-wire-type':bytes([historical[0]^1])+historical[1:],
  'duplicate-field':historical+field(6,1),
  'nonminimal-varint':b'\x8a\x00'+historical[1:],
  'explicit-default':historical+field(8,0),
  'unknown-field':historical+field(213,1),
  'compact-marker':historical+field(202,1),
  'package-marker':historical+field(211,1),
  'fixed-length-reference-marker':historical+msg(205,bytes(32)),
  'fixed-length-receipt-marker':historical+msg(209,bytes(32)),
  'truncated-nested':historical[:-1],
  'invalid-nested-reference':msg(1,field(1,3)+field(203,3))+historical[16:],
  'future-row-engine':msg(1,field(1,3)+field(205,1))+historical[16:],
  'future-row-id':msg(1,field(1,3)+field(204,1))+historical[16:],
  'future-native-payload':historical+msg(201,field(1,5)+msg(8,b'x')),
  'bad-embedded-profile':historical+msg(201,field(1,1)),
  'too-many-rows':msg(1,field(1,3))*31+historical[16:],
 }
 # Independent historical descriptor proves these bodies are old writer
 # encodings; the current descriptor is not the historical acceptance oracle.
 repo=Path(__file__).resolve().parents[4];nanopb=repo/'.pio/libdeps/glyph_mk6/Nanopb'
 old_binary=a.out/'old-writer-roundtrip'
 run([os.environ.get('CC','cc'),'-std=c11','-I'+str(fixture),'-I'+str(nanopb),fixture/'roundtrip.c',fixture/'config.pb.c',nanopb/'pb_common.c',nanopb/'pb_decode.c',nanopb/'pb_encode.c','-o',old_binary])
 for body in positive:
  proof=subprocess.run([old_binary],input=body,capture_output=True);assert proof.returncode==0,proof.stderr
 inputs=positive+list(negative.values())
 observed=run([a.binary,'observe-historical'],input=''.join(b.hex()+'\n' for b in inputs));actual=[int(x) for x in observed.stdout.splitlines()]
 assert actual==[0]*len(positive)+[1]*len(negative),(actual,negative)
 faults=run([a.binary,'observe-historical-faults'],input=historical.hex()+'\n');assert faults.stdout.strip()=='0';(a.out/'observer-faults.txt').write_text(faults.stderr)
 base=f.baseline(ultimate=True,backend=True);defaults=a.out/'defaults.pb';defaults.write_bytes(base['/config-v2.bin'][8:]);cases=[]
 def add(name,disk,healthy):cases.append((name,disk,healthy))
 def retained(raw,disk=base):d=copy.deepcopy(disk);d['/config.bin']=raw;return d
 add('old-writer-minimal-healthy-compact',retained(wrap(historical)),True)
 add('old-writer-embedded-profile-healthy-compact',retained(wrap(positive[1])),True)
 for version in [2,3]:add('receipt-migration-'+str(version),retained(wrap(historical),f.completed_migration(version)),True)
 stages,_=f.package_plan(base,True,100)
 add('managed-package-healthy',retained(wrap(historical),stages['COMMITTED']),True)
 bad=bytearray(wrap(historical));bad[-1]^=1;add('body-corruption',retained(bytes(bad)),False)
 bad=bytearray(wrap(historical));bad[4]^=1;add('incorrect-crc',retained(bytes(bad)),False)
 add('truncated-body',retained(wrap(historical)[:-1]),False)
 add('trailing-byte',retained(wrap(historical)+b'x'),False)
 add('short-header',retained(b'bad'),False)
 add('length-mismatch',retained(struct.pack('<II',27,zlib.crc32(historical))+historical),False)
 for name,body in negative.items():add(name,retained(wrap(body)),False)
 d=retained(wrap(historical));d['/config-v2.bin']=b'bad';add('invalid-current-no-rescue',d,False)
 d=retained(wrap(historical));del d['/config-v2.bin'];add('absent-current-no-rescue',d,False)
 for path in ['/ultimate-v2-0.bin','/ultimate-v2.ctrl']:
  d=retained(wrap(historical));raw=bytearray(d[path]);raw[-1]^=1;d[path]=bytes(raw);add('unrelated-corruption-'+path[1:],d,False)
 d=retained(wrap(historical),f.completed_migration(2));d['/ultimate-migration.src']=base['/config-v2.bin'];add('migration-source-receipt-still-required',d,False)
 results=[]
 for index,(name,disk,healthy) in enumerate(cases):
  out=a.out/str(index);out.mkdir();dump_namespace(disk,out/'seed.namespace');run([a.binary,'seed',out/'seed.namespace',out/'seed.nor']);run([a.binary,'boot',out/'seed.nor',defaults,out])
  if index==0:run([a.binary,'historical-classifier-faults',out/'seed.nor',defaults,out])
  boot=json.loads((out/'boot.json').read_text());status=response((out/'status.cobs').read_bytes(),cfg.ProfileStoreResponse)
  assert boot['outcome']==(1 if healthy else 6),(name,boot,status)
  assert boot['unchanged'],name
  if healthy:assert status.status==1 and status.recovery_flags==0,name
  else:assert status.status==8 and status.recovery_flags,name
  if name=='migration-source-receipt-still-required':assert 'migration proof' in status.diagnostic,status.diagnostic
  results.append(dict(name=name,healthy=healthy,diagnostic=status.diagnostic,raw_nor_unchanged=True))
 (a.out/'summary.json').write_text(json.dumps(dict(complete=True,observer_positive=len(positive),observer_negative=len(negative),namespace_cases=results,physical_filesystem_attestation=False,hardware_operations=0),indent=2)+'\n')
 print('historical compatibility:',len(positive),'positive,',len(negative),'negative,',len(cases),'namespace cases; read/seek/stat/open/close and short-read faults PASS')
if __name__=='__main__':main()
