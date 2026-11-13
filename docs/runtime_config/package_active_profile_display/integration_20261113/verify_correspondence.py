"""Read-only exact-source/ancestry/frozen-document proof; no build or device IO."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
F='9e69188d857138a3884bcbe243f22188815e9355'
R='286fd3b792bddb71559538b10fe57fae860d643b'
E='f24b7abe2af6f9bb5994f2baa51e1fd6c7ae6df5'
B='d31a5edd433beca0354e4595c26d0c4b69c085e8'
EJOIN='ee5cbffa33f2562b6637d29a9ce9b32580be94d2'
I='e027f1cd851c037f0b4f8c3a2ab321eef1b81e34'
CURRENT={'docs/AGENT_CONTEXT.md','docs/CURRENT_STATE.md','docs/ROADMAP.md','docs/agent_framework/USER_DIRECTION.md','docs/runtime_config/README.md'}
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def tree(ref):
    result={}
    for row in git('ls-tree','-rz',ref).split(b'\0'):
        if row:
            h,p=row.split(b'\t',1);mode,kind,oid=h.decode().split()
            result[p.decode()]={'mode':mode,'kind':kind,'object':oid}
    return result
f,r,e,b,i,head=map(tree,(F,R,E,B,I,'HEAD'))
non=lambda x:{p:v for p,v in x.items() if not p.startswith('docs/')}
assert non(f)==non(r)==non(i)==non(head),'non-documentation inputs differ from tested F'
assert non(e)==non(b),'hardware result E is not source-free'
assert git('show','-s','--format=%P',EJOIN).decode().split()==[B,E]
assert git('show','-s','--format=%P',I).decode().split()==[EJOIN,R]
for ref in (F,R,E,I):assert subprocess.run(['git','merge-base','--is-ancestor',ref,'HEAD'],cwd=ROOT).returncode==0
assert git('rev-parse',F+'^{tree}').decode().strip()=='cd0d8408b1c8b808a3a41529259b57c0896e2f7c'
blobs=sorted({v['object'] for v in non(f).values() if v['kind']=='blob'})
raw=subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=('\n'.join(blobs)+'\n').encode());at=0;hashes={}
for oid in blobs:
    end=raw.index(b'\n',at);size=int(raw[at:end].split()[2]);data=raw[end+1:end+1+size]
    hashes[oid]=hashlib.sha256(data).hexdigest();at=end+size+2
entries=[]
for path,value in sorted(non(f).items()):
    sha=hashes.get(value['object']);p=ROOT/path
    if value['kind']=='blob':
        data=os.readlink(p).encode() if value['mode']=='120000' else p.read_bytes()
        assert hashlib.sha256(data).hexdigest()==sha,'working input drift: '+path
        if value['mode']!='120000':assert bool(p.stat().st_mode&0o111)==(value['mode']=='100755'),'working mode drift: '+path
    entries.append({'path':path,**value,'sha256':sha})
frozen={}
for origin,values in ((R,r),(E,e)):
    for path,value in values.items():
        if path.startswith('docs/') and path not in CURRENT:
            assert head.get(path)==value,'historical document drift: '+path
            assert hashlib.sha1((b'blob '+str(len((ROOT/path).read_bytes())).encode()+b'\0')+(ROOT/path).read_bytes()).hexdigest()==value['object'],'working historical document drift: '+path
            if path in frozen:assert frozen[path]==value
            frozen[path]=value
changed=[p for p in sorted(set(non(f))|set(non(b))) if non(f).get(p)!=non(b).get(p)]
late_host=[p for p in sorted(r) if p.startswith('docs/') and p.endswith('.py') and f.get(p)!=r[p]]
catalog={'result':'PASS_EXACT_TESTED_NON_DOCUMENTATION_INPUTS','tested_F':F,'accepted_source_R':R,'source_free_result_E':E,'fresh_canonical_B':B,'source_free_adoption_merge':EJOIN,'actual_source_join_I':I,'source_join_parents':[EJOIN,R],'source_free_adoption_parents':[B,E],'tested_tree':'cd0d8408b1c8b808a3a41529259b57c0896e2f7c','critical_path_count':len(entries),'critical_paths':entries,'changed_non_doc_paths_from_B':changed,'frozen_document_count':len(frozen),'frozen_documents_catalog_sha256':hashlib.sha256(json.dumps(frozen,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'later_host_executors_under_docs':late_host,'later_host_disposition':'Preserved exact bytes as historical approved one-shot host executors/evidence processors; not firmware inputs, not newly hardware tested, not executed by this integration. No fresh device authority.','current_document_exceptions':sorted(CURRENT),'firmware_rebuilds':0,'device_access':False}
if sys.argv[1:]==['--write']:(OUT/'CORRESPONDENCE.json').write_text(json.dumps(catalog,indent=2)+'\n')
else:
    assert not sys.argv[1:]
    assert json.loads((OUT/'CORRESPONDENCE.json').read_text())==catalog,'catalog differs'
print('PASS',len(entries),'tracked inputs outside docs/; changed from B:',len(changed),'; frozen docs:',len(frozen),'; later host scripts:',len(late_host))
