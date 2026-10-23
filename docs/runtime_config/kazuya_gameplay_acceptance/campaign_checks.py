#!/usr/bin/env python3
"""Offline campaign checks. Never opens a serial port or transmits a device request."""
import ast, argparse, hashlib, importlib.util, json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def load(p):return json.loads(Path(p).read_text())
def need(v,msg):
    if not v:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def checks():
    s=importlib.util.spec_from_file_location('frozen_menu_checks',ROOT/'docs/runtime_config/character_profile_menu/packet_checks.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def verify():
    ident=load(HERE/'IDENTITY.json')
    for name,h in ident['source_files_sha256'].items():need(sha(ROOT/name)==h,'changed pinned input '+name)
    sys.path.insert(0,str(ROOT/'tools'))
    import glyph_native_profile_json as c
    p=c.load_json(ROOT/'profiles/kazuya/Kazuya.profile.json')
    need(c.compile_report(p)==ident['compile_report'],'canonical compile report mismatch')
    matrix=load(HERE/'TEST_MATRIX.json');cases=matrix['cases'];ids=[x['id'] for x in cases]
    need(matrix['packet_id']==ident['packet_id']=='KGA-ID48-GC-R2','packet identity mismatch')
    need(len(ids)==len(set(ids))==matrix['manual_check_count_maximum']==35,'case count/identity')
    need(sum(not x['optional'] for x in cases)==matrix['required_checks']==33,'required count')
    need(sum(x['optional'] for x in cases)==matrix['optional_checks']==2,'optional count')
    # Deterministic expectations remain pinned to the host oracle. Manual R2
    # intentionally does not enumerate every RF state/horizontal combination.
    tree=ast.parse((ROOT/'tools/test_kazuya_profile.py').read_text())
    assignments=[n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MATRIX' for t in n.targets)]
    need(len(assignments)==1,'ambiguous host MATRIX')
    oracle=ast.literal_eval(assignments[0].value);need(len(oracle)==16,'host MATRIX extent')
    names={0:'none',1:'A',2:'B',32:'Z',33:'A+Z'}
    for case in cases:
        if 'rf_index' not in case or 'agent_expected_native_table' not in case:continue
        table,digital=oracle[case['rf_index']]
        if case.get('shield'):table='DefensiveDownBack'
        need(case['agent_expected_native_table']==table and case['agent_expected_command_digital']==names[digital],'attached expectation differs '+case['id'])
    review=load(HERE/'packet_review.json')
    need(review['verdict']=='PASS_FOR_OWNER_APPROVAL' and review['packet_id']==ident['packet_id'],'independent R2 review not PASS')
    for name,h in review['reviewed_files_sha256'].items():need(sha(HERE/name)==h,'reviewed file changed '+name)
    print('PASS pinned sources, canonical compile, matrix, independent reviewed packet')
def snap(path,accepted=False):
    m=checks();s,c=m.audit(path,True)
    ids=s['records'];need(set(k for k,v in ids.items() if v['schema']==5)=={'27','48'},'native directory differs')
    ident=load(HERE/'IDENTITY.json');r=ids['48']
    need(r['name']=='Kazuya' and r['revision']==1 and r['wrapper_sha256']==ident['compile_report']['wrapper_sha256'] and r['body_sha256']==ident['compile_report']['body_sha256'],'ID48 mismatch')
    if accepted:
        old=load(ROOT/'docs/runtime_config/character_profile_menu/hardware_20261023/preservation.json')['after']
        need(s==old,'preflight differs from accepted baseline; stop for reconciliation')
    out=Path(path)/'snapshot.json'
    if out.exists():need(load(out)==s,'saved snapshot mismatch')
    else:
        with out.open('x') as f:json.dump(s,f,indent=2);f.write('\n')
    return s,c,m
def compare(a,b,eventfile):
    x,ca,m=snap(a);y,cb,_=snap(b)
    for k in ['incarnation','generation','high_water','records']:need(x[k]==y[k],'preservation differs '+k)
    events=load(eventfile);need(isinstance(events,list) and 1<=len(events)<=12,'missing/unbounded selection log')
    for e in events:
        need(set(e)=={'profile_id','backend','mode_index','owner_observation'},'event fields')
        ident,backend,i=e['profile_id'],e['backend'],e['mode_index']
        need(ident in (27,48) and backend in (2,3) and (ident!=48 or backend==3),'unauthorized selection scope')
        need(bool(e['owner_observation']) and isinstance(i,int) and not isinstance(i,bool) and 0<=i<len(ca.game_mode_configs),'unobserved/invalid context row')
        mode=ca.game_mode_configs[i]
        need(mode.mode_id==m.PB.MODE_ULTIMATE and mode.ultimate_profile_engine==1,'not existing native context')
        need(not mode.applicable_backends or backend in mode.applicable_backends,'ineligible backend')
        need(m.sha(m.preprocessing_bytes(mode,m.PB))==m.KAZUYA.native_payload[28:60].hex(),'context mismatch')
        indices=[j for j,v in enumerate(ca.communication_backend_configs) if v.backend_id==backend]
        need(len(indices)==1,'ambiguous backend');j=indices[0]
        mode.ultimate_profile_id=ident;mode.ultimate_profile_engine=1;mode.ultimate_profile_config=0
        ca.communication_backend_configs[j].default_mode_config=i+1
        if backend==2:ca.default_usb_backend_config=j+1
        else:ca.default_backend_config=j+1
    need(events[-1]['profile_id']==27,'last approved profile selection must be Ultimate')
    m.equal_config(ca,cb)
    print('PASS all records/store fences unchanged; exact Config replay of observed selections; CRC verified independently per snapshot')
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='action',required=True)
    sub.add_parser('verify')
    s=sub.add_parser('snapshot');s.add_argument('path');s.add_argument('--accepted',action='store_true')
    c=sub.add_parser('compare');c.add_argument('before');c.add_argument('after');c.add_argument('events')
    s=sub.add_parser('show');s.add_argument('group',type=int,choices=range(1,9));s.add_argument('--batch',type=int,default=1)
    a=p.parse_args()
    if a.action=='verify':verify()
    elif a.action=='snapshot':s,_,_=snap(a.path,a.accepted);print('PASS full snapshot',len(s['records']),'records')
    elif a.action=='compare':compare(a.before,a.after,a.events)
    else:
        rows=[x for x in load(HERE/'TEST_MATRIX.json')['cases'] if x['group']==a.group]
        need(1<=a.batch<=(len(rows)+2)//3,'batch outside group')
        shown=[]
        for row in rows[(a.batch-1)*3:a.batch*3]:
            owner={k:v for k,v in row.items() if not k.startswith('agent_') and k not in ('rf_index','shield')}
            if 'steps' in owner:owner['steps']=[{k:v for k,v in step.items() if not k.startswith('agent_')} for step in owner['steps']]
            shown.append(owner)
        print(json.dumps(shown,indent=2))
if __name__=='__main__':main()
