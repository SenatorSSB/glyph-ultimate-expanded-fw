#!/usr/bin/env python3
"""Adversarial proof controls: source-family allowlist cannot hide unknown edges."""
import argparse,copy,json
from pathlib import Path
from graph_gate import audit
p=argparse.ArgumentParser();p.add_argument('--baseline-functions',type=Path,required=True);p.add_argument('--candidate-functions',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
b=json.loads(a.baseline_functions.read_text());f=json.loads(a.candidate_functions.read_text());audit(b,b);audit(b,f)
results=[]
def reject(label,mutation):
 g=copy.deepcopy(f);mutation(g)
 try:audit(b,g)
 except AssertionError:results.append({'control':label,'result':'REJECTED_AS_REQUIRED'});return
 raise AssertionError('False pass: '+label)
crc=next(n for n in f if n.startswith('Persistence::CheckSavedConfig(CheckedStorageFile&'))
renderer=next(n for n in f if n.startswith('MenuButtonHints::UpdateDisplay('))
def edge(n,target):return lambda g:g[n]['calls'].append({'name':target})
reject('Unknown CRC symbol',edge(crc,'GOPT_UNMODELED_FUNCTION'))
reject('Known malloc inserted under CRC',edge(crc,'__wrap_malloc'))
reject('Unknown renderer symbol',edge(renderer,'GOPT_UNMODELED_FUNCTION'))
reject('Unknown loop indirect instruction',lambda g:g['loop']['indirect'].append({'instruction':'blx r12'}))
reject('Changed filesystem frame',lambda g:g['lfs_dir_open'].__setitem__('resolved_frame_bytes',g['lfs_dir_open']['resolved_frame_bytes']+4))
reject('Removed inherited function',lambda g:g.pop('lfs_dir_open'))
reject('Unrecognized added function',lambda g:g.__setitem__('GOPT_UNMODELED_FUNCTION',copy.deepcopy(g[crc])))
result={'baseline_positive':'PASS','candidate_positive':'PASS','negative_controls':results,'count':len(results)}
a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
