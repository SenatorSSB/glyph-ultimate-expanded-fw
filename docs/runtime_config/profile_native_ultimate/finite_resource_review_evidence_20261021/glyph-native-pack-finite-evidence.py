#!/usr/bin/env python3
"""Archive explicit finite proof inputs; keep firmware bytes in their custody locator."""
from pathlib import Path
import argparse,json,hashlib,gzip
ap=argparse.ArgumentParser();ap.add_argument('destination');ap.add_argument('--pins',action='append',default=[]);ap.add_argument('--flat',action='append',default=[]);a=ap.parse_args();out=Path(a.destination);out.mkdir(exist_ok=False);(out/'objects').mkdir()
def h(b):return hashlib.sha256(b).hexdigest()
inputs={}; flat=[]
for s in a.pins:
 p=Path(s);d=json.loads(p.read_text());inputs[s]={'sha256':h(p.read_bytes()),'bytes':p.stat().st_size}
 for k,v in d.get('files',{}).items():
  assert isinstance(v,dict) and 'sha256' in v,(s,k)
  if k in inputs:assert inputs[k]['sha256']==v['sha256'],k
  inputs[k]=v
for s in a.flat+a.pins:
 p=Path(s);raw=p.read_bytes();dst=out/p.name
 if dst.exists():assert dst.read_bytes()==raw,p
 else:dst.write_bytes(raw)
 flat.append({'source':s,'relative':p.name,'bytes':len(raw),'sha256':h(raw)})
entries=[]
for s,v in sorted(inputs.items()):
 p=Path(s);assert p.is_file() and not p.is_symlink(),s
 raw=p.read_bytes();digest=h(raw);assert digest==v['sha256'],s
 e={'source':s,'raw_sha256':digest,'raw_bytes':len(raw)}
 if 'local_backups/hardware-artifacts/' in s:
  e.update(custody_reference=s,archived=False,reason='Firmware artifact retained at exact immutable content-addressed custody; no substitute artifact embedded.')
 else:
  compressed=gzip.compress(raw,compresslevel=9,mtime=0);dst=out/'objects'/(digest+'.gz')
  if dst.exists():assert dst.read_bytes()==compressed
  else:dst.write_bytes(compressed)
  assert gzip.decompress(dst.read_bytes())==raw
  e.update(relative=str(dst.relative_to(out)),compressed_sha256=h(compressed),compressed_bytes=len(compressed),archived=True)
 entries.append(e)
manifest={'kind':'FINITE_INNER_AND_STARTUP_EVIDENCE_ARCHIVE_NO_WHOLE_RESOURCE_ACCEPTANCE','script_sha256':h(Path(__file__).read_bytes()),'flat':flat,'inputs':entries,'qualification':'Exact immutable reports and explicit pinned inputs only. Archive does not certify source graph completeness, final candidate correspondence, target observation, hardware acceptance or all31/P1 PASS. Original reports, limitations, failed attempts and custody locators preserved.'}
p=out/'manifest.json';p.write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'directory':str(out),'manifest_sha256':h(p.read_bytes()),'flat':len(flat),'inputs':len(entries),'unique_gzip_objects':len(list((out/'objects').glob('*.gz'))),'compressed_total_bytes':sum(p.stat().st_size for p in (out/'objects').glob('*.gz'))},indent=2))
