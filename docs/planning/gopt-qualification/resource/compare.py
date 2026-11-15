#!/usr/bin/env python3
"""Offline final-image resource comparison. No build and no device operations."""
import argparse, hashlib, json, shutil, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--map',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--source',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--toolchain',type=Path,required=True);p.add_argument('--baseline-dir',type=Path,required=True);p.add_argument('--baseline-control',action='store_true');a=p.parse_args();BASE=a.baseline_dir
a.out.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(argv):
 r=subprocess.run(list(map(str,argv)),capture_output=True,text=True)
 (a.out/('command-%02d.log'%len(logs))).write_text(r.stdout+r.stderr)
 logs.append({'argv':list(map(str,argv)),'returncode':r.returncode})
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 return r.stdout
logs=[]
def shape(x):return [x['resolved_frame_bytes'],sorted(set(c['name'] for c in x['calls'])), sorted(set(c['name'] for c in x['tail'])), sorted(set(c['instruction'] for c in x['indirect']))]
def load(p):return json.loads(p.read_text())
try:
 assert sha(BASE/'firmware.elf')=='1c42f32ca4dcb18c54dcb591f64ed97d3372c99a51874f258e5f64d0dcdf52b2', 'Wrong retained integration baseline ELF'
 assert sha(BASE/'resource/functions.json')=='bca4901c189a5bb05af0205f92670c5125bd10252280093104d9fb8a2317ff86', 'Wrong baseline linked graph'
 assert sha(BASE/'resource/core1-bound-graph.json')=='adc65b97ce96fa20e35985ce4403e6936c625bc947c91bcf485d90376da5d114', 'Wrong retained resource/core1-bound-graph.json'
 assert sha(BASE/'resource/summary.json')=='cc734aff2328a5c6d7bd50ac30919c006d99e92baa0008faf37df41d6388f79a', 'Wrong retained resource/summary.json'
 assert sha(a.repo/'docs/runtime_config/package_active_profile_display/resource/baseline-resource-source-predicate-ledger.json.gz')=='a3c67143f713045e3f6498088ad35fdaa7391a1f93eae765bb040d5278d9d1a6', 'Wrong retained ledger'
 assert len(a.source)==40 and all(c in '0123456789abcdef' for c in a.source)
 assert run(['git','-C',a.repo,'rev-parse',a.source]).strip()==a.source
 source_paths=['src','HAL','include','config','schema','platformio.ini','builder_scripts','lib']
 run(['git','-C',a.repo,'diff','--quiet','0b9ef3afd1834ac7832871bca0651b67147840a2','2bcb5104054f64d8b9c1af9dd1be4a974112f8ec','--',*source_paths])
 if a.baseline_control:
  assert a.source=='0b9ef3afd1834ac7832871bca0651b67147840a2' and sha(a.elf)=='43b3b7b0630d66d0b17266580e2cd6be0862cd9059694cf805b1c90d5b21fd1f', 'Baseline-control flag accepts only exact retained0b9 source/ELF'
 else:run(['git','-C',a.repo,'diff','--quiet',a.source,'--',*source_paths])
 # Data-custody copy is internal to this analysis directory only.
 shutil.copyfile(a.elf,a.out/'firmware.elf');shutil.copyfile(a.map,a.out/'firmware.map')
 assert sha(a.elf)==sha(a.out/'firmware.elf')
 assert bytes.fromhex(a.source) in a.elf.read_bytes(), 'ELF does not contain requested source identity'
 R=a.out/'resource'
 run([sys.executable,HERE/'extract.py','--elf',a.out/'firmware.elf','--output-dir',R,'--toolchain',a.toolchain])
 f=load(R/'functions.json');b=load(BASE/'resource/functions.json');s=load(R/'summary.json');bs=load(BASE/'resource/summary.json')
 from graph_gate import audit
 delta=audit(b,f);changed=delta['changed'];added=delta['added'];removed=delta['removed']
 (a.out/'graph-delta.json').write_text(json.dumps(delta,indent=2)+'\n')
 run([sys.executable,HERE/'core0.py','--resource',R,'--baseline-functions',BASE/'resource/functions.json','--baseline-ledger',a.repo/'docs/runtime_config/package_active_profile_display/resource/baseline-resource-source-predicate-ledger.json.gz','--output',a.out/'core0.json'])
 run([sys.executable,HERE/'core1.py','--output-dir',R])
 c0=load(a.out/'core0.json');c1=load(R/'core1-bound-graph.json');oldc1=load(BASE/'resource/core1-bound-graph.json')
 assert not c1['unknown'],c1['unknown']
 assert c1['bounds']['loop1']['bound']+16+68<=1152
 assert all(shape(f[n])==shape(b[n]) for n in oldc1['reachable'] if not n.startswith(('MenuButtonHints::UpdateDisplay(', 'draw_profile_label('))), 'Changed inherited core1 descendant'
 assert c1['special_bounds']==oldc1['special_bounds'], 'Changed core1 leaf union'
 assert all(n in b and shape(f[n])==shape(b[n]) for n in c1['special_bounds']), 'Changed special leaf machine-code shape'
 # IRQ unions and ROM assumptions are unchanged: require ALL non-page/non-loop
 # functions to retain shape, rather than silently replaying only local frames.
 symbols={x['name']:x for x in load(R/'symbols.json')}
 assert symbols['__StackTop']['address']==0x20042000 and symbols['__StackOneTop']['address']==0x20041000
 assert symbols['__StackLimit']['address']==0x20040000
 assert s['stack_reservations']==[2048,2048]
 assert s['static']<=bs['static'] and s['static']<=199632
 assert s['heap_capacity']>=bs['heap_capacity']
 # No CRC scratch may lengthen later siblings: an inline clone's local
 # frame must not exceed the accepted frame when its outgoing graph changes.
 crc_wrappers=[n for n in f if n.startswith(('Persistence::CheckSavedConfig()', 'Persistence::ValidateLegacySource(', 'Persistence::CheckCaptureInput(', 'Persistence::LoadConfigRaw('))]
 assert all(f[n]['resolved_frame_bytes']<=b[n]['resolved_frame_bytes'] for n in crc_wrappers), 'CRC local outlives its phase in an inline caller; shorten lifetime or recompose sibling branches'
 # CRC helpers are returned siblings of decode, encode, stage write and rename.
 # Bound every linked ancestor path conservatively with a 540-byte checked
 # read/seek/stat/open lower subtree; use the larger physical IRQ408 even for
 # configurator paths. main/setup/loop direct paths and virtual SendReport
 # roots cover startup/recovery, migration, ordinary load/save/reconcile,
 # checked reference, GET/SET and package config publication.
 reverse={n:set() for n in f}
 for n,x in f.items():
  for e in x['calls']+x['tail']:
   if e['name'] in reverse:reverse[e['name']].add(n)
 targets=[n for n in f if n.startswith(('Persistence::CheckSavedConfig(', 'Persistence::ValidateLegacySource(', 'Persistence::CheckCaptureInput(', 'Persistence::LoadConfigRaw('))]
 roots={'main':0, 'setup':f['main']['resolved_frame_bytes'], 'loop':f['main']['resolved_frame_bytes'], 'ConfiguratorBackend::SendReport()':f['main']['resolved_frame_bytes']+f['loop']['resolved_frame_bytes']}
 crc_routes=[];unclosed=[]
 def ancestors(n, path):
  assert n not in path, ('CRC ancestor recursion',path,n)
  path=path+[n]
  if n in roots:
   total=roots[n]+sum(f[k]['resolved_frame_bytes'] for k in path)+540+408
   crc_routes.append({'path':list(reversed(path)),'outer_prefix':roots[n],'checked_lower_subtree':540,'IRQ':408,'total':total})
   return
  parents=reverse[n]
  if not parents:
   # Exact source migration callback is passed synchronously by boot migrator.
   if n.startswith('MigrateBootLegacyConfiguration()::{lambda'):
    parents=[k for k in f if k.startswith('ProfileStore::PrepareImportedLegacyRecord(')]
    assert len(parents)==1 and f[parents[0]]['indirect']
    ancestors(parents[0],path);return
   unclosed.append(path);return
  for parent in sorted(parents):ancestors(parent,path)
 for n in targets:ancestors(n,[])
 assert not unclosed,('Unmodeled CRC ancestor',unclosed)
 assert crc_routes and max(x['total'] for x in crc_routes)<=2048
 (a.out/'crc-callers.json').write_text(json.dumps({'routes':crc_routes,'unclosed':unclosed,'assumption':'Exact baseline checked read/seek/stat/open subtree upper540 unchanged; all paths carry conservative physical IRQ408; returned phase siblings max-compose.'},indent=2)+'\n')
 # Enumeration's visitor runs sequentially with directory I/O, not beneath it.
 def one(prefix):
  names=[n for n in f if n.startswith(prefix)];assert len(names)==1,(prefix,names);return names[0]
 visitor=one('(anonymous namespace)::SelectObject(')
 assert not f[visitor]['indirect']
 assert set(e['name'] for e in f[visitor]['calls']+f[visitor]['tail'])<={'__wrap___aeabi_memcpy'}
 visitor_bound=f[visitor]['resolved_frame_bytes']+12
 enumeration=one('CheckedStorage::Enumerate(');objectat=one('GlyphPackageSourceReader::ObjectAt(')
 visitor_route=680+f[one('package_storage::ClassifyNamespaceInto(')]['resolved_frame_bytes']+f[one('package_storage::(anonymous namespace)::Classifier::Run()')]['resolved_frame_bytes']+f[objectat]['resolved_frame_bytes']+f[enumeration]['resolved_frame_bytes']+visitor_bound
 assert visitor_route<=c0['routes']['classify.directory_scan']['total']
 constructor=one('GlyphPackageSourceReader::GlyphPackageSourceReader(')
 assert not f[constructor]['indirect']
 assert set(e['name'] for e in f[constructor]['calls']+f[constructor]['tail'])<={'__wrap_memset'}
 assert f[constructor]['resolved_frame_bytes']+8<=64
 def flash(x):return sum(x['sections'][n]['size'] for n in ['.boot2','.text','.rodata','.data'])
 summary={'source':a.source,'baseline_tested_source':'0b9ef3afd1834ac7832871bca0651b67147840a2','canonical_baseline':'2bcb5104054f64d8b9c1af9dd1be4a974112f8ec','baseline_reference_elf_sha256':sha(BASE/'firmware.elf'),'elf_sha256':sha(a.elf),'map_sha256':sha(a.map),'named_functions':len(f),'graph_changes':list(changed),'static_ram':s['static'],'static_delta':s['static']-bs['static'],'static_ceiling':199632,'heap_capacity':s['heap_capacity'],'heap_delta':s['heap_capacity']-bs['heap_capacity'],'flash':flash(s),'flash_delta':flash(s)-flash(bs),'stack_reservations':s['stack_reservations'],'core0_maximum':c0['maximum_affected_route'],'core0_lifecycle_maximum':c0['new_lifecycle_maximum'],'core0_routes':len(c0['routes']),'core1_setup':c1['bounds']['setup1']['bound'],'core1_loop':c1['bounds']['loop1']['bound'],'core1_bound':max(c1['bounds'][n]['bound'] for n in ['loop1','setup1'])+16+68,'core1_budget':1152,'crc_routes':len(crc_routes),'crc_maximum':max(x['total'] for x in crc_routes),'directory_visitor_subtree':visitor_bound,'directory_visitor_complete_route':visitor_route,'directory_io_route':c0['routes']['classify.directory_scan']['total'],'core1_unresolved_edges':c1['unknown'],'physical_highwater':'NOT_MEASURED','status':'PASS_BASELINE_CONTROL' if a.baseline_control else 'PASS_MODELED_SCOPE'}
 (a.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
finally:
 (a.out/'commands.json').write_text(json.dumps(logs,indent=2)+'\n')
