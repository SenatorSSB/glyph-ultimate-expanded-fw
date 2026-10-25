import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--old',required=True);p.add_argument('--new',required=True);p.add_argument('--output',required=True);a=p.parse_args()
o=json.loads(Path(a.old).read_text());n=json.loads(Path(a.new).read_text())
def normalize(name):
 if name.endswith('_veneer'):name=name[:-7]
 name=name.lstrip('_')
 if name.startswith('wrap_'):name=name[5:].lstrip('_')
 if name in ('aeabi_memcpy','aeabi_memcpy4','aeabi_memcpy8'):name='memcpy'
 return name
def signature(v):return (v['resolved_frame_bytes'],[normalize(c['name']) for c in v['calls']],[c['instruction'] for c in v['indirect']],[normalize(c['name']) for c in v['tail']])
r={'classification':'PRELIMINARY_GRAPH_CORRESPONDENCE_REQUIRES_SOURCE_ALIAS_CALLBACK_AND_ROUTE_REVIEW','same':[],'changed':[],'missing':sorted(o.keys()-n.keys()),'added':sorted(n.keys()-o.keys())}
for name in sorted(o.keys()&n.keys()):
 x,y=o[name],n[name]
 if signature(x)==signature(y):r['same'].append(name)
 else:r['changed'].append({'name':name,'old':signature(x),'new':signature(y)})
Path(a.output).write_text(json.dumps(r,indent=2)+'\n')
print({k:len(v) for k,v in r.items() if isinstance(v,list)})
