"""Differential frozen Config inventory/canonical oracle versus streaming C++."""
from pathlib import Path
import copy,json,random,struct,subprocess,sys,os
HERE=Path(__file__).resolve().parent
ROOT=Path(os.environ['GLYPH_PACKAGE_REPO']).resolve()
CORPUS=Path(os.environ['GLYPH_PACKAGE_CORPUS']).resolve()
sys.path[:0]=[os.environ.get('GLYPH_PACKAGE_RESEARCH', str(ROOT/'tools/research')),str(CORPUS/'proof'),str(CORPUS/'wire')]
import glyph_package_storage as model,glyph_package_fixtures as fixtures
inventory,encode=model.config_wire();schema=inventory.__globals__['SCHEMA']
def var(v):
 b=bytearray()
 while v>=128:b.append((v&127)|128);v>>=7
 return bytes(b)+bytes([v])
def scalar(n,v):return var(n<<3)+var(v)
def data(n,b):return var(n<<3|2)+var(len(b))+b
paths={'Config':[]}
def walk(name):
 for n,f in schema[name].items():
  if f['type']==11 and f['message'] not in paths:
   paths[f['message']]=paths[name]+[(name,int(n))];walk(f['message'])
walk('Config')
def node(name,parts):
 # Independent empty-tree encoder supplies only mandatory fixed-byte defaults.
 defaults=[]
 for n,f in schema[name].items():
  if f['type']==12 and f['options'].get('fixed_length')=='true' and int(n) not in {p[0] for p in parts}:defaults.append((int(n),data(int(n),bytes(int(f['options']['max_size'])))))
 return b''.join(raw for _,raw in sorted(parts+defaults,key=lambda t:t[0]))
def wrap(name,raw):
 for parent,n in reversed(paths[name]):raw=node(parent,[(n,data(n,raw))])
 return raw
cases=[];groups={}
def add(group,name,raw,expected=None):
 try:tree=inventory(raw);ok=encode(tree)==raw
 except (ValueError,UnicodeError):ok=False
 if expected is not None:assert ok==expected,('test construction',name,ok)
 cases.append((group,name,raw,ok));groups[group]=groups.get(group,0)+1
# Every reachable message/field receives independent schema-driven controls.
for message,path in paths.items():
 add('schema-positive','empty '+message,wrap(message,encode([],message)),True)
 add('unknown','unknown '+message,wrap(message,node(message,[(max(map(int,schema[message]))+1,scalar(max(map(int,schema[message]))+1,1))])),False)
 for text,field in schema[message].items():
  n=int(text);kind=field['type'];opt=field['options'];repeated=field['repeated'];label=message+'.'+field['name']
  def put(raw):return wrap(message,node(message,[(n,raw)]))
  if field['nanopb']['storage']=='CALLBACK':
   add('callback',label,put(data(n,b'')),False);continue
  if repeated:
   maximum=int(opt['max_count'])
   if kind==11:
    child=encode([],field['message']);good=data(n,child)
    add('schema-positive','repeated '+label,put(good*maximum),True)
    add('count',label,put(good*(maximum+1)),False)
   else:
    add('schema-positive','packed '+label,put(data(n,bytes(maximum))),True)
    add('count',label,put(data(n,bytes(maximum+1))),False)
    add('unpacked',label,put(scalar(n,0)),False)
    add('split-packed',label,put(data(n,b'\0')+data(n,b'\0')),False)
    add('packed-empty',label,put(data(n,b'')),False)
    if kind==14:add('enum',label,put(data(n,var(max(field['enum_values'])+1))),False)
   continue
  if kind in (4,8,13,14):
   limits={'IS_8':255,'IS_16':65535,'IS_32':2**32-1,'IS_64':2**64-1};maximum=limits.get(opt.get('int_size'),2**32-1 if kind in (13,14) else 2**64-1)
   vals=field.get('enum_values',[0,1 if kind==8 else maximum])
   for value in vals:
    if value:add('schema-positive',label+'='+str(value),put(scalar(n,value)),True)
   add('default',label,put(scalar(n,0)),False)
   if kind==14:add('enum',label,put(scalar(n,max(vals)+1)),False)
   elif kind==8:add('bool',label,put(scalar(n,2)),False)
   elif maximum<2**64-1:add('width',label,put(scalar(n,maximum+1)),False)
   good=scalar(n,next(v for v in vals if v))
   add('duplicate',label,put(good+good),False)
  elif kind==9:
   maximum=int(opt['max_length'])
   add('schema-positive',label,put(data(n,b'A'*maximum)),True)
   add('schema-positive',label+' Unicode',put(data(n,'\U0010ffff'.encode())),True)
   for raw in (b'\xff',b'\0',b'\xc0\x80',b'\xed\xa0\x80',b'\xf4\x90\x80\x80',b'\xe2\x82'):
    add('UTF8/NUL',label+' '+raw.hex(),put(data(n,raw)),False)
   add('extent',label,put(data(n,b'A'*(maximum+1))),False)
   add('default',label,put(data(n,b'')),False)
  elif kind==12:
   maximum=int(opt['max_size']);add('schema-positive',label,put(data(n,bytes(maximum))),True)
   for size in [0,maximum-1,maximum+1]:add('fixed-bytes',label+' '+str(size),put(data(n,bytes(size))),False)
  elif kind==11:
   good=data(n,encode([],field['message']));add('schema-positive',label,put(good),True);add('duplicate',label,put(good+good),False)
  elif kind==2:
   for raw in (b'\0'*4,struct.pack('<I',0x80000000),struct.pack('<I',0x7fc00001),struct.pack('<I',0x7f800000),struct.pack('<f',1.5)):
    add('float',label+' '+raw.hex(),put(var(n<<3|5)+raw),raw!=b'\0'*4)
# Explicit tag-order and overlong-key probes at every reachable message level.
def fragment(n,f):
 kind=f['type'];op=f['options']
 if kind==11:return data(n,encode([],f['message']))
 if f['repeated']:return data(n,b'\0')
 if kind==9:return data(n,b'A')
 if kind==12:return data(n,bytes(int(op['max_size'])))
 if kind==2:return var(n<<3|5)+struct.pack('<f',1.5)
 return scalar(n,1)
for message in paths:
 fs=[(int(n),f) for n,f in sorted(schema[message].items(),key=lambda x:int(x[0])) if f['nanopb']['storage']!='CALLBACK']
 (n,a),(m,b)=fs[:2];first,second=fragment(n,a),fragment(m,b)
 canonical=node(message,[(n,first),(m,second)])
 assert canonical.startswith(first+second)
 add('field-order',message,wrap(message,second+first+canonical[len(first+second):]),False)
 assert first[0]<128
 bad=bytes([first[0]|128,0])+first[1:]
 add('nonminimal-key',message,wrap(message,node(message,[(n,bad)])),False)
# Source-backed retained Config vectors and all generated package/migration states.
for name in ['config_vectors.json','source_operation_vectors.json']:
 d=json.loads((ROOT/'contracts/glyph-reference-v1'/name).read_text())
 for key in ('before','after'):add('retained-Config',name+' '+key,bytes.fromhex(d[key]),True)
stage=(ROOT/'contracts/glyph-reference-v1/stage-v3-fixture.pb').read_bytes()
add('retained-original','stage-v3-fixture',stage)
add('retained-Config','stage-v3 canonical projection',encode(inventory(stage)),True)
from source_native_oracle import SourceNativeOracle
source=SourceNativeOracle(CORPUS/'wire');model.CONFIG_VALIDATOR=source.check_config;model.NATIVE_VALIDATOR=source.check;model.LEGACY_PROFILE_VALIDATOR=source.check_profile
disks=[]
for rows in (1,29,30):
 for ultimate in (False,True):disks.append(fixtures.baseline(rows,ultimate))
for with_rgb,empty in [(False,False),(True,False),(True,True)]:
 first,_=fixtures.package_plan(fixtures.baseline(),with_rgb,empty_rgb=empty);second,_=fixtures.package_plan(first['COMMITTED'],False,200);disks.extend(first.values());disks.extend(second.values());disks.append(fixtures.later_raw_create(second['COMMITTED']))
for version in (1,2):disks.append(fixtures.completed_migration(version))
seen=set()
for index,disk in enumerate(disks):
 for name,raw in disk.items():
  if (name.startswith('/config') or name.endswith('migration.src')) and len(raw)>=8:
   body,_=model.config_body(raw,65536)
   if body not in seen:seen.add(body);add('snapshot','disk'+str(index)+name,body,True)
# Required concrete counterexamples from strongest review.
base=fixtures.baseline()['/config-v2.bin'][8:]
concrete=[('MODE enum11 actual source',base.replace(b'\x08\x01',b'\x08\x0b',1)),('UTF8 FF actual source',base.replace(b'Unmanaged',b'\xffnmanaged',1))]
for name,raw in concrete:
 add('source-regression',name,raw,False)
 actual=subprocess.run([str(source.config_binary)],input=raw.hex()+'\n',text=True,capture_output=True)
 assert actual.returncode==0,(name,actual.stderr)
 print(name+': actual pinned C++ pb_decode/source-validator ACCEPTS; frozen strict oracle REJECTS')
source.close();model.CONFIG_VALIDATOR=model.NATIVE_VALIDATOR=model.LEGACY_PROFILE_VALIDATOR=None

add('regression','MODE enum11',wrap('GameModeConfig',scalar(1,11)),False)
add('regression','name UTF8 FF',wrap('GameModeConfig',data(2,b'\xff')),False)
base=fixtures.baseline()['/config-v2.bin'][8:]
minuszero=HERE/'minus-zero-before.pb'
if minuszero.exists():add('minus-zero-source','actual source-valid float -0',minuszero.read_bytes(),True)
add('fixed-presence','absent Config205/209',b'',False)
for missing in (205,209):
 _,tree=model.config_body(fixtures.baseline()['/config-v2.bin']);raw=b''.join(part for number,part in [(205,data(205,bytes(32))),(209,data(209,bytes(32)))] if number!=missing);add('fixed-presence',str(missing),raw,False)
for prefix in range(len(base)):add('prefix','base '+str(prefix),base[:prefix])
rng=random.Random(0xB2C0F1)
seeds=[base,*sorted(seen)]
for i in range(2000):
 raw=bytearray(rng.choice(seeds));at=rng.randrange(len(raw)+1);op=rng.randrange(3)
 if op==0:raw[at:at]=bytes([rng.randrange(256)])
 elif op==1 and at<len(raw):del raw[at]
 elif at<len(raw):raw[at]^=1<<rng.randrange(8)
 add('mutation',str(i),bytes(raw))
# Historical inventory may exceed the package CREATE Config8191 cap.
# Saturate only schema bounds; source semantic validation is deliberately separate.
def saturated(message):
 entries=[]
 for text,f in schema[message].items():
  if f['nanopb']['storage']=='CALLBACK':continue
  kind=f['type'];op=f['options']
  if kind==11:value=saturated(f['message'])
  elif kind==9:value='A'*int(op['max_length'])
  elif kind==12:value='00'*int(op['max_size'])
  elif kind==2:value=struct.pack('<f',1.5).hex()
  elif kind==14:value=max(f['enum_values'])
  elif kind==8:value=1
  else:value={'IS_8':255,'IS_16':65535,'IS_32':2**32-1,'IS_64':2**64-1}.get(op.get('int_size'),2**32-1 if kind in (13,14) else 2**64-1)
  values=[copy.deepcopy(value) for _ in range(int(op['max_count']))] if f['repeated'] else [value]
  entries.append(dict(number=int(text),values=values))
 return entries
historical=encode(saturated('Config'));assert 8191<len(historical)<=65536,len(historical)
add('historical-large','saturated Config '+str(len(historical)),historical,True)
print('Schema-valid historical Config body bytes',len(historical),'(separate source validation still mandatory)')
for raw in [b'\0',b'\x80',b'\x88\0\1',b'\xff'*10,b'\xff'*65536,b'\xff'*65537]:add('bounds',str(len(raw)),raw,False)
proc=subprocess.run([os.environ.get('CONFIG_WIRE_PROBE',str(HERE/'build/probe'))],input='\n'.join(raw.hex() for _,_,raw,_ in cases)+'\n',text=True,capture_output=True,check=False)
if proc.returncode:print(proc.stderr);raise SystemExit(proc.returncode)
lines=proc.stdout.splitlines();assert len(lines)==len(cases),(len(lines),len(cases),proc.stderr)
for (group,name,raw,expected),actual in zip(cases,lines):assert (actual=='0')==expected,(group,name,actual,expected,raw.hex()[:300])
valid=sum(x[3] for x in cases);print('Differential oracle PASS:',len(cases),'cases;',valid,'valid;',len(cases)-valid,'rejected;',len(seen),'unique package/migration Config snapshots; reader chunks1/2/3/7/31/32/255/256 and first/later-read storage failures')
print('Groups:',json.dumps(groups,sort_keys=True))
if os.environ.get('GLYPH_PACKAGE_TEST_OUTPUT'):
 (Path(os.environ['GLYPH_PACKAGE_TEST_OUTPUT'])/'config-results.json').write_text(json.dumps(dict(cases=len(cases),valid=valid,rejected=len(cases)-valid,snapshots=len(seen),groups=groups),indent=2)+'\n')
