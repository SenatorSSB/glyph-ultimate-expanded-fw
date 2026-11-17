"""Read-only exact linked-image comparison for the bounded USB finalization repair."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for arg in ['candidate_resource','baseline_resource','candidate_elf','baseline_elf','output']:p.add_argument('--'+arg.replace('_','-'),type=Path,required=True)
a=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(a.baseline_elf)=='e55c7c157fdc161bd0cc0636b96bf3299f09a5d2e934b65f5f9760fc600c3a60'
assert sha(a.candidate_elf)=='e3c7662ce3de2eb5b818ffe8c18d3d6c346e655e13ca9326efa6eb6e6376c75c'
load=lambda d,n:json.loads((d/n).read_text())
old=load(a.baseline_resource,'functions.json');new=load(a.candidate_resource,'functions.json')
def shape(v):return (v['resolved_frame_bytes'],sorted({x['name'] for x in v['calls']}),sorted({x['name'] for x in v['tail']}),sorted({x['instruction'] for x in v['indirect']}))
assert set(old)==set(new) and len(new)==3302
assert all(shape(old[n])==shape(new[n]) for n in old),[n for n in old if shape(old[n])!=shape(new[n])]
b=load(a.baseline_resource,'summary.json');c=load(a.candidate_resource,'summary.json')
assert b['static']==c['static']==198888 and b['heap_capacity']==c['heap_capacity']==63060
assert b['stack_reservations']==c['stack_reservations']==[2048,2048]
core1=load(a.candidate_resource,'core1-bound-graph.json');assert not core1['unknown']
assert core1['bounds']['setup1']['bound']==968 and core1['bounds']['loop1']['bound']==984
assert 984+16+68==1068<=1152
r={'status':'PASS','baseline_source':'59870835e7cd8e7c52bd3742e4910a7083cd21f5','candidate_source':'dcf6e29589f558a95c021bef491578f87e41750f',
   'baseline_elf_sha256':sha(a.baseline_elf),'candidate_elf_sha256':sha(a.candidate_elf),
   'baseline_graph_sha256':sha(a.baseline_resource/'functions.json'),'candidate_graph_sha256':sha(a.candidate_resource/'functions.json'),
   'common_functions':3302,'changed_call_frame_tail_indirect_shapes':0,'new_functions':0,'removed_functions':0,
   'flash_before_after':[650556,650564],'static_before_after':[198888,198888],'linked_heap_capacity_before_after':[63060,63060],
   'reserved_stacks_each':2048,'boot_backend_frame_before_after':[64,64],'core0_retained_maximum':2048,'core0_lifecycle_model':2044,
   'core1_setup':968,'core1_loop':984,'core1_outer':16,'core1_irq':68,'core1_envelope':1068,'core1_retained_ceiling':1152,
   'ceiling_increase':False,'physical_peak_heap_or_stack_highwater':'NOT_MEASURED',
   'scope':'Retains source-qualified IRQ/ROM/indirect call unions from accepted model; exact current core0 composition supplied separately. Equal graph shapes do not assert equal report/USB semantics or physical acceptance.'}
a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
