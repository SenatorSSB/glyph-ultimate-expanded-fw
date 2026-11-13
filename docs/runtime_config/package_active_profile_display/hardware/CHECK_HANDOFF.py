#!/usr/bin/env python3
"""Offline-only packet/resource/custody verifier. No serial, USB or build access."""
from pathlib import Path
import copy,gzip,hashlib,json,stat,sys,subprocess
HERE=Path(__file__).resolve().parent
OUT=HERE.parent
ROOT=OUT.parents[2]
def need(value,why):
 if not value:raise ValueError(why)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def packet_rules(p):
 need(p['status']=='FINAL_PROPOSAL_UNAPPROVED_NON_EXECUTABLE' and p['owner_approval'] is None,'proposal not approved')
 need(p['built_source_sha']=='9e69188d857138a3884bcbe243f22188815e9355' and p['no_rebuild_or_substitution'],'built source')
 limits=p['limits'];need((limits['controller_exchanges'],limits['configurator_sessions'],limits['xinput_identity_sessions'],limits['manual_candidate_installs'])==(70,2,2,1),'operation bounds')
 for key in ['CREATE','QUERY_PACKAGE','protocol2_STATUS','profile_mutations','reference_rewrites','default_or_backend_changes','managed_selection_or_activation','automatic_retries_or_reconnects','automatic_rollback_or_recovery']:need(limits[key]==0,'forbidden operation '+key)
 ops=p['request_allowlist'];need([x['stage'] for x in ops]==['pre_snapshot','first_xinput_boot','post_snapshot','final_xinput_boot'],'stage order')
 snap=ops[0]['operations'];need([(v['command'],v.get('protocol'),v['operation'],v['count']) for v in snap]==[(10,None,'CONFIGURATOR_RUNTIME_IDENTITY',1),(9,3,'PACKAGE_STATUS',1),(3,None,'GET_CONFIG',1),(9,2,'LIST',4),(9,2,'READ',27)],'snapshot allowlist')
 need(sum(x['count'] for x in snap)==34 and ops[2]['same_operations_as']=='pre_snapshot' and ops[2]['count']==34,'snapshot count')
 need(2*34+sum(ops[i]['operations'][0]['count'] for i in [1,3])==70,'complete request count')
 need(all(x['count']==1 and x['operation']=='FIXED_RUNTIME_IDENTITY_XINPUT' for i in [1,3] for x in ops[i]['operations']),'identity count')
 need(p['transport']['deadlines_ms']=={'identity':10000,'each_other_request':30000},'finite deadlines')
def run():
 p=read(HERE/'packet.json');packet_rules(p)
 m=read(HERE/'PREPARATION_MANIFEST.json')
 for relative,v in m.items():
  file=OUT/relative;need(file.is_file() and sha(file)==v['sha256'] and file.stat().st_size==v['bytes'],'manifest '+relative)
 handoff=read(HERE/'HANDOFF.json');need(handoff['packet_sha256']==sha(HERE/'packet.json') and handoff['preparation_manifest_sha256']==sha(HERE/'PREPARATION_MANIFEST.json'),'handoff identity')
 resource=OUT/'resource';rm=read(resource/'MANIFEST.json')
 for name,v in rm.items():need(sha(resource/name)==v['sha256'] and (resource/name).stat().st_size==v['bytes'],'resource '+name)
 need(p['resource_manifest_sha256']==sha(resource/'MANIFEST.json'),'packet/resource binding')
 proof=read(resource/'stack-impact-summary.json');graph=read(resource/'current-core1-bound-graph.json')
 need(not graph['unknown'] and proof['unknown']==[],'unresolved graph edges')
 need(proof['new_resolver_subtree_bound']==64 and sum(proof['new_label_loop_path'][x] for x in ['core1_wrapper','main1','loop1','IntegratedDisplay::SendReport','UpdateDisplay','current_profile_label_including_children','core1_IRQ_including_alignment'])==292,'label composition')
 need(16+72+24+graph['bounds']['InputDisplay::UpdateDisplay(IntegratedDisplay*, Adafruit_GFX&)']['bound']+68==948,'viewer composition')
 need(16+72+24+graph['bounds']['MenuButtonHints::UpdateDisplay(IntegratedDisplay*, Adafruit_GFX&)']['bound']+68==948,'dashboard composition')
 need(16+max(graph['bounds']['setup1']['bound'],graph['bounds']['loop1']['bound'])+68==1060<=proof['retained_core1_upper']<=proof['stack1_reservation'],'core1 composition/reservation')
 need(proof['source_pin_matches']==89 and proof['source_pin_rows']==90 and 'SSD1306' in proof['source_pin_exception'],'qualified source exception')
 # Verify originals in owner-held custody, never a mutable build directory.
 for name,v in p['artifacts'].items():
  file=Path(v['custody']);need(file.is_absolute(),'absolute custody')
  for parent in [file,*file.parents]:need(not parent.is_symlink(),'symlinked custody')
  need(stat.S_ISREG(file.lstat().st_mode) and file.stat().st_size==v['bytes'] and sha(file)==v['sha256'],'custody '+name)
 need(p['artifacts']['firmware.elf']['sha256']==proof['elf_sha256'] and p['artifacts']['firmware.map']['sha256']==proof['map_sha256'],'resource/artifact identity')
 need(p['baseline_binding_sha256']==sha(HERE/'BASELINE_BINDING.json'),'baseline binding')
 b=read(HERE/'BASELINE_BINDING.json');need((b['directory_entries'],b['store_generation'],b['selected_legacy_record']['reference'],b['selected_legacy_record']['row_zero_based'])==(27,229,53,2),'fixed legacy route')
 need(b['selected_legacy_record']['expected_plate_label']=='Unknown Plate' and b['managed_record_not_selected']['physical_display_status']=='NOT_TESTED_HOST_ONLY','reachable/host distinction')
 for f,digest in p['source_pins'].items():need(sha(ROOT/f)==digest,'source pin '+f)
 # Negative controls exercise authority/operation boundaries without hardware.
 rejected=0
 for key,value in [('reference_rewrites',1),('controller_exchanges',71),('CREATE',1),('managed_selection_or_activation',1)]:
  bad=copy.deepcopy(p);bad['limits'][key]=value
  try:packet_rules(bad)
  except ValueError:rejected+=1
 bad=copy.deepcopy(p);bad['request_allowlist'][0]['operations'][1]['operation']='CREATE_PACKAGE'
 try:packet_rules(bad)
 except ValueError:rejected+=1
 need(rejected==5,'negative controls')
 print(json.dumps({'result':'PASS_OFFLINE_ONLY','packet_id':p['packet_id'],'packet_sha256':sha(HERE/'packet.json'),'preparation_manifest_sha256':sha(HERE/'PREPARATION_MANIFEST.json'),'resource_manifest_sha256':sha(resource/'MANIFEST.json'),'all4_retained_artifacts':'HASH_SIZE_NONSYMLINK_MATCH','affected_rendering_bound_bytes':948,'new_label_path_bytes':292,'core1_composition_bytes':1060,'negative_controls_rejected':rejected,'hardware_access':False,'rebuild':False},indent=2))
if __name__=='__main__':run()
