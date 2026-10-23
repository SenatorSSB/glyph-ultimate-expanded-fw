#!/usr/bin/env python3
"""Offline checks for the exact owner packet. No device/network/subprocess writer."""
import argparse, base64, hashlib, json, sys, zlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import glyph_serial_config_tool as transport
import glyph_profile_store_production_tool as production
from convert_glyph_native_ultimate_profile import preprocessing_bytes, validate_standalone_profile
from glyph_runtime_identity_tool import payload_digest
PB, JF, _ = transport.load_runtime_proto_modules(ROOT)
HERE = Path(__file__).resolve().parent
SEL = set(range(28, 48))
EXPECTED = {r['id']: r for r in json.loads((HERE / 'retained_profile_identities.json').read_text())['records']}
KAZUYA = PB.UltimateProfile()
JF.ParseDict(json.loads((HERE / 'Kazuya.protobuf.json').read_text()), KAZUYA)

def need(ok, reason):
    if not ok: raise ValueError(reason)

def sha(b): return hashlib.sha256(b).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def response(p):
    m = PB.ProfileStoreResponse(); JF.ParseDict(load(p)['response'], m, ignore_unknown_fields=False)
    need(m.protocol_version == 2 and m.mutation_protocol_version == 2 and m.status == PB.PROFILE_STORE_OK, 'nonproduction/non-OK response: '+str(p))
    return m

def status(p):
    s = response(p)
    production.verify_production_status(argparse.Namespace(action='status'), PB, s)
    need(s.store_incarnation > 0 and not s.recovery_flags and s.mutation_feasible, 'unhealthy/recovery/not feasible')
    need(s.store_generation < 0xffffffff and s.transaction_token_high_water < 0xfffffffffffffffe, 'generation/token exhausted')
    return s

def key(s): return (s.store_incarnation, s.store_generation, s.config_generation, s.transaction_token_high_water)

def config(p, s):
    raw = base64.b64decode(load(p)['rawConfigPayloadBase64'], validate=True)
    need(zlib.crc32(raw) == s.config_generation, 'Config raw CRC differs from current STATUS digest')
    c = PB.Config(); c.ParseFromString(raw)
    need(c.ultimate_profile_root_format == 2 and c.ultimate_profile_store_format == 1 and not c.ultimate_profiles, 'not admitted compact Config')
    need(c.ultimate_profile_store_incarnation == s.store_incarnation, 'Config incarnation mismatch')
    need(0 < len(c.game_mode_configs) <= 30 and 0 < len(c.communication_backend_configs) <= 15, 'Config extents')
    for b in c.communication_backend_configs:
        need(0 < b.default_mode_config <= len(c.game_mode_configs), 'backend default row invalid')
    need(0 < c.default_backend_config <= len(c.communication_backend_configs) and 0 < c.default_usb_backend_config <= len(c.communication_backend_configs), 'default backend invalid')
    return c, raw

def no_sel(c):
    need(not any(m.ultimate_profile_id in SEL for m in c.game_mode_configs), 'SEL still referenced by a Config row')

def directory(d, s):
    entries = {}; cursor = 0; visited = set()
    while True:
        need(cursor not in visited and len(visited) < 9, 'LIST cycle/extent'); visited.add(cursor)
        r = response(Path(d) / ('list-'+str(cursor)+'.json'))
        need((r.store_incarnation, r.store_generation, r.config_generation) == key(s)[:3], 'LIST fence drift')
        for e in r.entries:
            need(e.profile_id and e.profile_id not in entries, 'duplicate/zero directory ID')
            entries[e.profile_id] = {'id':e.profile_id, 'name':e.name, 'rank':e.display_rank, 'revision':e.revision, 'directory_payload_version':e.payload_version}
        cursor = r.next_page_cursor
        if not cursor: break
    need(0 < len(entries) <= 64, 'directory size')
    return entries

def record(d, ident, entry, s):
    r = response(Path(d) / ('read-'+str(ident)+'.json'))
    need((r.store_incarnation, r.store_generation, r.config_generation) == key(s)[:3], 'READ fence drift')
    need(r.profile_id == ident and r.profile_revision == entry['revision'] and ((r.profile.schema_version == 5) == (entry['directory_payload_version'] == 5)), 'READ/directory identity mismatch')
    validate_standalone_profile(r.profile, PB)
    out = dict(entry, schema=r.profile.schema_version, wrapper_sha256=sha(r.profile.SerializeToString(deterministic=True)), body_sha256=sha(r.profile.native_payload) if r.profile.schema_version == 5 else None)
    if out['schema'] == 5 and ident not in EXPECTED:
        need(entry['name']=='Kazuya' and out['wrapper_sha256']==sha(KAZUYA.SerializeToString(deterministic=True)), 'unexpected native character; reconcile packet before mutations')
    if ident in EXPECTED:
        e = EXPECTED[ident]
        for f in ['name','revision','schema','wrapper_sha256','body_sha256']: need(out[f] == e[f], 'golden/fixture mismatch ID'+str(ident)+' '+f)
        # Rank is a fresh metadata fact; preserve actual ranks, never substitute historical ranks.
    return out, r.profile

def audit(d, require_safe=False):
    d = Path(d); s = status(d/'status-start.json'); end = status(d/'status-end.json')
    identity=load(d/'identity.json')
    need(identity.get('context')=='configurator' and identity.get('status')=='configurator' and identity.get('primary_backend')==8,'normal Configurator identity not established')
    need(key(s) == key(end), 'snapshot STATUS drift')
    c, raw = config(d/'config.json', s); entries = directory(d, s); records = {}; profiles = {}
    for ident, entry in entries.items(): records[str(ident)], profiles[ident] = record(d, ident, entry, s)
    need(27 in profiles, 'Ultimate absent')
    for m in c.game_mode_configs:
        if m.ultimate_profile_id:
            need(m.mode_id == PB.MODE_ULTIMATE and m.ultimate_profile_id in profiles, 'dangling/wrong-mode stable reference')
        if m.ultimate_profile_engine == 1:
            need(m.ultimate_profile_id in profiles and profiles[m.ultimate_profile_id].schema_version == 5, 'native template not schema5')
            need(sha(preprocessing_bytes(m, PB)) == profiles[m.ultimate_profile_id].native_payload[28:60].hex(), 'native preprocessing mismatch')
    if require_safe: no_sel(c)
    return {'incarnation':s.store_incarnation, 'generation':s.store_generation, 'config_generation':s.config_generation, 'high_water':s.transaction_token_high_water, 'records':records, 'config_raw_sha256':sha(raw)}, c

def snapshot(d): return load(Path(d)/'snapshot.json')
def parsed_config(d):
    s = status(Path(d)/'status-end.json'); return config(Path(d)/'config.json', s)[0]
def equal_config(a,b): need(a.SerializeToString(deterministic=True) == b.SerializeToString(deterministic=True), 'unexpected Config field changes')
def request_receipt(p):
    x = load(p); raw = bytes.fromhex(x['request_hex']); need(sha(raw) == x['request_sha256'], 'receipt payload hash')
    q = PB.ProfileStoreRequest(); q.ParseFromString(raw); need(q.protocol_version == 2, 'receipt protocol')
    return q

def mutation(before, after, receipt, result, operation, ident=None, store_delta=0):
    q = request_receipt(receipt); r = response(result)
    need(q.operation == operation and q.expected_store_incarnation == before['incarnation'] and q.expected_store_generation == before['generation'], 'request fences/operation mismatch')
    need(before['high_water'] < q.request_token < 0xffffffffffffffff, 'request token stale/exhausted')
    need(r.request_token == q.request_token and r.store_incarnation == before['incarnation'] and r.store_generation == before['generation']+store_delta, 'response token/incarnation/generation mismatch')
    need(after['incarnation'] == before['incarnation'] and after['generation'] == before['generation']+store_delta and after['high_water'] == q.request_token, 'post-operation status/accounting mismatch')
    if ident is not None: need(q.profile_id == ident and r.profile_id == ident, 'returned/requested ID mismatch')
    return q,r

def compare(a,b,kind,receipt=None,result=None,mode=None,backend=2):
    x,y = snapshot(a),snapshot(b); ca,cb = parsed_config(a),parsed_config(b)
    need(x['incarnation'] == y['incarnation'], 'incarnation changed')
    if kind == 'preserve':
        need(x == y, 'Config/store/status preservation differs')
    elif kind == 'reference':
        q,r = mutation(x,y,receipt,result,PB.PROFILE_STORE_SET_MODE_REFERENCE,27)
        need(x['records'] == y['records'] and q.expected_config_generation == x['config_generation'], 'reference changed store or wrong Config fence')
        need(q.mode_config_index < len(ca.game_mode_configs), 'reference row out of range'); m = ca.game_mode_configs[q.mode_config_index]
        need(m.mode_id == PB.MODE_ULTIMATE and m.ultimate_profile_engine == 1 and m.ultimate_profile_id in SEL, 'reference source not verified native SEL context')
        need(sha(preprocessing_bytes(m,PB)) == KAZUYA.native_payload[28:60].hex(), 'reference preprocessing mismatch')
        m.ultimate_profile_id=27; m.ultimate_profile_engine=1; m.ultimate_profile_config=0
        need(cb.profile_reference_token == q.request_token and cb.profile_reference_result_id == 27 and cb.profile_reference_result_mode_index == q.mode_config_index and cb.profile_reference_result_store_generation == x['generation'] and len(cb.profile_reference_digest)==32, 'reference receipt fields mismatch')
        zero=PB.ProfileStoreRequest();zero.CopyFrom(q);zero.request_token=0
        need(cb.profile_reference_digest==hashlib.sha256(b'Glyph.ProfileStore.Request.v1\0'+zero.SerializeToString(deterministic=True)).digest(),'reference request digest differs from immutable receipt')
        for f in ['profile_reference_token','profile_reference_digest','profile_reference_result_id','profile_reference_result_mode_index','profile_reference_result_store_generation']: setattr(ca,f,getattr(cb,f))
        equal_config(ca,cb)
    elif kind == 'selection':
        need(x['records']==y['records'] and (x['generation'],x['high_water'])==(y['generation'],y['high_water']), 'selection changed store/transaction state')
        need(mode is not None and mode < len(ca.game_mode_configs), 'selection row required')
        m=ca.game_mode_configs[mode]; need(m.mode_id==PB.MODE_ULTIMATE and m.ultimate_profile_engine==1 and sha(preprocessing_bytes(m,PB))==KAZUYA.native_payload[28:60].hex(), 'selection context')
        need(not m.applicable_backends or backend in m.applicable_backends,'selection backend ineligible')
        m.ultimate_profile_id=27;m.ultimate_profile_engine=1;m.ultimate_profile_config=0
        matches=[i for i,v in enumerate(ca.communication_backend_configs) if v.backend_id==backend];need(len(matches)==1,'ambiguous backend')
        i=matches[0];ca.communication_backend_configs[i].default_mode_config=mode+1
        if backend in (PB.COMMS_BACKEND_XINPUT,PB.COMMS_BACKEND_DINPUT,PB.COMMS_BACKEND_NINTENDO_SWITCH):ca.default_usb_backend_config=i+1
        else:ca.default_backend_config=i+1
        equal_config(ca,cb);no_sel(cb)
    elif kind == 'deletes':
        no_sel(ca);no_sel(cb);equal_config(ca,cb)
        need(SEL <= set(map(int,x['records'])), 'all20 verified fixtures required before delete sequence')
        expected={k:v for k,v in x['records'].items() if int(k) not in SEL};need(y['records']==expected,'deletion preservation set differs')
        current=dict(x)
        for ident in sorted(SEL):
            stem=Path(receipt)/('delete-'+str(ident));q=request_receipt(str(stem)+'.request.json');r=response(str(stem)+'.result.json');post=status(str(stem)+'.post.json')
            after=dict(current,generation=post.store_generation,high_water=post.transaction_token_high_water)
            mutation(current,after,str(stem)+'.request.json',str(stem)+'.result.json',PB.PROFILE_STORE_DELETE,ident,1)
            need(post.config_generation==x['config_generation'],'DELETE changed Config digest');current=after
        need(y['generation']==current['generation'] and y['high_water']==current['high_water'],'final delete accounting differs')
    elif kind == 'create':
        no_sel(ca);no_sel(cb);equal_config(ca,cb)
        q,r=mutation(x,y,receipt,result,PB.PROFILE_STORE_CREATE,store_delta=1)
        need(q.name=='Kazuya' and q.profile.SerializeToString(deterministic=True)==KAZUYA.SerializeToString(deterministic=True),'CREATE payload/name mismatch')
        need(q.display_rank==rank(x),'CREATE rank differs from lowest free rank after Ultimate')
        need(r.profile_id and str(r.profile_id) not in x['records'],'CREATE ID is not new')
        expected=dict(x['records']);entry=y['records'].get(str(r.profile_id));need(entry is not None,'CREATE directory/read missing')
        need(entry=={'id':r.profile_id,'name':'Kazuya','rank':q.display_rank,'revision':r.profile_revision,'schema':5,'directory_payload_version':5,'wrapper_sha256':sha(KAZUYA.SerializeToString(deterministic=True)),'body_sha256':sha(KAZUYA.native_payload)},'Kazuya stored identity differs')
        need(r.profile_revision==1,'unexpected CREATE revision');expected[str(r.profile_id)]=entry;need(expected==y['records'],'non-SEL existing record changed')
    print('PASS '+kind)

def rank(s):
    native=[r for r in s['records'].values() if r['schema']==5];need(len(native)==1 and native[0]['id']==27,'rank plan requires only permanent Ultimate native record before CREATE')
    used={r['rank'] for r in s['records'].values()};v=s['records']['27']['rank']+1
    while v in used:v+=1
    need(v<=0xffffffff,'no safe rank after Ultimate');return v

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['fences','cursor','ids','snapshot','one','references','rank','identity','compare']);p.add_argument('path');p.add_argument('other',nargs='?');p.add_argument('--id',type=int);p.add_argument('--safe',action='store_true');p.add_argument('--initial',action='store_true');p.add_argument('--kind',choices=['preserve','reference','selection','deletes','create']);p.add_argument('--previous-status');p.add_argument('--receipt');p.add_argument('--result');p.add_argument('--mode',type=int);p.add_argument('--backend',type=int,default=2);a=p.parse_args();d=Path(a.path)
    if a.action=='fences':
        s=status(d);print(s.store_incarnation,s.store_generation,s.config_generation,s.transaction_token_high_water,s.transaction_token_high_water+1)
    elif a.action=='cursor':print(response(d).next_page_cursor)
    elif a.action=='ids':
        s=status(d/'status-start.json');print('\n'.join(map(str,directory(d,s))))
    elif a.action=='snapshot':
        out,c=audit(d,a.safe)
        if a.initial:
            need({int(k) for k,v in out['records'].items() if v['schema']==5}==SEL|{27},'initial native directory differs from Ultimate plus20 fixtures')
            operations=21+sum(m.ultimate_profile_id in SEL for m in c.game_mode_configs)
            need(out['generation']<=0xffffffff-21 and out['high_water']<=0xfffffffffffffffe-operations,'insufficient complete packet generation/token runway')
        with (d/'snapshot.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
        print('PASS snapshot; records='+str(len(out['records'])))
    elif a.action=='one':
        s=status(d/'status-start.json');c,raw=config(d/'config.json',s);no_sel(c)
        need(a.previous_status is not None and a.other is not None,'previous status and safe baseline required')
        need(key(s)==key(status(a.previous_status)),'state changed since previous successful operation')
        baseline=snapshot(a.other);need(sha(raw)==baseline['config_raw_sha256'],'Config changed since safe Ultimate checkpoint')
        entries=directory(d,s);need(a.id in SEL and a.id in entries,'not a listed SEL')
        expected={int(k):v for k,v in baseline['records'].items() if int(k) not in set(range(28,a.id))}
        need(set(entries)==set(expected),'unexpected directory addition/deletion or skipped DELETE')
        for ident,e in entries.items():
            need(all(e[k]==expected[ident][k] for k in e),'directory metadata changed before DELETE')
        record(d,a.id,entries[a.id],s);end=status(d/'status-end.json');need(key(s)==key(end),'pre-delete drift')
        print('PASS verified unreferenced SEL'+str(a.id-27).zfill(2))
    elif a.action=='references':
        c=parsed_config(d)
        for i,m in enumerate(c.game_mode_configs):
            if m.ultimate_profile_id in SEL:
                need(m.mode_id==PB.MODE_ULTIMATE and m.ultimate_profile_engine==1 and sha(preprocessing_bytes(m,PB))==KAZUYA.native_payload[28:60].hex(),'SEL reference not safe native/context match');print(i)
    elif a.action=='rank':print(rank(snapshot(d)))
    elif a.action=='identity':
        s=snapshot(d);i=load(a.other);need(i['context']=='xinput' and i['status']=='persisted' and i['primary_backend']==2 and i['active_id']==27 and i['requested_reference']==27 and i['active_revision']==1 and i['schema_version']==5 and i['incarnation']==s['incarnation'],'safe XInput ID27 identity not proven')
        profile=response(d/'read-27.json').profile;need(i['payload_sha256']==payload_digest(profile),'runtime identity digest mismatch');need(i['context_row']==a.mode,'runtime context row differs');print('PASS active ID27 exact XInput identity')
    else:compare(d,Path(a.other),a.kind,a.receipt,a.result,a.mode,a.backend)

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,OSError,AssertionError) as e:print('STOP: '+str(e),file=sys.stderr);sys.exit(1)
