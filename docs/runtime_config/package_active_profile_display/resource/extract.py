#!/usr/bin/env python3
"""Exact ARM ELF graph/section/vtable evidence, using sealed predecessor extractor."""
import argparse,subprocess,json,hashlib,struct,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--toolchain',type=Path,required=True);a=ap.parse_args()
e=a.elf;o=a.output_dir;o.mkdir(parents=True,exist_ok=True)
for tool,args,name in [('nm',['-n','-S','-C'],'symbols.txt'),('objdump',['-d','-C'],'disassembly.txt'),('size',['-A'],'sections-size.txt'),('readelf',['-A'],'elf-attributes.txt')]:
 p=a.toolchain/('arm-none-eabi-'+tool)
 (o/name).write_bytes(subprocess.run([str(p),*args,str(e)],check=True,capture_output=True).stdout)
subprocess.run(['python3',str(Path(__file__).with_name('extract_linked_functions.py')),'--elf',str(e),'--output-dir',str(o)],check=True)
b=e.read_bytes();off=struct.unpack_from('<I',b,32)[0];es,n,st=struct.unpack_from('<HHH',b,46);ss=[struct.unpack_from('<10I',b,off+i*es) for i in range(n)];s=ss[st];names=b[s[4]:s[4]+s[5]]
secs={names[s[0]:].split(b'\0')[0].decode():{'type':s[1],'address':s[3],'size':s[5],'offset':s[4]} for s in ss}
def at(addr,n):
 for s in secs.values():
  if s['type']!=8 and s['address']<=addr and addr+n<=s['address']+s['size']:return b[s['offset']+addr-s['address']:s['offset']+addr-s['address']+n]
 raise KeyError(hex(addr))
syms=[]
for line in (o/'symbols.txt').read_text().splitlines():
 m=re.match(r'([\da-f]+) (?:([\da-f]+) )?([a-zA-Z]) (.*)',line)
 if m:syms.append(dict(address=int(m[1],16),size=int(m[2],16) if m[2] else 0,type=m[3],name=m[4]))
byaddr={}
for s in syms:
 if s['type'] in 'TtWw':byaddr.setdefault(s['address'],[]).append(s['name'])
v={}
for s in syms:
 if s['name'].startswith('vtable for '):
  vals=struct.unpack('<'+'I'*(s['size']//4),at(s['address'],s['size']))
  v[s['name']]=[dict(offset_from_vptr=4*i-8,value=hex(x),name=(byaddr.get(x&~1) or [None])[0],aliases=byaddr.get(x&~1,[])) for i,x in enumerate(vals)]
(o/'vtables.json').write_text(json.dumps(v,indent=2)+'\n');(o/'symbols.json').write_text(json.dumps(syms,indent=2)+'\n')
byname={s['name']:s for s in syms};startup={}
for prefix in ['preinit','init']:
 start=byname['__'+prefix+'_array_start']['address'];end=byname['__'+prefix+'_array_end']['address']
 startup[prefix]=[byaddr.get(struct.unpack('<I',at(addr,4))[0]&~1,[]) for addr in range(start,end,4)]
(o/'startup.json').write_text(json.dumps(startup,indent=2)+'\n')
summary=dict(elf=str(e),elf_sha256=hashlib.sha256(b).hexdigest(),elf_bytes=len(b),sections=secs,static=secs['.data']['size']+secs['.bss']['size'],stack_reservations=[secs[s]['size'] for s in ['.stack_dummy','.stack1_dummy']],heap_start=secs['.heap']['address'],heap_capacity=0x20040000-secs['.heap']['address'])
(o/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
