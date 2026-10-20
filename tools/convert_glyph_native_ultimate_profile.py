#!/usr/bin/env python3
"""Non-destructive V1–V3 -> finite schema5 Ultimate converter.

The converter preserves historical source semantics by default only when the
caller explicitly selects historical_compatibility. It never opens a device.
The package binds the exact ordered preprocessing context and original input.
"""
from __future__ import annotations
import argparse, base64, copy, hashlib, json, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TRUE=65535
POST=lambda n:0x2000+n
ROLE=lambda n:0x3000+n


def preprocessing_bytes(context, pb):
    if context.mode_id != pb.MODE_ULTIMATE: raise ValueError('context must be MODE_ULTIMATE')
    if len(context.button_remapping)>60 or len(context.socd_pairs)>10: raise ValueError('context extent')
    out=bytearray(b'Glyph.Native.Preprocess.v1\0')
    out+=struct.pack('<HB',context.mode_id,len(context.button_remapping))
    for r in context.button_remapping:
        if not 1<=r.physical_button<=60 or not 1<=r.activates<=60: raise ValueError('remap ID')
        out+=bytes([r.physical_button,r.activates])
    out+=bytes([len(context.socd_pairs)])
    for s in context.socd_pairs:
        if not 1<=s.button_dir1<=60 or not 1<=s.button_dir2<=60 or not 0<=s.socd_type<=5: raise ValueError('SOCD context')
        out+=bytes([s.button_dir1,s.button_dir2,s.socd_type])
    return bytes(out)


def convert(profile_message, context, pb, policy, *, options=None):
    from google.protobuf.json_format import MessageToDict
    if policy != 'historical_compatibility': raise ValueError('unsupported conversion policy; select historical_compatibility explicitly')
    original=profile_message.SerializeToString(deterministic=True)
    context_original=context.SerializeToString(deterministic=True)
    if profile_message.schema_version not in (1,2,3): raise ValueError('only admitted legacy schemas 1–3 can be converted')
    # Reuse the current host validator; malformed source is never repaired or
    # truncated to manufacture a convertible profile.
    import glyph_serial_config_tool as writer
    wrapper=pb.Config(); wrapper.ultimate_profiles.add().CopyFrom(profile_message)
    errors=writer.verify_ultimate_profiles(wrapper,pb)
    if errors: raise ValueError('invalid legacy source: '+str(errors))
    profile=MessageToDict(profile_message)
    version=profile_message.schema_version
    context_digest=hashlib.sha256(preprocessing_bytes(context,pb)).digest()
    source_digest=hashlib.sha256(b'Glyph.Native.Conversion.v1\0'+policy.encode()+b'\0'+original).digest()
    routing={r.slot_id:r.input_token for r in profile_message.routing_slots}
    routed_token=lambda t:POST(routing[t]) if t in routing else 0
    intrinsic_token=routed_token if version==3 else POST
    b=profile if version>=2 else json.loads((ROOT/'tools/fixtures/stage_b_ultimate_profiles_fixture.json').read_text())['version_2']
    if version==1: routed_token=POST
    c=profile if version==3 else json.loads((ROOT/'tools/fixtures/stage_c_ultimate_profiles_fixture.json').read_text())
    dpad_flags=7; dpad_gate=intrinsic_token(29)
    roles=[]; names={}; pool=[]
    def role(name,all=(),any=(),none=()):
        assert len(all)<=2 and len(any)<=4 and len(none)<=9
        ident=len(roles)+1; roles.append({'id':ident,'all':list(all),'any':list(any),'none':list(none)});names[name]=ROLE(ident);return ROLE(ident)
    p={f'lf{i}':intrinsic_token(i) for i in range(1,17)}|{f'rf{i}':intrinsic_token(16+i) for i in range(1,17)}|{f'lt{i}':intrinsic_token(32+i) for i in range(1,9)}|{f'rt{i}':intrinsic_token(40+i) for i in range(1,9)}|{f'mb{i}':intrinsic_token(48+i) for i in range(1,13)}
    r={}
    def s(name,all=(),any=(),none=()):r[name]=role(name,all,any,none);return r[name]
    s('c_any',any=[p[x] for x in ('rt2','rt3','rt4','rt5')]);s('y2sub',all=[p['lt3']],any=[p['rf3'],p['rf4']],none=[p['lf4']]);s('base_rf3',all=[p['rf3']],none=[p['lt3'],p['lf4']]);s('rf9base',all=[p['rf9'],r['base_rf3']]);s('custom',all=[p['rt1'],p['rf4']],none=[r['rf9base']]);s('rf4_cblocked',all=[p['rf4'],r['c_any']],none=[r['custom']]);s('rf4_available',all=[p['rf4']],none=[r['rf4_cblocked'],r['rf9base']]);s('force_y2',all=[r['y2sub'],p['rf2']]);s('force_lf4',all=[p['lf4'],p['rf3']]);s('force_up',any=[p['rf5'],r['force_y2'],r['force_lf4']]);s('ls_up',any=[p['lf2'],r['force_up']]);s('ls_down',any=[p['lf5'],p['lt6']],none=[r['force_up']]);s('ls_left',all=[p['lf3']],none=[p['lf1']]);s('ls_right',all=[p['lf1']],none=[p['lf3']]);s('direction_a',any=[p['lt6'],p['rf5']]);s('not_force',none=[r['force_up']]);s('rf3_suppress',all=[r['rf9base']],none=[r['c_any']]);s('digital_a',all=[p['rf1']],none=[r['y2sub']]);s('digital_b',all=[p['rf2']],none=[p['lf4'],r['y2sub']]);s('digital_y2b',all=[p['lt3'],p['rf3']],none=[p['lf4']]);s('digital_x',all=[r['base_rf3']],none=[r['rf3_suppress']]);s('digital_y2x',all=[r['y2sub'],p['rf1']],none=[r['c_any']]);s('digital_lf4x',all=[p['lf4'],p['rf2']],none=[r['c_any']]);s('null',all=[p['rf9']],none=[r['rf9base'],r['rf4_available']]);s('c_horizontal',any=[p['rt3'],p['rt4']]);s('c_vertical',any=[p['rt2'],p['rt5']]);s('c_diagonal',all=[r['c_horizontal'],r['c_vertical']]);s('rf3_vertical',all=[p['rf3'],r['c_vertical']],any=[r['ls_left'],r['ls_right']],none=[p['rt3'],p['rt4']]);s('rf6_down',all=[r['ls_down']],none=[r['ls_up']]);s('rf6_up',all=[r['ls_up']],none=[r['ls_down']])
    intrinsic=len(roles)
    # Separate user graph: do not borrow arbitrary user roles as intrinsic meanings.
    user_id_map={}
    def tok(t):
     if 1<=t<=60:return routed_token(t)
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
     if phase=='DIGITAL':
      mask=(tok(e['gateToken']) if e.get('gateToken') else TRUE,e.get('digitalSetMask',0),e.get('digitalClearMask',0),int(bool(e.get('gateToken') and e.get('gateInverted'))));continue
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
     flags=(1 if e.get('gateToken') and e.get('gateInverted',False) else 0) | (2 if phase in ('BASE_TABLE','DIRECTION_A','RF6','RF7') and target=='LEFT_STICK' else 0)
     if t in (3,4):gate=0x5000+(6 if t==3 else 7)+1 # actual resolved digital trigger bit
     # 32 bytes: target,priority,activation,extra gate,source,mode,table0,table1,data18,winner,flags,reserved2.
     if phase=='DPAD':
      dpad_flags=0 if e.get('suppress',False) else e.get('value',0)
      if e.get('gateToken'):
       dpad_gate=role('dpad-extra',all=[p['rf13']],**({'none':[extra]} if e.get('gateInverted') else {'any':[extra]}))
      else:dpad_gate=p['rf13']
     if not e.get('suppress',False) and (phase!='DPAD' or dpad_flags&2):effects.append((t,priority[phase],gate,extra,source,mode,e.get('tableId',0),e.get('modeTableId',0),bytes(data),255,flags))
    if len(roles)>96 or len(bindings)>32 or len(effects)>16: raise ValueError("native section capacity exceeded")
    def encode(roles,rules,bindings,effects,sources,fill=False):
     header=bytearray(96);header[:4]=b'GNP5';struct.pack_into('<HHH',header,4,1,1,0);header[10:20]=bytes([len(roles),len(roles),len(sources),len(rules),len(bindings),len(effects),b.get("defaultTableId",0),1,2,dpad_flags]);struct.pack_into('<HHHH',header,20,p['rf8'],TRUE,TRUE,dpad_gate);header[28:60]=context_digest;header[60:92]=source_digest
     tables=b''.join(bytes(v for xy in t['coordinates'] for v in [xy.get('x',0),xy.get('y',0)]) for t in sorted(profile['tables'],key=lambda t:t.get('tableId',0)))
     rh=bytearray();tokens=[]
     for x in roles:
      counts=len(x['all'])|(len(x['any'])<<2)|(len(x['none'])<<5);rh+=struct.pack('<BH',x['id'],counts);tokens+=x['all']+x['any']+x['none']
     if len(tokens)>768: raise ValueError("native token capacity exceeded")
     struct.pack_into('<H',header,92,len(tokens))
     body=tables+rh+b''.join(struct.pack('<H',t) for t in tokens)
     body+=b''.join(struct.pack('<BHHHH',*s) for s in sources)
     body+=b''.join(struct.pack('<BBH',*x) for x in rules)
     body+=b''.join(struct.pack('<HHBB',*x) for x in bindings)
     for t,pr,g,g2,ds,m,t0,t1,data,w,f in effects:body+=struct.pack('<BBHHBBBB18sBBH',t,pr,g,g2,ds,m,t0,t1,data,w,f,0)
     body+=struct.pack('<HHHH',*mask)
     result=header+body;struct.pack_into('<H',result,8,len(result));return bytes(result),len(tokens)
    body,tokens=encode(roles,rules,bindings,effects,sources)
    if len(body)>3336: raise ValueError('native body capacity exceeded')
    native=pb.UltimateProfile(schema_version=5,native_payload=body)
    wire=native.SerializeToString(deterministic=True)
    assert len(wire)<=3341
    assert profile_message.SerializeToString(deterministic=True)==original
    assert context.SerializeToString(deterministic=True)==context_original
    files=['src/modes/Ultimate.cpp','include/modes/UltimateProfileEvaluator.hpp','schema/haybox/config.proto','schema/haybox/config.options']
    metadata={'schema':5,'encoding':1,'engine_abi':1,'policy':policy,'source_schema':version,
      'legacy_payload_sha256':hashlib.sha256(original).hexdigest(),'native_payload_sha256':hashlib.sha256(wire).hexdigest(),
      'body_sha256':hashlib.sha256(body).hexdigest(),'preprocessing_sha256':context_digest.hex(),
      'preprocessing':MessageToDict(context),'preprocessing_canonical_hex':preprocessing_bytes(context,pb).hex(),
      'conversion_source_sha256':source_digest.hex(),'source_files':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
      'old_role_id_to_native_token':user_id_map,'counts':{'conditions':len(roles),'tokens':tokens,'bindings':len(bindings),'effects':len(effects),'tables':28},
      'correspondence':'Historical source compatibility including LT6 post-table override, V2 selection-only routing and V3 exactly-once routing; all 18 source families.',
      'limitations':['Raw controller outputs only; no gameplay semantics or hardware acceptance.','Nunchuk physical acceptance NOT_TESTED.']}
    return native,metadata


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True,help='Complete Config JSON or protobuf input (never modified)')
    parser.add_argument('--profile-index',type=int,default=0)
    parser.add_argument('--mode-index',type=int,required=True)
    parser.add_argument('--policy',choices=['historical_compatibility'],required=True)
    parser.add_argument('--output',type=Path,required=True,help='New output package directory')
    a=parser.parse_args()
    import glyph_serial_config_tool as writer
    pb,jf,_=writer.load_runtime_proto_modules(ROOT)
    config=pb.Config()
    if a.input.suffix=='.json':jf.Parse(a.input.read_text(),config)
    else:config.ParseFromString(a.input.read_bytes())
    native,metadata=convert(config.ultimate_profiles[a.profile_index],config.game_mode_configs[a.mode_index],pb,a.policy)
    a.output.mkdir(parents=True,exist_ok=False)
    (a.output/'profile.pb').write_bytes(native.SerializeToString(deterministic=True))
    (a.output/'profile.json').write_text(jf.MessageToJson(native)+'\n')
    (a.output/'conversion.json').write_text(json.dumps(metadata,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'output':str(a.output),'body_bytes':len(native.native_payload),'payload_sha256':metadata['native_payload_sha256'],'device_access':False}))
    return 0

if __name__=='__main__':raise SystemExit(main())
