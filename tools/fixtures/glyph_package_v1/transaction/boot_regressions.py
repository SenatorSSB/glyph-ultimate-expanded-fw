"""Finite actual-source startup probes; never access devices or infer their state."""
import argparse,copy,json,os,subprocess,sys
from pathlib import Path
from run import dump_namespace

def main():
    p=argparse.ArgumentParser();p.add_argument('--binary',required=True,type=Path)
    p.add_argument('--corpus',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
    p.add_argument('--require-visible',action='store_true');a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    sys.path[:0]=[str(a.corpus/'proof'),str(a.corpus/'wire'),str(a.corpus.parents[1]/'tools/research')]
    import glyph_package_storage as m
    import glyph_package_fixtures as f
    golden=json.loads((a.corpus/'storage-vectors.json').read_text())
    baseline=f.baseline(ultimate=True,backend=True)
    defaults=a.out/'defaults.pb';defaults.write_bytes(baseline['/config-v2.bin'][8:])
    cases=[(c['name'],{p:bytes.fromhex(v) for p,v in c['disk'].items()},
            not c['expected'][1] and bool(c['disk'])) for c in golden['cases']]
    cases += [('config-only',{'/config-v2.bin':baseline['/config-v2.bin']},False)]
    old=f.completed_migration(3)
    legacy={p:b for p,b in old.items() if not p.startswith('/ultimate-v2')}
    cases += [('legacy-v1',legacy,False)]
    pre=copy.deepcopy(baseline);_,tree=m.config_body(pre['/config-v2.bin']);f.put(tree,210,0)
    pre['/config-v2.bin']=f.config_file(tree);cases += [('pre-marker',pre,False)]
    pending=copy.deepcopy(f.completed_migration(2))
    for path in ('/ultimate-v2-0.bin','/ultimate-v2-1.bin'):
        root=bytearray(pending[path]);m.put32(root,20,1);m.put32(root,3904,m.crc(root[:3904]));pending[path]=bytes(root)
    pending['/ultimate-v2.ctrl']=f.source_control(pending['/ultimate-v2-0.bin'])
    cases += [('migration-pending',pending,False),('mount-failure',None,False)]
    results=[]
    env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'}
    def run(argv):
        c=subprocess.run(list(map(str,argv)),capture_output=True,text=True,timeout=30,env=env)
        if c.returncode:raise RuntimeError(str(argv)+'\n'+c.stdout+c.stderr)
    for i,(name,disk,normal) in enumerate(cases):
        out=a.out/str(i);out.mkdir();nor=out/'seed.nor'
        if disk is None:nor.write_bytes(bytes([255])*524288)
        else:
            namespace=out/'seed.namespace';dump_namespace(disk,namespace)
            run([a.binary,'seed',namespace,nor])
        run([a.binary,'boot',nor,defaults,out])
        r=json.loads((out/'boot.json').read_text());r.update(name=name,expected_normal=normal)
        results.append(r)
        (a.out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
        assert r['outcome']==(1 if normal else 6),(name,r)
        if a.require_visible and not normal:assert r['recovery_visible'] and not r['splash'],(name,r)
    print(json.dumps({'cases':len(results),'normal':sum(x['expected_normal'] for x in results),
        'recovery':sum(not x['expected_normal'] for x in results),'visible_required':a.require_visible,
        'physical_cause':'UNKNOWN','hardware_operations':0}))
if __name__=='__main__':main()
