import argparse
_ap=argparse.ArgumentParser();_ap.add_argument("--elf",required=True);_ap.add_argument("--output-dir",required=True);_aa=_ap.parse_args()
import re,json,struct,bisect
from pathlib import Path
elf=Path(_aa.elf).read_bytes()
# Section mapping preserves read-only load addresses; ELF32 LE.
shoff=struct.unpack_from('<I',elf,32)[0];shentsize,shnum=struct.unpack_from('<HH',elf,46)
sections=[]
for i in range(shnum):
 sh=struct.unpack_from('<10I',elf,shoff+i*shentsize);sections.append(sh)
def bytesat(addr,n):
 for sh in sections:
  if sh[3]<=addr and addr+n<=sh[3]+sh[5]:return elf[sh[4]+addr-sh[3]:sh[4]+addr-sh[3]+n]
 raise KeyError(hex(addr))
syms=[];byname={}
for l in (Path(_aa.output_dir)/'symbols.txt').read_text().splitlines():
 m=re.match(r'([\da-f]+) (?:([\da-f]+) )?([a-zA-Z]) (.*)',l)
 if not m:continue
 a=int(m[1],16);sz=int(m[2],16) if m[2] else 0;typ=m[3];name=m[4];s={'address':a,'size':sz,'type':typ,'name':name};syms.append(s);byname[name]=s
fnsyms=[s for s in syms if s['type'] in 'TtWw' and 0x10000000<=s['address']<0x20042000]
# aliases are retained; exact symbol size is authoritative for C++ template bodies.
addrnames={}
for s in fnsyms:addrnames.setdefault(s['address'],[]).append(s['name'])
starts=sorted(addrnames)
def owner(a):
 i=bisect.bisect_right(starts,a)-1
 if i<0:return None
 names=addrnames[starts[i]]
 exact=[byname[n] for n in names if byname[n]['size'] and a<starts[i]+byname[n]['size']]
 return (max(exact,key=lambda s:s['size']) if exact else byname[names[0]])['name']
ins=[]
for l in (Path(_aa.output_dir)/'disassembly.txt').read_text().splitlines():
 m=re.match(r'([\da-f]+):\s+((?:[\da-f]{4,8}\s+)+)\s*(.*?)\s*$',l)
 if m:ins.append((int(m[1],16),m[3],l))
addresses=[x[0] for x in ins];funcs={}
for s in fnsyms:
 start=s['address'];end=start+s['size'] if s['size'] else (starts[bisect.bisect_right(starts,start)] if bisect.bisect_right(starts,start)<len(starts) else start)
 rows=ins[bisect.bisect_left(addresses,start):bisect.bisect_left(addresses,end)];frame=0;calls=[];ind=[];tail=[];stack=[];internal=[]
 for a,asm,line in rows:
  if re.match(r'(push|sub\s+sp|add\s+sp|mov\s+sp|stmdb\s+sp)',asm):stack.append(line)
  if asm.startswith('push'):
   regs=re.search(r'\{([^}]+)\}',asm)[1].split(', ');c=0
   for r in regs:
    mm=re.match(r'r(\d+)-r(\d+)',r);c+=(int(mm[2])-int(mm[1])+1) if mm else 1
   frame+=c*4
  m=re.match(r'sub\s+sp, #(\d+)',asm)
  if m:frame+=int(m[1])
  m=re.match(r'(bl|blx|b\.n|b\.w)\s+([\da-f]+)\s+<(.*)>',asm)
  if m:
   dst=int(m[2],16)
   if m[1].startswith('bl'):
    if start < dst < end:internal.append({'at':hex(a),'to':hex(dst),'reason':'INTRA_SYMBOL_CONTROL_FLOW_NO_CALLEE_FRAME'})
    else:calls.append({'at':hex(a),'to':hex(dst),'name':owner(dst) or m[3]})
   elif not start<=dst<end:tail.append({'at':hex(a),'to':hex(dst),'name':owner(dst) or m[3]})
  elif re.match(r'blx?\s+',asm):ind.append({'at':hex(a),'instruction':asm})
 funcs[s['name']]={'address':hex(start),'end':hex(end),'symbol_size':s['size'],'allocation_inventory':frame,'calls':calls,'internal_control_calls':internal,'indirect':ind,'tail':tail,'stack_instructions':stack}

# Resolve literal-loaded negative ADDSP prologue allocations, e.g. hash_file620.
for name,f in funcs.items():
 rows=ins[bisect.bisect_left(addresses,int(f['address'],16)):bisect.bisect_left(addresses,int(f['end'],16))]; literals={}; extra=[]
 for a,asm,line in rows:
  m=re.match(r'ldr\s+(r\d+), \[pc, #\d+\].*@ \(([\da-f]+)',asm)
  if m:
   try:literals[m[1]]=struct.unpack('<i',bytesat(int(m[2],16),4))[0]
   except:pass
  m=re.match(r'add\s+sp, (r\d+)',asm)
  if m and m[1] in literals and literals[m[1]]<0:extra.append({'at':hex(a),'literal_delta':literals[m[1]]})
 f['negative_literal_SP_allocations']=extra;f['resolved_frame_bytes']=f['allocation_inventory']-sum(e['literal_delta'] for e in extra)
(Path(_aa.output_dir)/'functions.json').write_text(json.dumps(funcs,indent=2)+'\n')
