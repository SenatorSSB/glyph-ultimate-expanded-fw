"""Disposable M1 finite-layout/conversion witness; never imported by firmware."""
import json,struct,hashlib,pathlib,copy
R=pathlib.Path('/private/tmp/glyph-profile-native-20261020'); O=pathlib.Path('/private/tmp/glyph-native-design-probe');O.mkdir(exist_ok=True)
a=json.loads((R/'tools/fixtures/stage_a_ultimate_profiles_dry_run.json').read_text()); b=json.loads((R/'tools/fixtures/stage_b_ultimate_profiles_fixture.json').read_text())['version_2']; c=json.loads((R/'tools/fixtures/stage_c_ultimate_profiles_fixture.json').read_text())
TRUE=65535; POST=lambda n:0x2000+n; ROLE=lambda n:0x3000+n
roles=[]; names={}; pool=[]
def role(name,all=(),any=(),none=()):
    assert len(all)<=2 and len(any)<=4 and len(none)<=9
    ident=len(roles)+1; roles.append({'id':ident,'all':list(all),'any':list(any),'none':list(none)});names[name]=ROLE(ident);return ROLE(ident)
p={f'lf{i}':POST(i) for i in range(1,17)}|{f'rf{i}':POST(16+i) for i in range(1,17)}|{f'lt{i}':POST(32+i) for i in range(1,9)}|{f'rt{i}':POST(40+i) for i in range(1,9)}|{f'mb{i}':POST(48+i) for i in range(1,13)}
r={}
def s(name,all=(),any=(),none=()):r[name]=role(name,all,any,none);return r[name]
s('c_any',any=[p[x] for x in ('rt2','rt3','rt4','rt5')]);s('y2sub',all=[p['lt3']],any=[p['rf3'],p['rf4']],none=[p['lf4']]);s('base_rf3',all=[p['rf3']],none=[p['lt3'],p['lf4']]);s('rf9base',all=[p['rf9'],r['base_rf3']]);s('custom',all=[p['rt1'],p['rf4']],none=[r['rf9base']]);s('rf4_cblocked',all=[p['rf4'],r['c_any']],none=[r['custom']]);s('rf4_available',all=[p['rf4']],none=[r['rf4_cblocked'],r['rf9base']]);s('force_y2',all=[r['y2sub'],p['rf2']]);s('force_lf4',all=[p['lf4'],p['rf3']]);s('force_up',any=[p['rf5'],r['force_y2'],r['force_lf4']]);s('ls_up',any=[p['lf2'],r['force_up']]);s('ls_down',any=[p['lf5'],p['lt6']],none=[r['force_up']]);s('ls_left',all=[p['lf3']],none=[p['lf1']]);s('ls_right',all=[p['lf1']],none=[p['lf3']]);s('direction_a',any=[p['lt6'],p['rf5']]);s('not_force',none=[r['force_up']]);s('rf3_suppress',all=[r['rf9base']],none=[r['c_any']]);s('digital_a',all=[p['rf1']],none=[r['y2sub']]);s('digital_b',all=[p['rf2']],none=[p['lf4'],r['y2sub']]);s('digital_y2b',all=[p['lt3'],p['rf3']],none=[p['lf4']]);s('digital_x',all=[r['base_rf3']],none=[r['rf3_suppress']]);s('digital_y2x',all=[r['y2sub'],p['rf1']],none=[r['c_any']]);s('digital_lf4x',all=[p['lf4'],p['rf2']],none=[r['c_any']]);s('null',all=[p['rf9']],none=[r['rf9base'],r['rf4_available']]);s('c_horizontal',any=[p['rt3'],p['rt4']]);s('c_vertical',any=[p['rt2'],p['rt5']]);s('c_diagonal',all=[r['c_horizontal'],r['c_vertical']]);s('rf3_vertical',all=[p['rf3'],r['c_vertical']],any=[r['ls_left'],r['ls_right']],none=[p['rt3'],p['rt4']]);s('rf6_down',all=[r['ls_down']],none=[r['ls_up']]);s('rf6_up',all=[r['ls_up']],none=[r['ls_down']])
intrinsic=len(roles)
# Separate user graph: do not borrow arbitrary user roles as intrinsic meanings.
user_id_map={}
def tok(t):
 if t<=60:return POST(t)
 return user_id_map[t-64]
for x in sorted(b['roles'],key=lambda x:x['roleId']):
 d=x['condition'];new=role('user_'+str(x['roleId']),[tok(t) for t in d.get('allTokens',[])],[tok(t) for t in d.get('anyTokens',[])],[tok(t) for t in d.get('noneTokens',[])]);user_id_map[x['roleId']]=new
rules=[]
for i,x in enumerate(b['tableRules']):
 d=x['condition'];gate=role('rule_'+str(i),[tok(t) for t in d.get('allTokens',[])],[tok(t) for t in d.get('anyTokens',[])],[tok(t) for t in d.get('noneTokens',[])]);rules.append((x['priority'],x['tableId'],gate))
bindings=[]
def bind(gate,*bits):bindings.append((gate,sum(1<<x for x in bits),255,0))
for gate in (r['digital_a'],p['lt6'],p['rf5']):bind(gate,0)
for gate in (r['digital_b'],p['lf4'],p['rf7'],r['digital_y2b']):bind(gate,1)
for gate in (r['digital_x'],r['digital_y2x'],r['digital_lf4x']):bind(gate,2)
for gate,bits in [(p['rf10'],[3]),(p['lt1'],[4,6]),(p['rf6'],[5]),(p['rf16'],[7]),(p['mb7'],[8]),(p['mb6'],[9]),(p['mb5'],[10]),(p['mb4'],[11])]:bind(gate,*bits)
sources=[(1,r['ls_left'],r['ls_right'],r['ls_down'],r['ls_up']),(2,p['rt3'],p['rt4'],p['rt2'],p['rt5']),(3,0,0,r['not_force'],r['force_up']),(4,r['ls_left'],r['ls_right'],r['rf6_down'],r['rf6_up']),(5,r['ls_left'],r['ls_right'],p['rt2'],p['rt5']),(6,0,0,0,0),(7,0,0,p['rt2'],p['rt5'])]
# Exact existing Stage C primitives; phase names appear only in this converter.
act={'BASE_TABLE':TRUE,'DIRECTION_A':r['direction_a'],'RF6':p['rf6'],'RF7':p['rf7'],'RS_DIAGONAL':r['c_diagonal'],'RF3_VERTICAL':r['rf3_vertical'],'NULL':r['null'],'TRIGGERS':TRUE,'DPAD':p['rf13']}
priority={'BASE_TABLE':200,'DIRECTION_A':80,'RF6':60,'RF7':40,'RS_DIAGONAL':100,'RF3_VERTICAL':80,'NULL':10,'TRIGGERS':200,'DPAD':20}
effects=[];mask=(TRUE,0,0,0)
for e in c['outputProgram']['effects']:
 phase=e['phase'].removeprefix('ULTIMATE_OUTPUT_PHASE_');target=e['target'].removeprefix('ULTIMATE_OUTPUT_TARGET_')
 if phase=='DIGITAL':mask=(TRUE,e.get('digitalSetMask',0),e.get('digitalClearMask',0),0);continue
 targets={'LEFT_STICK':1,'RIGHT_STICK':2,'TRIGGER_L':3,'TRIGGER_R':4,'ANALOGUE_NULL':5,'DPAD_LEFT_STICK':1};t=targets[target]
 source=1
 if phase=='DIRECTION_A':source=3
 if phase=='RF6':source=4
 if phase=='RF3_VERTICAL':source=5
 if phase in ('NULL','DPAD'):source=6
 ds=e.get('directionSource')
 if ds=='ULTIMATE_DIRECTION_SOURCE_C_STICK':source=2
 elif ds=='ULTIMATE_DIRECTION_SOURCE_CENTER':source=6
 elif ds=='ULTIMATE_DIRECTION_SOURCE_EFFECTIVE_X_C_STICK_Y':source=7 if phase in ('DIRECTION_A','NULL','DPAD') else 5
 mode={'ULTIMATE_COORDINATE_SELECTED_TABLE':1,'ULTIMATE_COORDINATE_TABLE':2,'ULTIMATE_COORDINATE_FIXED':3,'ULTIMATE_COORDINATE_INLINE':4}.get(e.get('coordinateMode'),0)
 data=list(e.get('coordinates',[0]*18))
 if mode==3:data[:2]=[e.get('fixedX',0),e.get('fixedY',0)]
 if t in (3,4):data[0]=e.get('value',0);source=0;mode=0
 gate=act[phase]
 extra=tok(e['gateToken']) if e.get('gateToken',0) else TRUE
 flags=(1 if e.get('gateInverted',False) else 0) | (2 if phase in ('BASE_TABLE','DIRECTION_A','RF6','RF7') and target=='LEFT_STICK' else 0)
 if t in (3,4):gate=0x5000+(6 if t==3 else 7)+1 # actual resolved digital trigger bit
 # 32 bytes: target,priority,activation,extra gate,source,mode,table0,table1,data18,winner,flags,reserved2.
 if not e.get('suppress',False):effects.append((t,priority[phase],gate,extra,source,mode,e.get('tableId',0),e.get('modeTableId',0),bytes(data),255,flags))
assert len(roles)<=96 and len(bindings)<=32 and len(effects)<=16
context=json.dumps(a['gameModeConfigs'][0],sort_keys=True,separators=(',',':')).encode();source=json.dumps({'a':a['ultimateProfiles'][0],'b':b,'c':c,'policy':'historical_compatibility'},sort_keys=True,separators=(',',':')).encode()
def encode(roles,rules,bindings,effects,sources,fill=False):
 header=bytearray(96);header[:4]=b'GNP5';struct.pack_into('<HHH',header,4,1,1,0);header[10:20]=bytes([len(roles),len(roles),len(sources),len(rules),len(bindings),len(effects),0,1,2,7]);struct.pack_into('<HHHH',header,20,p['rf8'],TRUE,TRUE,p['rf13']);header[28:60]=hashlib.sha256(context).digest();header[60:92]=hashlib.sha256(source).digest()
 tables=b''.join(bytes(v for xy in t['coordinates'] for v in [xy['x'],xy['y']]) for t in sorted(a['ultimateProfiles'][0]['tables'],key=lambda t:t['tableId']))
 rh=bytearray();tokens=[]
 for x in roles:
  counts=len(x['all'])|(len(x['any'])<<2)|(len(x['none'])<<5);rh+=struct.pack('<BH',x['id'],counts);tokens+=x['all']+x['any']+x['none']
 assert len(tokens)<=768;struct.pack_into('<H',header,92,len(tokens))
 body=tables+rh+b''.join(struct.pack('<H',t) for t in tokens)
 body+=b''.join(struct.pack('<BHHHH',*s) for s in sources)
 body+=b''.join(struct.pack('<BBH',*x) for x in rules)
 body+=b''.join(struct.pack('<HHBB',*x) for x in bindings)
 for t,pr,g,g2,ds,m,t0,t1,data,w,f in effects:body+=struct.pack('<BBHHBBBB18sBBH',t,pr,g,g2,ds,m,t0,t1,data,w,f,0)
 body+=struct.pack('<HHHH',*mask)
 result=header+body;struct.pack_into('<H',result,8,len(result));return bytes(result),len(tokens)
body,tokens=encode(roles,rules,bindings,effects,sources)
def vint(x):
 z=bytearray()
 while x>127:z.append((x&127)|128);x>>=7
 z.append(x);return bytes(z)
wrapped=b'\x08\x05\x42'+vint(len(body))+body
(O/'ordinary-native.body').write_bytes(body);(O/'ordinary-native.pb').write_bytes(wrapped)
# Worst storage witness: all array counts and a fully occupied finite token pool.
maxroles=[]
for i in range(96):
 n=8 # 768 total; populate all/any/none capacities across cases without exceeding finite total.
 maxroles.append({'id':i+1,'all':[POST(1),POST(2)],'any':[POST(3),POST(4),POST(5),POST(6)],'none':[POST(7),POST(8)]})
maxsources=[(i+1,POST(1),POST(2),POST(3),POST(4)) for i in range(8)]
maxrules=[(i+1,i%28,ROLE(i+1)) for i in range(32)]
maxbindings=[(ROLE(i+1),4095,255,0) for i in range(32)]
maxeffects=copy.deepcopy(effects)
for i in range(5):maxeffects.append((1,i+1,ROLE(i+1),TRUE,1,4,0,0,bytes((j+i)%256 for j in range(18)),255,0))
maxbody,maxtokens=encode(maxroles,maxrules,maxbindings,maxeffects,maxsources);maxwrapped=b'\x08\x05\x42'+vint(len(maxbody))+maxbody
(O/'maximum-native.body').write_bytes(maxbody);(O/'maximum-native.pb').write_bytes(maxwrapped)
# Decode exact offsets and ensure canonical re-encoding can be proven independently.
def check(z):
 assert z[:4]==b'GNP5' and struct.unpack_from('<HH',z,4)==(1,1) and struct.unpack_from('<H',z,8)[0]==len(z)
 rc,ec,sc,tc,bc,oc=z[10:16];nt=struct.unpack_from('<H',z,92)[0];off=600;total=0
 for i in range(rc):
  ident,counts=struct.unpack_from('<BH',z,off);off+=3;assert ident==i+1 and counts>>9==0
  counts=(counts&3,(counts>>2)&7,(counts>>5)&15);assert counts[0]<=2 and counts[1]<=4 and counts[2]<=9;total+=sum(counts)
 assert total==nt and nt<=768;off+=2*nt+sc*9+tc*4+bc*6+oc*32+8;assert off==len(z)
 return {'body':len(z),'conditions':rc,'tokens':nt,'sources':sc,'rules':tc,'bindings':bc,'effects':oc}
# Independent effect-shape/conflict checks beyond encoded-length arithmetic.
for specimen in (effects,maxeffects):
 domains={}
 for t,pr,g,g2,ds,m,t0,t1,data,w,f in specimen:
  assert t in (1,2,3,4,5) and pr>0 and (f&~3)==0 and w in (*range(28),255)
  if t in (3,4):assert ds==0 and m==0 and t0==t1==0 and not any(data[1:])
  else:assert 1<=ds<=8 and 1<=m<=4
  for domain in ((1,2) if t==5 else (t,)):
   assert (domain,pr) not in domains;domains[domain,pr]=True
result={'ordinary':check(body),'maximum':check(maxbody),'ordinary_profile_envelope':len(wrapped),'maximum_profile_envelope':len(maxwrapped),'maximum_record':32+len(maxwrapped),'sha256':hashlib.sha256(wrapped).hexdigest(),'intrinsic_roles':intrinsic,'user_roles':len(b['roles']),'rule_conditions':len(rules),'status':'layout and conversion-shape witness; NOT semantic differential/firmware acceptance'}
(O/'specimen.json').write_text(json.dumps({'roles':roles,'names':names,'rules':rules,'bindings':bindings,'effects':[{**{'target':e[0],'priority':e[1],'activation':e[2],'extra_gate':e[3],'source':e[4],'mode':e[5],'table0':e[6],'table1':e[7],'coordinates':list(e[8]),'winner':e[9],'flags':e[10]}} for e in effects],'sources':sources},indent=2))
(O/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
