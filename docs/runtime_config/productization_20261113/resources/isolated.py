#!/usr/bin/env python3
"""Exact isolated diagnostic core0 delta against the retained display predecessor."""
import argparse,gzip,hashlib,json
from pathlib import Path
from compose import shape

p=argparse.ArgumentParser();p.add_argument('--baseline-gz',type=Path,required=True);p.add_argument('--resource',type=Path,required=True);p.add_argument('--lane',choices=['startup','selection'],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
f=json.loads((a.resource/'functions.json').read_bytes());b=json.loads(gzip.decompress(a.baseline_gz.read_bytes()))
changed={k:(b[k]['resolved_frame_bytes'],f[k]['resolved_frame_bytes']) for k in f.keys()&b.keys() if shape(f[k])!=shape(b[k])};added=sorted(f.keys()-b.keys());removed=sorted(b.keys()-f.keys());routes={}
def fr(n):
 if n in f:return f[n]['resolved_frame_bytes']
 hs=[k for k in f if n in k and 'lambda' not in k];assert len(hs)==1,(n,hs);return f[hs[0]]['resolved_frame_bytes']
def total(name,*parts):routes[name]=sum(i if isinstance(i,int) else fr(i) for i in parts)
assert fr('loop')<=32
if a.lane=='startup':
 allowed=('show_boot_stage(', 'AboutMenu::UpdateDisplay(', '::ClassifyNamespaceInto(', 'Classifier::Run()', 'loop','GlyphPackageSourceReader::')
 assert all(any(w in k for w in allowed) for k in changed), changed
 assert all(k=='setup1::{lambda()#2}::_FUN()' for k in removed),removed
 assert all(any(w in k for w in ('Classification()', 'SelectConfig(', 'boot_timing::Snapshot()', 'transfer_dashboard()', 'mark_first_mode_ready()', 'boot_times','MaterializeProjection(', 'arduino::Print::print(unsigned long, int)')) for k in added),added
 # Full arbitrary Config semantic path can be reached in Scan, including historical recheck. OwnedSet already excludes all embedded profiles.
 for phase,sub in [('Classifier::Run()', 'Classifier::HistoricalRetained()'),('Classifier::RunRoots()', 'Classifier::LoadConfigs()')]:
  total('arbitrary_config.'+phase,680,'::ClassifyNamespaceInto(',phase,sub,'GlyphPackageSourceReader::Config(', 'GlyphPackageSourceReader::LoadNamedConfig(', 'Persistence::ObservePackageConfig(', 'Persistence::RunObservedPackageConfig()',1000)
 for adapter in [('GlyphPackageSourceReader::Native(','GlyphPackageSourceReader::MaterializeProjection('),('GlyphPackageSourceReader::Row(',)]:
  total('owned_compact.'+adapter[0],680,'::ClassifyNamespaceInto(',max(fr('Classifier::RunBaseline()'),fr('Classifier::RunFinal()')),'Classifier::OwnedSet(', *adapter,'GlyphPackageSourceReader::LoadNamedConfig(', 'Persistence::ObservePackageConfig(', 'Persistence::RunObservedPackageConfig()',976)
 total('existing_physical_append_stat',680,'::ClassifyNamespaceInto(','Classifier::RunFinal()', 'GlyphPackageSourceReader::AppendConfig(','::CompareAppendFiles(','::NextAppendField(',532)
 total('prepare_aggregate',168,'ProfileStore::PreparePackageTransaction(','::ComputePackageAggregate(', 'GlyphPackageSourceReader::Row(','GlyphPackageSourceReader::LoadNamedConfig(', 'Persistence::ObservePackageConfig(', 'Persistence::RunObservedPackageConfig()',1000,348)
 total('classify_directory',680,'::ClassifyNamespaceInto(','Classifier::Run()', 'GlyphPackageSourceReader::ObjectAt(', 'CheckedStorage::Enumerate(', 'lfs_dir_open','lfs_dir_find','lfs_dir_fetchmatch','lfs_dir_find_match',64,20)
 total('ordinary_loop_time_capture', 'main','loop','::mark_first_mode_ready()',64,408)
else:
 comparison='accepted separate branch proof covers evaluator; no startup directory-page families altered'
 total('ordinary.chord_full_depth', 'main','loop','::persist_ordinary_chord(', 'Persistence::LoadConfigChecked(',1208,24,300,348)
 total('managed.chord_unknown_skip','main','loop','::persist_managed_chord(', 'profile_selection::Persist<','Persistence::LoadConfigChecked(',1112,24,308,408)
 total('managed.menu_unknown_skip','main','loop','::service_profile_selection()', 'profile_selection::Persist<','Persistence::LoadConfigChecked(',1112,24,308,408)
 total('managed.physical_append', 'main','loop',max(fr('::service_profile_selection()'),fr('::persist_managed_chord(')), 'profile_selection::Persist<','Persistence::SaveConfigIfGenerationMatches(', 'Persistence::InitializeOrdinarySaveContext(', 'ProfileStore::BeginOrdinaryConfigWrite(', '::ClassifyNamespaceInto(','Classifier::RunFinal()', 'GlyphPackageSourceReader::AppendConfig(','::CompareAppendFiles(','::NextAppendField(',532,408)
 total('managed.gamecube_idle_wake','main','loop','GamecubeBackend::SendReport()', 'GamecubeConsole::WaitForPollStartBounded(', 'profile_selection::GamecubeSelectionPending()','managed_chord_held(',408)
 lower = ('pb_', 'lfs_', 'encode_', 'decode_', 'CheckedStorage::')
 assert {k for k in b if k.startswith(lower)} == {k for k in f if k.startswith(lower)}
 assert all(shape(b[k])==shape(f[k]) for k in b if k.startswith(lower))
 # Every storage-bearing chord branch returns through the same-frame-or-smaller
 # ordinary loop as the confirmed baseline. The source no longer nests IO
 # below select_mode. Enforce the shape here, not only in full campaign replay.
 def edges(key):
  hits=[k for k in f if key==k or (len(key)>4 and key in k and 'lambda' not in k)]
  assert len(hits)==1,(key,hits)
  return [a['name'] for a in f[hits[0]]['calls']+f[hits[0]]['tail']]
 assert any('::persist_ordinary_chord(' in x for x in edges('loop'))
 assert any('::persist_managed_chord(' in x for x in edges('loop'))
 assert not any('LoadConfig' in x or 'Persist<' in x for x in edges('::request_mode_destination('))
 assert any('managed_chord_held(' in x for x in edges('::GamecubeSelectionPending()'))
assert all(v<=2048 for v in routes.values()),routes
receipt=dict(source=a.resource.parent.name,lane=a.lane,elf_sha256=hashlib.sha256((a.resource.parent/'firmware.elf').read_bytes()).hexdigest(),
 baseline_sha256=hashlib.sha256(a.baseline_gz.read_bytes()).hexdigest(),changed=changed,added=added,removed=removed,affected_routes=routes,maximum_affected=max(routes.values()),
 inherited_legacy_SET_stage=2048,limit=2048,hardware=False)
a.output.write_text(json.dumps(receipt,indent=2)+'\n');print(routes)
