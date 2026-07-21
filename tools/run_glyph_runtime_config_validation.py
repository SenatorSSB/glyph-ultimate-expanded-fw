#!/usr/bin/env python3
"""Read-only deterministic aggregate runner for current runtime-config checks."""
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'docs/runtime_config/fixtures/runtime_config_validation_manifest.json'
REQUIRED={'id','command','category','applicability','branch_policy','source_dependencies','expected_success_exit','load_bearing','historical','arguments_required'}
def pairs(items):
 d={}
 for k,v in items:
  if k in d: raise ValueError(f'duplicate JSON key: {k}')
  d[k]=v
 return d
def load():
 m=json.loads(MANIFEST.read_text(),object_pairs_hook=pairs)
 if m.get('schema_version')!=1 or not isinstance(m.get('entries'),list): raise ValueError('invalid manifest root')
 ids=set()
 for e in m['entries']:
  if set(e)!=REQUIRED or e['id'] in ids: raise ValueError(f"invalid or duplicate checker entry: {e.get('id')}")
  ids.add(e['id'])
  if not isinstance(e['command'],list) or not e['command'] or e['arguments_required'] or (e['historical'] and e['applicability']!='historical_only'): raise ValueError(f"unsafe manifest entry: {e['id']}")
  if e['applicability']=='current' and e['historical']: raise ValueError(f"historical current entry: {e['id']}")
  if len(e['command'])>1 and not (ROOT/e['command'][1]).is_file(): raise ValueError(f"missing checker path: {e['command'][1]}")
 return m['entries']
def main():
 p=argparse.ArgumentParser();p.add_argument('--category',action='append');p.add_argument('--fail-fast',action='store_true');p.add_argument('--json',action='store_true');p.add_argument('--check-manifest',action='store_true');a=p.parse_args()
 try: entries=load()
 except Exception as e: print(f'manifest: FAIL: {e}');return 1
 if a.check_manifest: print('glyph_runtime_config_validation_manifest: PASS');return 0
 selected=[e for e in entries if e['applicability']=='current' and (not a.category or e['category'] in a.category)]
 results=[]
 for e in selected:
  r=subprocess.run(e['command'],cwd=ROOT,text=True,capture_output=True)
  results.append({'id':e['id'],'category':e['category'],'exit_code':r.returncode,'passed':r.returncode==e['expected_success_exit'],'stdout':r.stdout.strip(),'stderr':r.stderr.strip()})
  if a.fail_fast and not results[-1]['passed']: break
 ok=all(r['passed'] for r in results)
 out={'status':'PASS' if ok else 'FAIL','results':results,'historical_excluded':[e['id'] for e in entries if e['historical']]}
 if a.json: print(json.dumps(out,sort_keys=True))
 else:
  print(f"glyph_runtime_config_validation: {out['status']}")
  for r in results: print(f"- {r['id']}: {'PASS' if r['passed'] else 'FAIL'}")
  print('historical_excluded='+','.join(out['historical_excluded']))
 return 0 if ok else 1
if __name__=='__main__': raise SystemExit(main())
