#!/usr/bin/env python3
"""Read-only linked ELF extraction; writes only an explicit private output dir."""
import argparse,subprocess,json,hashlib,struct,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--elf',required=True);ap.add_argument('--output-dir',required=True);ap.add_argument('--toolchain',default='/private/tmp/glyph-native-selector-liveness-20261022/.platformio-home/packages/toolchain-rp2040-earlephilhower/bin');a=ap.parse_args()
e=Path(a.elf);o=Path(a.output_dir);o.mkdir(parents=True,exist_ok=True)
for tool,args,out in [('nm',['-n','-S','-C'],'symbols.txt'),('objdump',['-d','-C','--no-show-raw-insn'],'disassembly-no-bytes.txt'),('objdump',['-d','-C'],'disassembly.txt'),('size',['-A'],'sections-size.txt'),('readelf',['-A'],'elf-attributes.txt')]:
 r=subprocess.run([str(Path(a.toolchain)/('arm-none-eabi-'+tool)),*args,str(e)],check=True,capture_output=True);(o/out).write_bytes(r.stdout)
subprocess.run(['python3','/private/tmp/glyph-selector-resource-audit-20261022/extract_linked_functions.py','--elf',str(e),'--output-dir',str(o)],check=True)
subprocess.run(['python3','/private/tmp/glyph-selector-resource-audit-20261022/compare_linked_graphs.py','--old','/private/tmp/glyph-selector-resource-audit-20261022/exact4898/functions.json','--new',str(o/'functions.json'),'--output',str(o/'graph-delta.json')],check=True)
b=e.read_bytes();shoff=struct.unpack_from('<I',b,32)[0];shentsize,shnum,si=struct.unpack_from('<HHH',b,46)
S=[struct.unpack_from('<10I',b,shoff+i*shentsize) for i in range(shnum)];strings=b[S[si][4]:S[si][4]+S[si][5]]
secs={strings[s[0]:].split(b'\0',1)[0].decode():{'size':s[5],'address':s[3]} for s in S}
def read(addr,n):
 for s in S:
  if s[1]!=8 and s[3]<=addr and addr+n<=s[3]+s[5]:return b[s[4]+addr-s[3]:s[4]+addr-s[3]+n]
 raise ValueError(hex(addr))
syms=[]
for l in (o/'symbols.txt').read_text().splitlines():
 m=re.match(r'([\da-f]+) (?:([\da-f]+) )?([a-zA-Z]) (.*)',l)
 if m:syms.append({'address':int(m[1],16),'size':int(m[2],16) if m[2] else 0,'type':m[3],'name':m[4]})
byaddr={}
for s in syms:
 if s['type'] in 'TtWw':byaddr.setdefault(s['address'],[]).append(s['name'])
v={}
for s in syms:
 if s['name'].startswith('vtable for '):
  vals=struct.unpack('<'+'I'*(s['size']//4),read(s['address'],s['size']))
  v[s['name']]=[{'offset_from_vptr':4*i-8,'value':hex(x),'name':(byaddr.get(x&~1) or [None])[0],'aliases':byaddr.get(x&~1,[])} for i,x in enumerate(vals)]
(o/'vtables.json').write_text(json.dumps(v,indent=2)+'\n');(o/'symbols.json').write_text(json.dumps(syms,indent=2)+'\n')
startup={}
byname={s['name']:s for s in syms}
for prefix in ['preinit','init']:
 start=byname['__'+prefix+'_array_start']['address'];end=byname['__'+prefix+'_array_end']['address']
 startup[prefix]=[{'slot':hex(addr),'names':byaddr.get(struct.unpack('<I',read(addr,4))[0]&~1,[])} for addr in range(start,end,4)]
(o/'startup.json').write_text(json.dumps(startup,indent=2)+'\n')
oldsyms=json.loads(Path('/private/tmp/glyph-selector-resource-audit-20261022/exact4898/symbols.json').read_text())
# Old sealed symbols are keyed by name. Preserve actual records; compare size/type only, addresses may relocate.
if isinstance(oldsyms,dict): oldsym={name:rec for name,rec in oldsyms.items()}
else: oldsym={rec['name']:rec for rec in oldsyms}
newsyms={rec['name']:rec for rec in syms}
(o/'writable-symbol-delta.json').write_text(json.dumps({'old_only':[rec for name,rec in oldsym.items() if rec['type'] in 'BbDd' and name not in newsyms], 'new_only':[rec for name,rec in newsyms.items() if rec['type'] in 'BbDd' and name not in oldsym], 'changed':[{'name':name,'old':oldsym[name],'new':rec} for name,rec in newsyms.items() if rec['type'] in 'BbDd' and name in oldsym and (rec['size'],rec['type'])!=(oldsym[name]['size'],oldsym[name]['type'])]},indent=2)+'\n')
static=secs['.data']['size']+secs['.bss']['size']
(o/'elf-summary.json').write_text(json.dumps({'elf':str(e),'elf_sha256':hashlib.sha256(b).hexdigest(),'elf_bytes':len(b),'sections':secs,'data_plus_bss':static,'static_limit':199632,'remaining_static':199632-static},indent=2)+'\n')
print('ELF',hashlib.sha256(b).hexdigest(),'static',static)
