#!/usr/bin/env python3
"""Read-only classifier replay of the retained 5030-event frozen campaign.

Every event is bound to its retained raw NOR digest. Identical raw states are
replayed once; this is equivalence, not a rerun of the mutation campaign.
"""
import argparse,concurrent.futures,hashlib,json,os,subprocess,zlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--retained',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
expected={'first':1388,'second':1612,'prior':2030};events={};images={}
for shard in sorted(a.retained.glob('historical-rgb-shard-*')):
 if not (shard/'results.jsonl').exists():continue
 for line in (shard/'results.jsonl').read_text().splitlines():
  row=json.loads(line);context,index=row['context'],row['event']['index'];key=(context,index)
  assert key not in events and row['pass'] and row['source_fingerprint']=='8486ea4bcef83736d5229534b59e608ea01aaf27c39ec426a498212756e5b0db'
  path=shard/context/('cut-%04d'%index)/'cut.nor.zlib';raw=zlib.decompress(path.read_bytes());digest=hashlib.sha256(raw).hexdigest()
  assert len(raw)==524288 and digest==row['raw_nor_sha256']
  events[key]=digest;images.setdefault(digest,(path,raw))
assert set(events)=={(ctx,i) for ctx,n in expected.items() for i in range(n)}
env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'}
def replay(item):
 digest,(source,raw)=item;work=a.out/digest;work.mkdir();(work/'before.nor').write_bytes(raw);results=[]
 for name,binary in [('baseline',a.baseline),('candidate',a.candidate)]:
  out=work/name;out.mkdir();cmd=[str(binary),'migration-diagnostic',str(work/'before.nor'),'18446744073709551615',str(out)];proc=subprocess.run(cmd,capture_output=True,text=True,env=env)
  assert proc.returncode==0,(cmd,proc.stdout,proc.stderr)
  facts=json.loads((out/'classification.json').read_text());stats=json.loads((out/'summary.json').read_text())
  assert (out/'after.nor').read_bytes()==raw and stats['programs']==stats['erases']==0 and stats['unchanged']
  results.append(facts)
 x,y=results
 assert {k:v for k,v in x.items() if k!='diagnostic'}=={k:v for k,v in y.items() if k!='diagnostic'},(digest,x,y)
 if x['diagnostic']!=y['diagnostic']:assert y['diagnostic'].startswith('migration: ')
 assert (work/'baseline/namespace.bin').read_bytes()==(work/'candidate/namespace.bin').read_bytes()
 return dict(raw_nor_sha256=digest,retained_source=str(source),baseline=x,candidate=y,raw_nor_unchanged=True,programs=0,erases=0)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(replay,sorted(images.items())))
(a.out/'states.json').write_text(json.dumps(results,indent=2)+'\n');(a.out/'events.json').write_text(json.dumps([dict(context=k[0],index=k[1],raw_nor_sha256=v) for k,v in sorted(events.items())],indent=2)+'\n')
summary=dict(result='PASS',retained_events=len(events),unique_raw_states=len(images),coverage=expected,all_material_fields_equal=True,raw_nor_unchanged=True,filesystem_equal=True,programs=0,erases=0,hardware_operations=0)
(a.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
