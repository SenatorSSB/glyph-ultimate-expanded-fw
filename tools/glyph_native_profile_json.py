#!/usr/bin/env python3
"""Offline, finite human JSON codec for schema-5 GNP5/ABI1. Never opens a device."""
from __future__ import annotations
import argparse, base64, copy, hashlib, json, re, struct
from pathlib import Path
from types import SimpleNamespace
try:
    from convert_glyph_native_ultimate_profile import validate_native_body, preprocessing_bytes, raw_fields
    from extract_glyph_identity_runtime_tables import runtime_table_id_names
except ModuleNotFoundError:
    from tools.convert_glyph_native_ultimate_profile import validate_native_body, preprocessing_bytes, raw_fields
    from tools.extract_glyph_identity_runtime_tables import runtime_table_id_names
ROOT=Path(__file__).resolve().parents[1]
SCHEMA_PATH=ROOT/'profiles/ultimate/Ultimate.profile.schema.json'
V1_SCHEMA_PATH=ROOT/'profiles/schema/glyph-native-ultimate-profile.v1.schema.json'
AUTHORING_V1_DOMAIN=b'Glyph.Native.Authoring.v1\0'
TABLES=tuple(runtime_table_id_names())
INPUTS=tuple(f'{p}{i}' for p,n in [('LF',16),('RF',16),('LT',8),('RT',8),('MB',12)] for i in range(1,n+1))
# include/core/state.hpp OutputState bits 0..11; friendly A/B/X/Y names are
# explicit aliases of a/b/x/y. buttonR (bit5) differs from triggerRDigital (bit7).
OUTPUTS=('buttonA','buttonB','buttonX','buttonY','buttonL','buttonR','triggerLDigital','triggerRDigital','start','select','home','capture')
DIRECTIONS=('leftStickLeft','leftStickRight','leftStickDown','leftStickUp','rightStickLeft','rightStickRight','rightStickDown','rightStickUp')
POLICIES=('unspecified','neutral','secondInputPriority','secondInputPriorityNoReactivation','firstPriority','secondPriority')
PROTO_POLICIES=('SOCD_UNSPECIFIED','SOCD_NEUTRAL','SOCD_2IP','SOCD_2IP_NO_REAC','SOCD_DIR1_PRIORITY','SOCD_DIR2_PRIORITY')
TARGETS=('leftStick','rightStick','triggerL','triggerR','bothSticks')
NAME_PATTERN=r'^[A-Za-z][A-Za-z0-9_-]{0,63}$'

def _require(ok,message):
    if not ok:raise ValueError(message)

def _pairs(pairs):
    result={}
    for key,value in pairs:
        _require(key not in result,'duplicate JSON key: '+key);result[key]=value
    return result

def dump_profile(profile):
    """Readable JSON with each raw coordinate pair kept on one line."""
    text=json.dumps(profile,indent=2,ensure_ascii=False)
    return re.sub(r'\[\n\s+(\d+),\n\s+(\d+)\n\s+\]',r'[\1, \2]',text)+'\n'

def load_json(path):
    return json.loads(Path(path).read_text(),object_pairs_hook=_pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('invalid JSON constant '+x)))

def _schema_check(value,schema,path='$'):
    """Dependency-free evaluator for the exact finite keywords in our schema."""
    if 'oneOf' in schema:
        matches=0
        for alt in schema['oneOf']:
            try:_schema_check(value,alt,path);matches+=1
            except ValueError:pass
        _require(matches==1,path+': expected one permitted shape');return
    if 'const' in schema:_require(type(value) is type(schema['const']) and value==schema['const'],path+': invalid constant')
    if 'enum' in schema:_require(value in schema['enum'],path+': unknown symbol')
    kind=schema.get('type');types={'object':dict,'array':list,'string':str,'integer':int,'boolean':bool,'null':type(None)}
    if kind:_require(type(value) is types[kind],path+': expected '+kind)
    if kind=='object':
        props=schema.get('properties',{});patterns=schema.get('patternProperties',{})
        _require(schema.get('minProperties',0)<=len(value)<=schema.get('maxProperties',len(value)),path+': invalid property count')
        _require(set(schema.get('required',[]))<=value.keys(),path+': missing required fields')
        for k,v in value.items():
            matching=[sub for pattern,sub in patterns.items() if re.search(pattern,k) is not None]
            if schema.get('additionalProperties') is False:_require(k in props or matching,path+': unknown field '+k)
            if k in props:_schema_check(v,props[k],path+'.'+k)
            for sub in matching:_schema_check(v,sub,path+'.'+k)
    if kind=='array':
        _require(schema.get('minItems',0)<=len(value)<=schema.get('maxItems',len(value)),path+': invalid length')
        if schema.get('uniqueItems'):_require(len({json.dumps(x,sort_keys=True) for x in value})==len(value),path+': duplicate items')
        for i,v in enumerate(value):_schema_check(v,schema['items'],f'{path}[{i}]')
    if kind=='integer':_require(schema.get('minimum',value)<=value<=schema.get('maximum',value),path+': integer out of range')
    if kind=='string':
        _require(schema.get('minLength',0)<=len(value)<=schema.get('maxLength',len(value)),path+': invalid string length')
        if 'pattern' in schema:_require(re.fullmatch(schema['pattern'],value) is not None,path+': invalid symbol syntax')

def _context(context):
    """Normalize human context or strict preprocessing-only protobuf JSON."""
    _require(type(context) is dict,'preprocessing must be object')
    if 'mode' in context:result=copy.deepcopy(context)
    else:
        _require(context.keys()<={'modeId','buttonRemapping','socdPairs','mode_id','button_remapping','socd_pairs'},'unknown preprocessing context fields')
        def field(o,a,b,default=None):
            _require(not(a in o and b in o),'duplicate preprocessing aliases');return o.get(a,o.get(b,default))
        mode=field(context,'modeId','mode_id')
        _require(type(mode) is int and mode==3 or mode=='MODE_ULTIMATE','context must be MODE_ULTIMATE')
        def button(v):
            if type(v) is int:
                _require(0<=v<=60,'input ID out of range');return INPUTS[v-1] if v else 'none'
            _require(type(v) is str,'invalid input symbol')
            return 'none' if v=='BTN_UNSPECIFIED' else v.removeprefix('BTN_')
        result={'mode':'MODE_ULTIMATE','remaps':[],'socd':[]}
        remaps=field(context,'buttonRemapping','button_remapping',[]);pairs=field(context,'socdPairs','socd_pairs',[])
        _require(type(remaps) is list and type(pairs) is list,'preprocessing entries must be arrays')
        for r in remaps:
            _require(type(r) is dict and r.keys()<={'physicalButton','physical_button','activates'},'invalid remap fields')
            result['remaps'].append({'physical':button(field(r,'physicalButton','physical_button')),'activates':button(r.get('activates',0))})
        for p in pairs:
            _require(type(p) is dict and p.keys()<={'buttonDir1','button_dir1','buttonDir2','button_dir2','socdType','socd_type'},'invalid SOCD fields')
            policy=field(p,'socdType','socd_type',0)
            if type(policy) is str:
                _require(policy in PROTO_POLICIES,'unknown SOCD policy');policy=PROTO_POLICIES.index(policy)
            _require(type(policy) is int and 0<=policy<=5,'SOCD policy out of range')
            result['socd'].append({'first':button(field(p,'buttonDir1','button_dir1')),'second':button(field(p,'buttonDir2','button_dir2')),'policy':POLICIES[policy]})
    _schema_check(result,load_json(SCHEMA_PATH)['properties']['preprocessing'],'$.preprocessing');return result

def context_bytes(context):
    c=_context(context)
    ctx=SimpleNamespace(mode_id=3,button_remapping=[SimpleNamespace(physical_button=INPUTS.index(r['physical'])+1,activates=0 if r['activates']=='none' else INPUTS.index(r['activates'])+1) for r in c['remaps']],socd_pairs=[SimpleNamespace(button_dir1=INPUTS.index(s['first'])+1,button_dir2=INPUTS.index(s['second'])+1,socd_type=POLICIES.index(s['policy'])) for s in c['socd']])
    return preprocessing_bytes(ctx,SimpleNamespace(MODE_ULTIMATE=3))

def _varint(n):
    out=bytearray()
    while n>127:out.append((n&127)|128);n>>=7
    out.append(n);return bytes(out)

def wrap_body(body):
    validate_native_body(body);return b'\x08\x05\x42'+_varint(len(body))+body

def unwrap_profile(data):
    if type(data) is dict:
        if 'response' in data:
            _require(data.keys()=={'response'} and type(data['response']) is dict,'expected closed read-result envelope')
            data=data['response']
            # The supported offline READ export is deliberately finite. Session
            # metadata is checked then discarded; it cannot enter human source.
            fields=('protocol_version','request_token','status','store_generation',
                    'profile_id','profile_revision','profile','config_generation',
                    'mutation_protocol_version','store_incarnation','diagnostic')
            aliases={}
            for key in fields:
                parts=key.split('_');camel=parts[0]+''.join(x.title() for x in parts[1:])
                aliases[key]=key;aliases[camel]=key
            _require(data.keys()<=aliases.keys(),'unknown read-result fields')
            normalized={}
            for key,value in data.items():
                dest=aliases[key];_require(dest not in normalized,'duplicate read-result aliases');normalized[dest]=value
            status=normalized.get('status')
            _require(status=='PROFILE_STORE_OK' or type(status) is int and status==1,'read-result status must be PROFILE_STORE_OK')
            for key,value in normalized.items():
                if key in ('status','profile'):continue
                if key=='diagnostic':_require(type(value) is str,'invalid read-result diagnostic');continue
                bits=64 if key in ('request_token','store_generation','profile_revision','config_generation') else 32
                if bits==64 and type(value) is str:
                    _require(re.fullmatch(r'0|[1-9][0-9]*',value) is not None,'invalid read-result integer');value=int(value)
                _require(type(value) is int and 0<=value<(1<<bits),'invalid read-result integer')
            _require('profile' in normalized,'read-result profile missing');data=normalized['profile']
        elif 'profile' in data:
            _require(data.keys()=={'profile'},'unknown profile envelope fields');data=data['profile']
        _require(type(data) is dict,'profile must be object')
        aliases={'schemaVersion':'schemaVersion','schema_version':'schemaVersion','nativePayload':'nativePayload','native_payload':'nativePayload'}
        _require(data.keys()<=aliases.keys(),'unknown schema5 protobuf JSON fields')
        normalized={}
        for key,value in data.items():
            dest=aliases[key];_require(dest not in normalized,'duplicate protobuf JSON aliases');normalized[dest]=value
        _require(normalized.keys()=={'schemaVersion','nativePayload'},'expected closed schema5 protobuf JSON wrapper');data=normalized
        _require(type(data['schemaVersion']) is int and data['schemaVersion']==5,'expected schema5')
        _require(type(data['nativePayload']) is str,'nativePayload must be base64')
        try:body=base64.b64decode(data['nativePayload'],validate=True)
        except Exception as exc:raise ValueError('invalid nativePayload base64') from exc
        _require(base64.b64encode(body).decode()==data['nativePayload'],'noncanonical base64')
        validate_native_body(body);return body
    _require(type(data) is bytes,'profile must be bytes or protobuf JSON')
    fields=list(raw_fields(data))
    _require(len(fields)==2 and fields[0]==(1,0,5) and fields[1][:2]==(8,2),'noncanonical/unknown schema5 wrapper fields')
    body=fields[1][2];_require(wrap_body(body)==data,'noncanonical protobuf encoding');return body

def _mask(names):return sum(1<<OUTPUTS.index(n) for n in names)
def _outputs(mask):return [n for i,n in enumerate(OUTPUTS) if mask&(1<<i)]

def _profile_version(profile):
    _require(type(profile) is dict,'profile must be object')
    version=profile.get('formatVersion')
    _require(type(version) is int and version in (0,1),'unsupported formatVersion')
    return version

def _authored_source_v1_sha256(profile):
    semantic={k:v for k,v in profile.items() if k not in ('provenance','metadata','name')}
    canonical=json.dumps(semantic,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
    return hashlib.sha256(AUTHORING_V1_DOMAIN+canonical).digest()

def compile_profile(profile):
    version=_profile_version(profile)
    _schema_check(profile,load_json(V1_SCHEMA_PATH if version==1 else SCHEMA_PATH))
    if version==1:
        slots={name:t['slot'] for name,t in profile['tables'].items()}
        _require('any' not in slots,'table name any is reserved')
        _require(len(set(slots.values()))==len(slots),'duplicate table slots')
    else:slots={name:i for i,name in enumerate(TABLES)}
    conditions=profile['conditions'];sources=profile['directionSources'];cn=[c['name'] for c in conditions];sn=[s['name'] for s in sources]
    _require(len(set(cn))==len(cn),'duplicate condition names');_require(len(set(sn))==len(sn),'duplicate source names')
    early=sum(c['stage']=='early' for c in conditions)
    _require(all(c['stage']=='early' for c in conditions[:early]),'early conditions must precede late conditions')
    def token(t):
        if t in ('false','true'):return 0 if t=='false' else 65535
        kind,name=t.split(':',1)
        if kind in ('original','preSocd','postSocd'):return ('original','preSocd','postSocd').index(kind)*4096+INPUTS.index(name)+1
        if kind=='condition':
            _require(name in cn,'unknown condition '+name);return 0x3001+cn.index(name)
        if kind=='direction':return 0x4001+DIRECTIONS.index(name)
        if kind=='finalDigital':return 0x5001+OUTPUTS.index(name)
        raise ValueError('unknown token '+t)
    def source(name):
        _require(name in sn,'unknown direction source '+name);return sn.index(name)+1
    def table(name,*,winner=False):
        if version==0:return 255 if name=='any' else TABLES.index(name)
        if winner and name=='any':return 255
        _require(name in slots,'unknown table '+str(name))
        return slots[name]
    header=bytearray(96);header[:4]=b'GNP5';struct.pack_into('<HH',header,4,1,1)
    header[10:20]=bytes([len(conditions),early,len(sources),len(profile['tableRules']),len(profile['digitalBindings']),len(profile['analogEffects']),table(profile['defaultTable']),source(profile['leftStickSource']),source(profile['rightStickSource']),sum(1<<i for i,k in enumerate(('routeToDpad','bypassLeftStick','suppressLeftStickDigital')) if profile['dpad'][k])])
    struct.pack_into('<HHHH',header,20,*(token(profile['gates'][k]) for k in ('mode','leftStickDigital','rightStickDigital','dpad')))
    header[28:60]=hashlib.sha256(context_bytes(profile['preprocessing'])).digest();header[60:92]=_authored_source_v1_sha256(profile) if version==1 else bytes.fromhex(profile['provenance']['sha256']);body=bytearray()
    if version==0:
        for i,name in enumerate(TABLES):
            t=profile['tables'][name];_require(t['id']==i,'table ID/name mismatch: '+name);body+=bytes(v for d in range(1,10) for v in t['directions'][str(d)])
    else:
        body=bytearray([128])*(28*18)
        for name,t in profile['tables'].items():
            slot=slots[name];body[slot*18:(slot+1)*18]=bytes(v for d in range(1,10) for v in t['directions'][str(d)])
    pool=[]
    for i,c in enumerate(conditions):
        body+=struct.pack('<BH',i+1,len(c['all'])|len(c['any'])<<2|len(c['none'])<<5);pool.extend(token(t) for k in ('all','any','none') for t in c[k])
    _require(len(pool)<=768,'condition token pool exceeds 768');struct.pack_into('<H',header,92,len(pool));body+=b''.join(struct.pack('<H',t) for t in pool)
    for i,s in enumerate(sources):body+=struct.pack('<BHHHH',i+1,*(token(s[k]) for k in ('left','right','down','up')))
    for r in profile['tableRules']:body+=struct.pack('<BBH',r['priority'],table(r['table']),token(r['when']))
    for b in profile['digitalBindings']:body+=struct.pack('<HHBB',token(b['when']),_mask(b['outputs']),table(b['winnerTable'],winner=True),0)
    for e in profile['analogEffects']:
        target=TARGETS.index(e['target'])+1;data=bytes(18);s=mode=t0=t1=0
        if target in (3,4):data=bytes([e['value']])+bytes(17)
        else:
            s=source(e['source']);c=e['coordinates'];mode=('selectedTable','table','fixed','inline').index(c['mode'])+1
            if mode==2:t0=table(c['normalTable']);t1=table(c['modeTable'])
            if mode==3:data=bytes(c['point'])+bytes(16)
            if mode==4:data=bytes(v for p in c['points'] for v in p)
        body+=struct.pack('<BBHHBBBB18sBBH',target,e['priority'],token(e['activation']),token(e['gate']),s,mode,t0,t1,data,table(e['winnerTable'],winner=True),int(e['gateInverted'])|int(e['skipWhenDpadBypass'])<<1,0)
    m=profile['digitalPostMask'];body+=struct.pack('<HHHH',token(m['gate']),_mask(m['set']),_mask(m['clear']),int(m['inverted']))
    body=header+body;_require(len(body)<=3336,'native body capacity exceeded');struct.pack_into('<H',body,8,len(body));return wrap_body(bytes(body))

def profile_to_protobuf_json(profile):return {'schemaVersion':5,'nativePayload':base64.b64encode(unwrap_profile(compile_profile(profile))).decode()}
def validate_profile(profile):
    wire=compile_profile(profile);body=unwrap_profile(wire)
    return {**validate_native_body(body),'profile_sha256':hashlib.sha256(wire).hexdigest(),'body_sha256':hashlib.sha256(body).hexdigest(),'preprocessing_sha256':body[28:60].hex()}

def compile_report(profile):
    """Compile and report exact offline source/wire correspondence; no device access."""
    wire=compile_profile(profile);body=unwrap_profile(wire)
    version=profile['formatVersion']
    slots={name:t['slot'] if version==1 else t['id'] for name,t in profile['tables'].items()}
    return {'profile_name':profile['name'],'format_version':version,
            'declared_tables':sorted(slots),'table_slots':dict(sorted(slots.items())),
            'neutral_filled_slots':[i for i in range(28) if i not in slots.values()],
            'condition_count':body[10],'token_count':struct.unpack_from('<H',body,92)[0],
            'direction_source_count':body[12],'table_rule_count':body[13],
            'digital_binding_count':body[14],'analog_effect_count':body[15],
            'body_bytes':len(body),'wrapper_bytes':len(wire),
            'preprocessing_sha256':body[28:60].hex(),'provenance_sha256':body[60:92].hex(),
            'provenance_kind':profile['provenance']['kind'],
            'body_sha256':hashlib.sha256(body).hexdigest(),'wrapper_sha256':hashlib.sha256(wire).hexdigest()}

def decode_profile(data,preprocessing,*,correspondence=None,name='Ultimate'):
    """Decode to archival v0 wire labels, never recover lost v1 source names."""
    body=unwrap_profile(data);context=_context(preprocessing);_require(hashlib.sha256(context_bytes(context)).digest()==body[28:60],'preprocessing context digest mismatch')
    u16=lambda at:struct.unpack_from('<H',body,at)[0]
    count,early,ns,nr,nb,ne=body[10:16];names=[f'condition{i+1:02d}' for i in range(count)]
    if correspondence is not None:
        _require(type(correspondence) is dict and correspondence.get('body_sha256')==hashlib.sha256(body).hexdigest(),'correspondence does not bind exact body')
        seen={}
        for f in correspondence.get('correspondence_report',{}).get('families',[]):
            for n,t in f.get('condition_tokens',{}).items():
                _require(type(t) is int and 0x3001<=t<=0x3000+count,'invalid correspondence condition token');_require(re.fullmatch(NAME_PATTERN,n) is not None,'invalid correspondence name');_require(t not in seen or seen[t]==n,'conflicting correspondence names');seen[t]=n
        report=correspondence.get('correspondence_report',{})
        for row in report.get('legacy_role_mapping',[]):
            t=row.get('native_condition_token');legacy=row.get('legacy_role_id')
            _require(type(t) is int and 0x3001<=t<=0x3000+count and type(legacy) is int and 1<=legacy<=32,'invalid legacy condition correspondence')
            if t not in seen:seen[t]=f'legacyRole{legacy:02d}'
        rule_offset=600+count*3+u16(92)*2+ns*9
        for row in report.get('rules',[]):
            i=row.get('native_index');t=row.get('condition_token')
            _require(type(i) is int and 0<=i<nr and t==u16(rule_offset+4*i+2),'invalid table rule correspondence')
            if t and 0x3001<=t<=0x3000+count and t not in seen:seen[t]=f'tableRuleGate{i:02d}'
        for t,n in seen.items():names[t-0x3001]=n
        _require(len(set(names))==len(names),'duplicate correspondence names')
    sn=[f'source{i+1}' for i in range(ns)]
    def tok(t):
        if t in (0,65535):return 'false' if t==0 else 'true'
        kind=t>>12;idx=(t&4095)-1
        if kind<=2:return ('original','preSocd','postSocd')[kind]+':'+INPUTS[idx]
        if kind==3:return 'condition:'+names[idx]
        if kind==4:return 'direction:'+DIRECTIONS[idx]
        return 'finalDigital:'+OUTPUTS[idx]
    tab=lambda n:'any' if n==255 else TABLES[n]
    result={'format':'glyph-native-ultimate-profile','formatVersion':0,'name':name,'provenance':{'kind':'preservedConversionSourceSha256','sha256':body[60:92].hex()},'preprocessing':context,'tables':{n:{'id':i,'directions':{str(j+1):list(body[96+i*18+j*2:98+i*18+j*2]) for j in range(9)}} for i,n in enumerate(TABLES)},'defaultTable':tab(body[16]),'leftStickSource':sn[body[17]-1],'rightStickSource':sn[body[18]-1],'gates':{k:tok(u16(20+2*i)) for i,k in enumerate(('mode','leftStickDigital','rightStickDigital','dpad'))},'dpad':{k:bool(body[19]&(1<<i)) for i,k in enumerate(('routeToDpad','bypassLeftStick','suppressLeftStickDigital'))},'conditions':[],'directionSources':[],'tableRules':[],'digitalBindings':[],'analogEffects':[]}
    offset=600+3*count
    for i in range(count):
        packed=u16(601+3*i);counts=(packed&3,(packed>>2)&7,(packed>>5)&15);c={'name':names[i],'stage':'early' if i<early else 'late'}
        for k,n in zip(('all','any','none'),counts):c[k]=[tok(u16(offset+2*j)) for j in range(n)];offset+=2*n
        result['conditions'].append(c)
    for i in range(ns):result['directionSources'].append({'name':sn[i],**{k:tok(u16(offset+1+2*j)) for j,k in enumerate(('left','right','down','up'))}});offset+=9
    for _ in range(nr):result['tableRules'].append({'priority':body[offset],'table':tab(body[offset+1]),'when':tok(u16(offset+2))});offset+=4
    for _ in range(nb):result['digitalBindings'].append({'when':tok(u16(offset)),'outputs':_outputs(u16(offset+2)),'winnerTable':tab(body[offset+4])});offset+=6
    for _ in range(ne):
        p=body[offset:offset+32];target=p[0];e={'target':TARGETS[target-1],'priority':p[1],'activation':tok(u16(offset+2)),'gate':tok(u16(offset+4)),'gateInverted':bool(p[29]&1),'skipWhenDpadBypass':bool(p[29]&2),'winnerTable':tab(p[28])}
        if target in (3,4):e['value']=p[10]
        else:
            e['source']=sn[p[6]-1];mode=p[7];c={'mode':('selectedTable','table','fixed','inline')[mode-1]}
            if mode==2:c.update(normalTable=tab(p[8]),modeTable=tab(p[9]))
            if mode==3:c['point']=list(p[10:12])
            if mode==4:c['points']=[list(p[10+i*2:12+i*2]) for i in range(9)]
            e['coordinates']=c
        result['analogEffects'].append(e);offset+=32
    result['digitalPostMask']={'gate':tok(u16(offset)),'set':_outputs(u16(offset+2)),'clear':_outputs(u16(offset+4)),'inverted':bool(u16(offset+6))}
    _require(compile_profile(result)==wrap_body(body),'human decode did not preserve exact native program');return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    dec=sub.add_parser('decode');dec.add_argument('input',type=Path);dec.add_argument('--preprocessing',required=True,type=Path);dec.add_argument('--correspondence',type=Path);dec.add_argument('--name',default='Ultimate');dec.add_argument('--output',required=True,type=Path)
    comp=sub.add_parser('compile');comp.add_argument('input',type=Path);comp.add_argument('--output',required=True,type=Path);comp.add_argument('--format',choices=('pb','protobuf-json'),default='pb')
    val=sub.add_parser('validate');val.add_argument('input',type=Path)
    report=sub.add_parser('report');report.add_argument('input',type=Path);report.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        if args.command=='decode':
            raw=args.input.read_bytes();data=load_json(args.input) if raw.lstrip().startswith(b'{') else raw
            out=decode_profile(data,load_json(args.preprocessing),correspondence=load_json(args.correspondence) if args.correspondence else None,name=args.name);args.output.write_text(dump_profile(out))
        elif args.command=='compile':
            profile=load_json(args.input)
            if args.format=='pb':args.output.write_bytes(compile_profile(profile))
            else:args.output.write_text(json.dumps(profile_to_protobuf_json(profile),indent=2)+'\n')
        elif args.command=='report':
            text=json.dumps(compile_report(load_json(args.input)),indent=2,sort_keys=True)+'\n'
            if args.output:args.output.write_text(text,encoding='utf-8')
            else:print(text,end='')
        else:print(json.dumps(validate_profile(load_json(args.input)),sort_keys=True))
    except (OSError,ValueError,KeyError,IndexError,TypeError,struct.error) as exc:parser.exit(2,'error: '+str(exc)+'\n')
if __name__=='__main__':main()
