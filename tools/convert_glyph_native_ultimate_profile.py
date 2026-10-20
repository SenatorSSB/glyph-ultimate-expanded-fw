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


def raw_fields(data):
    """Bounded protobuf field walk retaining presence before proto3 normalization."""
    cursor=0
    def varint():
        nonlocal cursor
        value=0
        for i in range(10):
            if cursor>=len(data):raise ValueError('truncated protobuf varint')
            b=data[cursor];cursor+=1
            if i==9 and b>1:raise ValueError('overlong protobuf varint')
            value|=(b&127)<<(7*i)
            if not b&128:return value
        raise ValueError('overlong protobuf varint')
    while cursor<len(data):
        key=varint();tag=key>>3;wire=key&7
        if not tag or tag>0x1fffffff:raise ValueError('invalid protobuf tag')
        if wire==0:value=varint()
        else:
            length=varint() if wire==2 else 8 if wire==1 else 4 if wire==5 else -1
            if length<0 or length>len(data)-cursor:raise ValueError('invalid protobuf field extent/wire type')
            value=data[cursor:cursor+length];cursor+=length
        yield tag,wire,value


def validate_profile_wire(data):
    fields=list(raw_fields(data));schemas=[v for t,w,v in fields if t==1 and w==0]
    if not schemas:raise ValueError('profile schema missing')
    schema=schemas[-1];native=[v for t,w,v in fields if t==8 and w==2]
    if schema==5:
        if len(schemas)!=1 or len(native)!=1 or any(t not in (1,8) for t,w,v in fields) or len(fields)!=2:
            raise ValueError('native wrapper must contain exactly schema5 and one payload')
        return validate_native_body(native[0])
    if any(t==8 for t,w,v in fields):raise ValueError('native field is forbidden in legacy profile, including empty field')
    if schema not in (1,2,3):raise ValueError('unsupported profile schema')
    return {'schema':schema,'engine':'legacy'}


def validate_native_body(body):
    def require(value,label):
        if not value:raise ValueError('invalid native '+label)
    require(isinstance(body,bytes) and 608<=len(body)<=3336,'body extent')
    u16=lambda offset:struct.unpack_from('<H',body,offset)[0]
    require(body[:4]==b'GNP5' and u16(4)==1 and u16(6)==1 and u16(8)==len(body) and not u16(94),'header')
    count,early,sources,rules,bindings,effects=body[10:16]
    require(count<=96 and early<=count and 1<=sources<=8 and rules<=32 and bindings<=32 and effects<=16,'section counts')
    require(body[16]<28 and 1<=body[17]<=sources and 1<=body[18]<=sources and body[19]<=7 and u16(92)<=768,'header references')
    require(len(body)==608+3*count+2*u16(92)+9*sources+4*rules+6*bindings+32*effects,'fixed section lengths')
    def token(t,roles,dirs=False,digital=False):
        if t in (0,65535):return True
        kind=t&0xf000;ident=t&0xfff
        return (kind in (0,0x1000,0x2000) and 1<=ident<=60 or kind==0x3000 and 1<=ident<=roles or
                dirs and kind==0x4000 and 1<=ident<=8 or digital and kind==0x5000 and 1<=ident<=12)
    offset=600+3*count;used=0
    for i in range(count):
        packed=u16(601+3*i);a=packed&3;any_count=(packed>>2)&7;none=(packed>>5)&15
        require(body[600+3*i]==i+1 and not packed>>9 and a<=2 and any_count<=4 and none<=9,'condition shape/ID')
        n=a+any_count+none;used+=n;require(used<=u16(92),'token pool')
        for j in range(n):require(token(u16(offset+2*j),i,i>=early),'condition domain/stage/reference')
        offset+=n*2
    require(used==u16(92),'token pool occupancy')
    for i in range(sources):
        require(body[offset]==i+1,'source ID');base=i+1 in (body[17],body[18])
        for j in range(4):require(token(u16(offset+1+2*j),early if base else count,not base),'direction source reference')
        offset+=9
    priorities=set()
    for _ in range(rules):
        priority,table=body[offset:offset+2]
        require(priority and priority not in priorities and table<28 and token(u16(offset+2),count,True),'table rule')
        priorities.add(priority);offset+=4
    winner=lambda x:x<28 or x==255
    for _ in range(bindings):
        require(token(u16(offset),count,True) and not u16(offset+2)&~4095 and winner(body[offset+4]) and not body[offset+5],'digital binding')
        offset+=6
    priorities=set()
    for _ in range(effects):
        p=body[offset:offset+32];target,priority=p[:2];mode=p[7]
        require(1<=target<=5 and priority and token(u16(offset+2),count,True,True) and token(u16(offset+4),count,True,True) and winner(p[28]) and not p[29]&~3 and not u16(offset+30),'effect shape')
        for domain in ((1,2) if target==5 else (target,)):
            require((domain,priority) not in priorities,'overlapping effect priority');priorities.add((domain,priority))
        if target in (3,4):require(not any(p[6:10]) and not any(p[11:28]) and not p[29]&2,'trigger effect')
        else:
            require(1<=p[6]<=sources and 1<=mode<=4,'effect coordinate/source')
            if mode==1:require(not any(p[8:28]),'selected-table union')
            if mode==2:require(p[8]<28 and p[9]<28 and not any(p[10:28]),'table union')
            if mode==3:require(not any(p[8:10]) and not any(p[12:28]),'fixed union')
            if mode==4:require(not any(p[8:10]),'inline union')
        offset+=32
    require(token(u16(offset),count,True) and not (u16(offset+2)|u16(offset+4))&~4095 and not u16(offset+2)&u16(offset+4) and u16(offset+6)<=1,'digital post mask')
    for i in range(4):require(token(u16(20+2*i),count,True),'header gate')
    return {'schema':5,'encoding':1,'engine_abi':1,'engine':'native_abi1','body_bytes':len(body)}


def validate_standalone_profile(profile,pb):
    if profile.schema_version==5:
        if profile.tables or profile.roles or profile.routing_slots or profile.default_table_id or profile.table_rules or profile.HasField('output_program'):
            raise ValueError('native profile contains legacy fields')
        return validate_profile_wire(profile.SerializeToString(deterministic=True))
    if profile.native_payload:raise ValueError('legacy profile contains native field')
    import glyph_serial_config_tool as writer
    if profile.schema_version not in (1,2,3):raise ValueError('unsupported legacy profile schema')
    return {'schema':profile.schema_version,'engine':'legacy','legacy_semantic_admission':'firmware existing validator'}


def preprocessing_bytes(context, pb):
    if context.mode_id != pb.MODE_ULTIMATE: raise ValueError('context must be MODE_ULTIMATE')
    if len(context.button_remapping)>60 or len(context.socd_pairs)>10: raise ValueError('context extent')
    out=bytearray(b'Glyph.Native.Preprocess.v1\0')
    out+=struct.pack('<HB',context.mode_id,len(context.button_remapping))
    for r in context.button_remapping:
        if not 1<=r.physical_button<=60 or not 0<=r.activates<=60: raise ValueError('remap ID')
        out+=bytes([r.physical_button,r.activates])
    out+=bytes([len(context.socd_pairs)])
    for s in context.socd_pairs:
        if not 1<=s.button_dir1<=60 or not 1<=s.button_dir2<=60 or not 0<=s.socd_type<=5: raise ValueError('SOCD context')
        out+=bytes([s.button_dir1,s.button_dir2,s.socd_type])
    return bytes(out)


def convert(profile_message, context, pb, policy, *, options=None):
    from google.protobuf.json_format import MessageToDict
    if policy not in ('historical_compatibility','clean_down_a','forced_table_down_a'):
        raise ValueError('unsupported conversion policy')
    options=copy.deepcopy(options or {})
    if policy!='historical_compatibility':
        required={'physical_input'}
        if policy=='clean_down_a':required|={'down_input','up_input'}
        else:required|={'table_id','table_priority','forced_x','forced_y'}
        allowed=required|{'a_winner_table'}
        if not required<=options.keys() or options.keys()-allowed:raise ValueError('policy requires exactly explicit '+str(sorted(required))+' and optional a_winner_table')
        if not 1<=options['physical_input']<=60:raise ValueError('physical input ID')
        if policy=='clean_down_a':
            for key in ('down_input','up_input'):
                if not 1<=options[key]<=60:raise ValueError('clean policy input ID')
            if options['down_input']==options['up_input']:raise ValueError('opposing inputs must differ')
            # Only genuine direction composition requires an explicit remap
            # and opposing policy. Forced-table composition adds no direction.
            first=next((r for r in context.button_remapping if r.physical_button==options['physical_input']),None)
            mapped=first.activates if first else options['physical_input']
            if mapped!=options['down_input']:raise ValueError('clean physical input must map to explicit down input in provided context')
            if not any({s.button_dir1,s.button_dir2}=={options['down_input'],options['up_input']} for s in context.socd_pairs):
                raise ValueError('clean policy requires explicit opposing pair and policy in provided context')
        else:
            if not 0<=options['table_id']<28 or not 1<=options['table_priority']<=255:raise ValueError('forced-table IDs/priorities')
            if not 0<=options['forced_x']<=255 or not 0<=options['forced_y']<=255:raise ValueError('forced raw coordinates')
    original=profile_message.SerializeToString(deterministic=True)
    context_original=context.SerializeToString(deterministic=True)
    if profile_message.native_payload:raise ValueError('mixed legacy source contains native payload')
    if profile_message.schema_version not in (1,2,3): raise ValueError('only admitted legacy schemas 1–3 can be converted')
    # Reuse the current host validator; malformed source is never repaired or
    # truncated to manufacture a convertible profile.
    import glyph_serial_config_tool as writer
    wrapper=pb.Config(); wrapper.ultimate_profiles.add().CopyFrom(profile_message)
    errors=writer.verify_ultimate_profiles(wrapper,pb)
    if errors: raise ValueError('invalid legacy source: '+str(errors))
    profile=MessageToDict(profile_message)
    if policy=='forced_table_down_a':
        # Forced coordinates are ordinary nine-way table data. No force effect
        # or extra resolver is added. Arbitrary legacy base modes that bypass
        # selected tables cannot truthfully satisfy this clean-policy contract.
        if profile_message.schema_version==3:
            base=next((e for e in profile_message.output_program.effects if e.phase==pb.ULTIMATE_OUTPUT_PHASE_BASE_TABLE and e.target==pb.ULTIMATE_OUTPUT_TARGET_LEFT_STICK),None)
            if base is None or base.suppress or base.gate_token or base.coordinate_mode!=pb.ULTIMATE_COORDINATE_SELECTED_TABLE:
                raise ValueError('forced-table policy requires enabled unconditional selected-table base LS effect')
        target=next(t for t in profile['tables'] if t.get('tableId',0)==options['table_id'])
        target['coordinates']=[{'x':options['forced_x'],'y':options['forced_y']} for _ in range(9)]
    version=profile_message.schema_version
    context_digest=hashlib.sha256(preprocessing_bytes(context,pb)).digest()
    source_digest=hashlib.sha256(b'Glyph.Native.Conversion.v1\0'+policy.encode()+b'\0'+json.dumps(options,sort_keys=True,separators=(',',':')).encode()+b'\0'+original).digest()
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
    if policy!='historical_compatibility':p['lt6']=0
    r={}
    def s(name,all=(),any=(),none=()):r[name]=role(name,all,any,none);return r[name]
    s('c_any',any=[p[x] for x in ('rt2','rt3','rt4','rt5')]);s('y2sub',all=[p['lt3']],any=[p['rf3'],p['rf4']],none=[p['lf4']]);s('base_rf3',all=[p['rf3']],none=[p['lt3'],p['lf4']]);s('rf9base',all=[p['rf9'],r['base_rf3']]);s('custom',all=[p['rt1'],p['rf4']],none=[r['rf9base']]);s('rf4_cblocked',all=[p['rf4'],r['c_any']],none=[r['custom']]);s('rf4_available',all=[p['rf4']],none=[r['rf4_cblocked'],r['rf9base']]);s('force_y2',all=[r['y2sub'],p['rf2']]);s('force_lf4',all=[p['lf4'],p['rf3']]);s('force_up',any=[p['rf5'],r['force_y2'],r['force_lf4']]);s('ls_up',any=[p['lf2'],r['force_up']]);s('ls_down',any=[p['lf5'],p['lt6']],none=[r['force_up']]);s('ls_left',all=[p['lf3']],none=[p['lf1']]);s('ls_right',all=[p['lf1']],none=[p['lf3']]);s('direction_a',any=[p['lt6'],p['rf5']]);s('not_force',none=[r['force_up']]);s('rf3_suppress',all=[r['rf9base']],none=[r['c_any']]);s('digital_a',all=[p['rf1']],none=[r['y2sub']]);s('digital_b',all=[p['rf2']],none=[p['lf4'],r['y2sub']]);s('digital_y2b',all=[p['lt3'],p['rf3']],none=[p['lf4']]);s('digital_x',all=[r['base_rf3']],none=[r['rf3_suppress']]);s('digital_y2x',all=[r['y2sub'],p['rf1']],none=[r['c_any']]);s('digital_lf4x',all=[p['lf4'],p['rf2']],none=[r['c_any']]);s('null',all=[p['rf9']],none=[r['rf9base'],r['rf4_available']]);s('c_horizontal',any=[p['rt3'],p['rt4']]);s('c_vertical',any=[p['rt2'],p['rt5']]);s('c_diagonal',all=[r['c_horizontal'],r['c_vertical']]);s('rf3_vertical',all=[p['rf3'],r['c_vertical']],any=[r['ls_left'],r['ls_right']],none=[p['rt3'],p['rt4']]);s('rf6_down',all=[r['ls_down']],none=[r['ls_up']]);s('rf6_up',all=[r['ls_up']],none=[r['ls_down']])
    if policy=='clean_down_a':
        # Original physical A is independent of the post-SOCD direction signal.
        # Replace only the explicit clean composition; all other legacy family
        # equations remain data and can still be rebound independently.
        roles[(r['ls_down']&0xfff)-1]['any']=[p['lf5'],POST(options['down_input'])]
        roles[(r['ls_down']&0xfff)-1]['none']=[]
        roles[(r['ls_up']&0xfff)-1]['any']=[POST(options['up_input']),r['force_up']]
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
    if policy!='historical_compatibility':
        bindings.append((options['physical_input'],1,options.get('a_winner_table',255),0))
        if options.get('a_winner_table',255) not in (*range(28),255):raise ValueError('A winner filter')
    sources=[(1,r['ls_left'],r['ls_right'],r['ls_down'],r['ls_up']),(2,p['rt3'],p['rt4'],p['rt2'],p['rt5']),(3,0,0,r['not_force'],r['force_up']),(4,r['ls_left'],r['ls_right'],r['rf6_down'],r['rf6_up']),(5,r['ls_left'],r['ls_right'],p['rt2'],p['rt5']),(6,0,0,0,0),(7,0,0,p['rt2'],p['rt5'])]
    # Exact existing Stage C primitives; phase names appear only in this converter.
    act={'BASE_TABLE':TRUE,'DIRECTION_A':r['direction_a'],'RF6':p['rf6'],'RF7':p['rf7'],'RS_DIAGONAL':r['c_diagonal'],'RF3_VERTICAL':r['rf3_vertical'],'NULL':r['null'],'TRIGGERS':TRUE,'DPAD':p['rf13']}
    priority={'BASE_TABLE':200,'DIRECTION_A':80,'RF6':60,'RF7':40,'RS_DIAGONAL':100,'RF3_VERTICAL':80,'NULL':10,'TRIGGERS':200,'DPAD':20}
    effects=[];mask=(TRUE,0,0,0);effect_correspondence=[]
    for legacy_effect_index,e in enumerate(c['outputProgram']['effects']):
     phase=e['phase'].removeprefix('ULTIMATE_OUTPUT_PHASE_');target=e['target'].removeprefix('ULTIMATE_OUTPUT_TARGET_')
     if phase=='DIGITAL':
      mask=(tok(e['gateToken']) if e.get('gateToken') else TRUE,e.get('digitalSetMask',0),e.get('digitalClearMask',0),int(bool(e.get('gateToken') and e.get('gateInverted'))))
      effect_correspondence.append({'legacy_index':legacy_effect_index,'phase':phase,'target':target,'literal_legacy_effect':copy.deepcopy(e),'native_effect_index':None,'native_section':'digital_post_mask','omission':None});continue
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
     emitted=not e.get('suppress',False) and (phase!='DPAD' or dpad_flags&2)
     effect_correspondence.append({'legacy_index':legacy_effect_index,'phase':phase,'target':target,'literal_legacy_effect':copy.deepcopy(e),'native_effect_index':len(effects) if emitted else None,'omission':None if emitted else 'suppressed or Dpad analogue-center flag disabled'})
     if emitted:effects.append((t,priority[phase],gate,extra,source,mode,e.get('tableId',0),e.get('modeTableId',0),bytes(data),255,flags))
    if policy=='forced_table_down_a':
        if options['table_priority'] in [x[0] for x in rules]:raise ValueError('forced table priority collision')
        rules.append((options['table_priority'],options['table_id'],options['physical_input']))
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
    validate_native_body(body)
    assert profile_message.SerializeToString(deterministic=True)==original
    assert context.SerializeToString(deterministic=True)==context_original
    files=['src/modes/Ultimate.cpp','include/modes/UltimateProfileEvaluator.hpp','schema/haybox/config.proto','schema/haybox/config.options']
    metadata={'schema':5,'encoding':1,'engine_abi':1,'policy':policy,'policy_options':options,'source_schema':version,
      'legacy_payload_sha256':hashlib.sha256(original).hexdigest(),'native_payload_sha256':hashlib.sha256(wire).hexdigest(),
      'body_sha256':hashlib.sha256(body).hexdigest(),'preprocessing_sha256':context_digest.hex(),
      'preprocessing':MessageToDict(context),'preprocessing_canonical_hex':preprocessing_bytes(context,pb).hex(),
      'conversion_source_sha256':source_digest.hex(),'source_files':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
      'old_role_id_to_native_token':user_id_map,'counts':{'conditions':len(roles),'tokens':tokens,'bindings':len(bindings),'effects':len(effects),'tables':28},
      'correspondence':('Historical source compatibility including LT6 post-table override, V2 selection-only routing and V3 exactly-once routing; all 18 source families.' if policy=='historical_compatibility' else 'Explicit clean composition; historical LT6 intrinsic down/A removed; original physical A is independent. Genuine clean_down_a reads the requested post-SOCD direction; forced_table_down_a only gates ordinary table selection and adds no direction. This is intentionally not historical LT6 parity.'),
      'limitations':['Raw controller outputs only; no gameplay semantics or hardware acceptance.','Nunchuk physical acceptance NOT_TESTED.']}
    family_names=['LS direction references','RS direction references','default and Mode nine-way tables',
      'X1 X2 Y1 Y2 modifiers','Tilt1 Tilt2 Tilt3 and minus41','Mode and normal/flipper/LF4 sublayers',
      'deterministic table selection','A B X Y Z digital terms','L/R digital carriers and trigger effects',
      'independent multiple-output and OR composition','clean genuine Down+A','clean forced-table+A',
      'historical LT6 post-table override','RF5 RF6 RF7 compounds','RS diagonal and RF3 vertical transforms',
      'Dpad route/bypass/digital flags and Nunchuk tail','both-stick null','all28 literal raw/asymmetric/noncenter tables']
    phases_by_family={9:['TRIGGERS'],13:['DIRECTION_A'],14:['RF6','RF7'],15:['RS_DIAGONAL','RF3_VERTICAL'],16:['DPAD'],17:['NULL']}
    families=[]
    for number,name in enumerate(family_names,1):
        families.append({'family':number,'name':name,'native_source_ids':[1] if number==1 else [2] if number==2 else [3,4,5,6,7] if number in (13,14,15) else [],
          'native_effect_indexes':[x['native_effect_index'] for x in effect_correspondence if x['phase'] in phases_by_family.get(number,[]) and x['native_effect_index'] is not None],
          'table_ids':list(range(28)) if number in (3,4,5,6,7,18) else [],
          'digital_binding_indexes':list(range(len(bindings))) if number in (8,9,10,11,12,13,14) else [],
          'condition_tokens':copy.deepcopy(r) if number in (1,2,4,5,6,7,8,13,14,15,16,17) else {},
          'policy_state':policy if number in (11,12,13) else 'literal native data/source compatibility'})
    metadata['correspondence_report']={
      'families':families,'intrinsic_input_tokens':p,'conditions':roles,
      'source_selector_basis':'actual legacy profile rules' if version>=2 else 'frozen source-selector equations/fixture',
      'source_selector_roles':copy.deepcopy(b['roles']),'source_selector_rules':copy.deepcopy(b['tableRules']),
      'legacy_role_mapping':[{'legacy_role_id':x.role_id,'native_condition_token':user_id_map[x.role_id],
                              'legacy_condition':MessageToDict(x.condition)} for x in sorted(profile_message.roles,key=lambda x:x.role_id)],
      'table_mapping':[{'legacy_table_id':t.table_id,'native_table_id':t.table_id,'body_offset':96+18*t.table_id,
                        'native_coordinates':next(x['coordinates'] for x in profile['tables'] if x.get('tableId',0)==t.table_id)} for t in profile_message.tables],
      'rules':[{'native_index':i,'priority':priority,'table_id':table,'condition_token':gate,
                'legacy_index':i if i<len(b['tableRules']) else None} for i,(priority,table,gate) in enumerate(rules)],
      'digital_bindings':[{'index':i,'gate':gate,'digital_mask':mask_bits,'winner_table':winner,'flags':flags} for i,(gate,mask_bits,winner,flags) in enumerate(bindings)],
      'direction_sources':[{'id':x[0],'left':x[1],'right':x[2],'down':x[3],'up':x[4]} for x in sources],
      'effects':effect_correspondence,
      'native_effect_records':[{'index':i,'target':x[0],'priority':x[1],'activation':x[2],'profile_gate':x[3],'source':x[4],'coordinate_mode':x[5],'table0':x[6],'table1':x[7],'coordinate_union':list(x[8]),'winner':x[9],'flags':x[10]} for i,x in enumerate(effects)],
      'digital_post_mask':{'gate':mask[0],'set':mask[1],'clear':mask[2],'inverted':mask[3]},
      'dpad':{'flags':dpad_flags,'gate':dpad_gate}}
    metadata['policy_deviations']=[]
    if policy!='historical_compatibility':
        metadata['policy_deviations'].append({'legacy_LT6_intrinsic_down_and_A_removed':True,
          'independent_original_physical_A':options['physical_input'],'winner_filter':options.get('a_winner_table',255),
          'digital_post_mask_still_applies':True})
    if policy=='clean_down_a':
        metadata['policy_deviations'].append({'post_SOCD_down_input':options['down_input'],'post_SOCD_up_input':options['up_input'],
          'changed_native_conditions':[r['ls_down'],r['ls_up']],'preprocessing_changed':False})
    if policy=='forced_table_down_a':
        original_table=next(t for t in profile_message.tables if t.table_id==options['table_id'])
        metadata['policy_deviations'].append({'forced_table_id':options['table_id'],
          'old_coordinates':[{'x':point.x,'y':point.y} for point in original_table.coordinates],
          'new_coordinates':[{'x':options['forced_x'],'y':options['forced_y']} for _ in range(9)],
          'existing_rule_indexes_referencing_table':[i for i,x in enumerate(b['tableRules']) if x.get('tableId',0)==options['table_id']],
          'existing_effects_referencing_table':[i for i,e in enumerate(c['outputProgram']['effects']) if e.get('tableId',0)==options['table_id'] or e.get('modeTableId',0)==options['table_id'] or e.get('coordinateMode')=='ULTIMATE_COORDINATE_SELECTED_TABLE'],
          'added_native_rule_index':len(rules)-1,'added_analogue_effects':0,'added_direction_contribution':False,'preprocessing_changed':False})
    metadata['protobuf_descriptor_sha256']=hashlib.sha256(pb.DESCRIPTOR.serialized_pb).hexdigest()
    metadata['legacy_oracle_manifest_sha256']=hashlib.sha256((ROOT/'docs/runtime_config/profile_native_ultimate/legacy_oracle_hashes.json').read_bytes()).hexdigest()
    metadata['primitive_inputs_sha256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['tools/fixtures/stage_b_ultimate_profiles_fixture.json','tools/fixtures/stage_c_ultimate_profiles_fixture.json','.pio/libdeps/glyph_mk6/Nanopb/pb.h','.pio/libdeps/glyph_mk6/Nanopb/generator/nanopb_generator.py']}
    return native,metadata


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True,help='Complete Config JSON or protobuf input (never modified)')
    parser.add_argument('--profile-index',type=int,default=0)
    parser.add_argument('--mode-index',type=int,required=True)
    parser.add_argument('--policy',choices=['historical_compatibility','clean_down_a','forced_table_down_a'],required=True)
    parser.add_argument('--policy-options',type=Path,help='Explicit clean input IDs/forced raw values and priorities JSON')
    parser.add_argument('--output',type=Path,required=True,help='New output package directory')
    a=parser.parse_args()
    import glyph_serial_config_tool as writer
    pb,jf,_=writer.load_runtime_proto_modules(ROOT)
    config=pb.Config()
    if a.input.suffix=='.json':jf.Parse(a.input.read_text(),config)
    else:
        raw=a.input.read_bytes()
        for tag,wire,value in raw_fields(raw):
            if tag==201:
                if wire!=2:raise ValueError('invalid embedded profile field')
                validate_profile_wire(value)
        config.ParseFromString(raw)
    native,metadata=convert(config.ultimate_profiles[a.profile_index],config.game_mode_configs[a.mode_index],pb,a.policy,options=json.loads(a.policy_options.read_text()) if a.policy_options else None)
    metadata['input_file_sha256']=hashlib.sha256(a.input.read_bytes()).hexdigest()
    a.output.mkdir(parents=True,exist_ok=False)
    (a.output/'profile.pb').write_bytes(native.SerializeToString(deterministic=True))
    (a.output/'profile.json').write_text(jf.MessageToJson(native)+'\n')
    (a.output/'conversion.json').write_text(json.dumps(metadata,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'output':str(a.output),'body_bytes':len(native.native_payload),'payload_sha256':metadata['native_payload_sha256'],'device_access':False}))
    return 0

if __name__=='__main__':raise SystemExit(main())
