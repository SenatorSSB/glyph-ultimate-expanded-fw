#!/usr/bin/env python3
"""Model stack watermark bounds; compile actual diagnostic TU with pinned ARM."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]
ARM=Path.home()/'.platformio/packages/toolchain-rp2040-earlephilhower/bin/arm-none-eabi-g++'
NM=ARM.with_name('arm-none-eabi-nm')
def run(command):
 p=subprocess.run(list(map(str,command)),cwd=ROOT,text=True,capture_output=True,timeout=60)
 if p.returncode:raise AssertionError(p.stdout+p.stderr)
 return p.stdout

def main():
 with tempfile.TemporaryDirectory(prefix='glyph-resources-') as directory:
  temp=Path(directory)
  harness=temp/'watermark.cpp';harness.write_text('''#include "core/StackWatermark.hpp"
#include "core/ResourceDiagnostics.hpp"
#include <cassert>
int main(){uint32_t memory[20]={};memory[0]=11;memory[19]=22;
glyph_resource::fill_stack_watermark(memory+1,memory+19);
assert(memory[0]==11&&memory[19]==22);
assert(glyph_resource::scan_stack_watermark(memory+1,memory+19)==72);
memory[8]=0;assert(glyph_resource::scan_stack_watermark(memory+1,memory+19)==28);
memory[1]=0;assert(glyph_resource::scan_stack_watermark(memory+1,memory+19)==0);
assert(!ReadResourceDiagnostics().resource_diagnostics_enabled);}
''')
  exe=temp/'model';run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I',ROOT/'include',harness,'-o',exe]);run([exe])
  (temp/'pico').mkdir();(temp/'hardware').mkdir()
  (temp/'Arduino.h').write_text('#pragma once\n')
  (temp/'pico/multicore.h').write_text('#pragma once\ninline unsigned get_core_num(){return *reinterpret_cast<volatile unsigned*>(0xd0000000u);}\n')
  (temp/'hardware/sync.h').write_text('#pragma once\n#include <cstdint>\ninline uint32_t save_and_disable_interrupts(){uint32_t r;asm volatile("mrs %0, primask\\n cpsid i":"=r"(r)::"memory");return r;}\ninline void restore_interrupts(uint32_t r){asm volatile("msr primask, %0"::"r"(r):"memory");}\n')
  for enabled in (0,1):
   target=temp/('resource'+str(enabled)+'.o')
   run([ARM,'-std=gnu++17','-mcpu=cortex-m0plus','-mthumb','-O3','-fstack-usage','-ffunction-sections','-fdata-sections','-DGLYPH_RESOURCE_DIAGNOSTICS='+str(enabled),'-DGLYPH_STRICT_HARDENING_CANDIDATE='+str(enabled),'-I',temp,'-I',ROOT/'include','-c',ROOT/'HAL/pico/src/core/ResourceDiagnostics.cpp','-o',target])
   symbols=run([NM,'-S',target])
   if enabled:
    assert '__wrap__sbrk' in symbols
    assert ' U __atomic' not in symbols,'Atomic samples must compile to native loads/stores, not library locks'
    rows=target.with_suffix('.su').read_text().splitlines()
    init=next(row for row in rows if 'InitializeResourceDiagnosticsCore' in row)
    frame=int(init.split('\t')[1]);assert frame<64,init
    bss=sum(int(match.group(1),16) for match in re.finditer(r'^[0-9a-f]+ ([0-9a-f]+) [bB] ',symbols,re.M))
    assert bss<=40,bss
    print('resource_diagnostic_ARM_init_frame_bytes='+str(frame)+' bss_bytes='+str(bss))
   else:assert '__wrap__sbrk' not in symbols and 'heap_peak' not in symbols and 'stack_minimum' not in symbols
  env=(ROOT/'config/glyph/env.ini').read_text()
  diagnostic=env[env.index('[env:glyph_mk6]'):env.index('[env:glyph_mk6_senscope_playtest]')]
  assert '-D GLYPH_STRICT_HARDENING_CANDIDATE=1' in diagnostic
  assert '-D GLYPH_RESOURCE_DIAGNOSTICS=1' in diagnostic and '-Wl,--wrap=_sbrk' in diagnostic
  assert 'GLYPH_RESOURCE_DIAGNOSTICS=1' not in env[:env.index('[env:glyph_mk6]')]
  assert 'GLYPH_RESOURCE_DIAGNOSTICS=1' not in env[env.index('[env:glyph_mk6_senscope_playtest]'):]
 print('glyph_resource_diagnostics=PASS disabled_no_hook_state=true bounded_watermark=true pinned_ARM_frame=true')
if __name__=='__main__':main()
