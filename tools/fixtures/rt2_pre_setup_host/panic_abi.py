"""Assemble production veneer text; execute its Thumb instructions in a narrow
instruction model with a hostile but AAPCS-conforming observer. This is modeled
ABI evidence; final target C++ naked-function disassembly is a separate gate.
"""
import ast,hashlib,re,struct,subprocess
from pathlib import Path
TOOLCHAIN=Path.home()/'.platformio/packages/toolchain-rp2040-earlephilhower/bin'
def run(args):
 return subprocess.check_output([str(x) for x in args],stderr=subprocess.STDOUT,text=True)
def check(root,temp):
 source=(root/'HAL/pico/src/core/RecoveryUsbDiagnostics.cpp').read_text()
 body=source[source.index('void __wrap_panic('):]
 body=body[body.index('asm volatile(')+len('asm volatile('):body.index(');')]
 asm=''.join(ast.literal_eval(x) for x in re.findall(r'"(?:\\.|[^"\\])*"',body))
 path=temp/'panic-abi.S';obj=temp/'panic-abi.elf';binary=temp/'panic-abi.bin'
 path.write_text('.syntax unified\n.cpu cortex-m0plus\n.thumb\n.text\n.global __wrap_panic\n.thumb_func\n__wrap_panic:\n'+asm+'\n.global GlyphObserveUsbPanic\n.thumb_func\nGlyphObserveUsbPanic:\nbx lr\n.section .realpanic,"ax"\n.global __real_panic\n.thumb_func\n__real_panic:\nb .\n')
 run([TOOLCHAIN/'arm-none-eabi-gcc','-mcpu=cortex-m0plus','-mthumb','-nostdlib','-Wl,-e,__wrap_panic','-Wl,-Ttext=0x10000000','-Wl,--section-start=.realpanic=0x10090000',path,'-o',obj])
 disassembly=run([TOOLCHAIN/'arm-none-eabi-objdump','-d',obj]);symbols={line.split()[-1]:int(line.split()[0],16) for line in run([TOOLCHAIN/'arm-none-eabi-nm',obj]).splitlines() if len(line.split())==3}
 run([TOOLCHAIN/'arm-none-eabi-objcopy','-O','binary','--only-section=.text',obj,binary]);code=binary.read_bytes();base=symbols['__wrap_panic']
 trials=0
 for nargs in [0,1,2,3,4,5,8,21,22,25,31,40]:
  for seed in range(4):
   args=[(0x6a000000+seed*0x100000+i*0x10103)&0xffffffff for i in range(nargs)]
   # Includes alternating aligned64-bit pairs and surrounding canary words.
   stack=[0xdada0000+i for i in range(64)]
   for i,arg in enumerate(args[3:]):stack[i]=arg
   initial_sp=0x20001000+8*seed;initial_lr=0x10070001+4*seed
   regs=[0x44440000+i for i in range(16)];regs[0]=0x10080000+seed*4
   for i,arg in enumerate(args[:3]):regs[i+1]=arg
   regs[13]=initial_sp;regs[14]=initial_lr;regs[15]=base
   before=regs[:];memory={initial_sp+i*4:w for i,w in enumerate(stack)};original=dict(memory);observed=real=0;steps=0
   def word(address):
    if base<=address<=base+len(code)-4:return struct.unpack_from('<I',code,address-base)[0]
    return memory[address]
   while steps<20:
    pc=regs[15];h=struct.unpack_from('<H',code,pc-base)[0];steps+=1;regs[15]+=2
    if h&0xfe00==0xb400:
     selected=[i for i in range(8) if h&(1<<i)]+([14] if h&0x100 else []);regs[13]-=4*len(selected)
     for i,r in enumerate(selected):memory[regs[13]+4*i]=regs[r]
    elif h&0xf800==0xf000:
     lo=struct.unpack_from('<H',code,pc-base+2)[0];assert lo&0xd000==0xd000
     s=(h>>10)&1;i1=1^((lo>>13)&1)^s;i2=1^((lo>>11)&1)^s
     delta=(s<<24)|(i1<<23)|(i2<<22)|((h&1023)<<12)|((lo&2047)<<1)
     if s:delta-=1<<25
     assert pc+4+delta==symbols['GlyphObserveUsbPanic'];assert regs[13]%8==0
     assert regs[0]==before[0];observed+=1
     for r in [0,1,2,3,12]:regs[r]=0xbad00000+r
     regs[14]=(pc+4)|1;regs[15]=pc+4
    elif h&0xf800==0x9800:regs[(h>>8)&7]=word(regs[13]+(h&255)*4)
    elif h&0xf800==0x4800:regs[(h>>8)&7]=word(((pc+4)&~3)+(h&255)*4)
    elif h&0xff00==0x4600:regs[(h&7)|((h>>4)&8)]=regs[(h>>3)&15]
    elif h&0xfe00==0xbc00:
     selected=[i for i in range(8) if h&(1<<i)];assert not h&0x100
     for i,r in enumerate(selected):regs[r]=word(regs[13]+4*i)
     regs[13]+=4*len(selected)
    elif h&0xff80==0xb000:regs[13]+=(h&127)*4
    elif h&0xff87==0x4700:
     target=regs[(h>>3)&15];assert target&1;assert target&~1==symbols['__real_panic'];real+=1;break
    else:raise AssertionError('unexpected production veneer instruction '+hex(h))
   assert observed==real==1 and regs[13]==initial_sp and regs[14]==initial_lr
   assert regs[:12]==before[:12] # restored args and all callee-saved registers
   assert all(memory[a]==w for a,w in original.items()) # all stack varargs/canaries exact
   actual=regs[1:4]+[word(initial_sp+i*4) for i in range(max(0,nargs-3))]
   assert actual[:nargs]==args
   trials+=1
 return {'status':'PASS','execution':'MODELED_ABI_actual_assembled_Thumb_instructions','trials':trials,'maximum_variadic_words':40,'stack_argument_alignment_bytes':8,'veneer_stack_bytes_during_observer':24,'veneer_stack_bytes_after_tail':0,'observer_calls':1,'real_panic_tail_calls':1,'assembly_sha256':hashlib.sha256(asm.encode()).hexdigest(),'assembled_text_sha256':hashlib.sha256(code).hexdigest(),'disassembly':disassembly,'limitation':'Final target C++ naked function and link relocations require separate ELF disassembly audit; no device execution claimed.'}
