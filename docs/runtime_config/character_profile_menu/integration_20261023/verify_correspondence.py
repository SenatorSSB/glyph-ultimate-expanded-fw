from pathlib import Path
import subprocess,json,hashlib
WD=Path(__file__).resolve().parents[4]
F='1de243c7bada73ba85843018058b4f66a06acdda';E='2b0da786dc4832c9575c1a8448f25279b0d2799e';I='b8f9d14079e0930e2e4616c2df7923be564255f6';BASE='55ab5984f47728db53a12665d685d16cfad39201'
def git(*a):return subprocess.check_output(['git',*a],cwd=WD)
def tree(ref):
 out={}
 for row in git('ls-tree','-rz',ref).split(b'\0'):
  if not row:continue
  h,p=row.split(b'\t',1);mode,kind,oid=h.decode().split();p=p.decode()
  if not p.startswith('docs/'):out[p]={'mode':mode,'kind':kind,'object':oid}
 return out
f,e,i,b=map(tree,(F,E,I,BASE))
assert e==b,'E includes non-doc drift'
assert i==f,'I differs from exact tested non-doc tree'
assert git('show','-s','--format=%P',I).decode().strip().split()==[E,F]
assert subprocess.run(['git','merge-base','--is-ancestor',F,E],cwd=WD).returncode==1
assert subprocess.run(['git','merge-base','--is-ancestor',F,I],cwd=WD).returncode==0
assert git('rev-parse',F+'^{tree}').decode().strip()=='5a25a83705a654480b8db805f20822f4d180d70f'
for ref in (E,I):assert git('show',ref+':docs/runtime_config/character_profile_menu/hardware_20261023/evidence.json')==git('show',E+':docs/runtime_config/character_profile_menu/hardware_20261023/evidence.json')
objects=[v['object'] for v in f.values() if v['kind']=='blob'];raw=subprocess.check_output(['git','cat-file','--batch'],cwd=WD,input=('\n'.join(objects)+'\n').encode());pos=0;hashes={}
for oid in objects:
 end=raw.index(b'\n',pos);head=raw[pos:end].decode().split();size=int(head[2]);blob=raw[end+1:end+1+size];hashes[oid]=hashlib.sha256(blob).hexdigest();pos=end+size+2
entries=[{'path':p,**v,'sha256':hashes.get(v['object'])} for p,v in sorted(f.items())]
changed=[p for p in sorted(set(f)|set(b)) if f.get(p)!=b.get(p)]
assert changed==['src/core/profile_selection.cpp','tools/fixtures/controller_profile_selector/metadata_menu.cpp','tools/fixtures/controller_profile_selector/selection_persistence.cpp']
out=WD/'docs/runtime_config/character_profile_menu/integration_20261023';assert out.is_dir()
catalog={'schema_name':'glyph_character_menu_exact_tested_transition','schema_version':1,'candidate_F':F,'source_free_acceptance_E':E,'actual_integration_I':I,'prior_canonical':BASE,'integration_parents':[E,F],'candidate_tree':'5a25a83705a654480b8db805f20822f4d180d70f','result':'PASS_EXACT_TESTED_NON_DOC_TREE','source_free_E':'PASS_BASELINE_NON_DOC_TREE_EXACT_F_NOT_ANCESTOR','critical_path_count':len(entries),'catalog_includes':'Every tracked non-doc path, including firmware/HAL/headers/schema/build config/host tools/tests/canonical profiles and Git modes/object identities','critical_paths':entries,'changed_non_doc_paths_from_baseline':changed,'active_firmware_source_delta':['src/core/profile_selection.cpp'],'documentation_merge_resolution':'Accepted E versions preserved for OWNER_PACKET.md,README.md,ledger.json,validation.json; no source conflict','accepted_hardware_evidence':'git-json:'+E+':docs/runtime_config/character_profile_menu/hardware_20261023/evidence.json','accepted_hardware_evidence_sha256':hashlib.sha256(git('show',E+':docs/runtime_config/character_profile_menu/hardware_20261023/evidence.json')).hexdigest(),'accepted_E_immutable_at_I':True,'new_firmware_build':False,'new_flash':False,'Kazuya_activation':'NO','Kazuya_gameplay':'NOT_TESTED'}
assert json.loads((out/'CORRESPONDENCE.json').read_text())==catalog, 'committed transition catalog differs'
print('PASS exact',len(entries),'tracked non-doc inputs; real I parents E,F; source-free E; immutable hardware evidence')
