#!/usr/bin/env python3
"""Actual CDC adapter under adversarial IRQ/main lock scheduling; no device I/O."""
from pathlib import Path
import subprocess,tempfile,json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[1]
HEADER=ROOT/'HAL/pico/include/comms/CoordinatedCdcStream.hpp'
HARNESS=r'''
#include <cassert>
#include <cstdint>
#include <cstddef>
#include <algorithm>
struct mutex_t { bool held=false; };
mutex_t __usb_mutex;
bool mutex_try_enter(mutex_t*m,void*){if(m->held)return false;m->held=true;return true;}
void mutex_exit(mutex_t*m){assert(m->held);m->held=false;}
unsigned ticks=0,attempts=0,deferrals=0,deadlocks=0;bool inner=false,connected=true;unsigned free_bytes=64;
uint32_t millis(){return ticks;}
void delay(unsigned n){assert(!__usb_mutex.held);ticks+=n;}
// Pinned task IRQ first tries __usb_mutex. Its DTR/reset handler then takes
// the FIFO writer/reader locks. Deliver it precisely while main owns one.
void irq(){++attempts;if(!mutex_try_enter(&__usb_mutex,nullptr)){++deferrals;return;}if(inner)++deadlocks;mutex_exit(&__usb_mutex);}
void access(){inner=true;irq();inner=false;}
uint32_t tud_cdc_n_available(uint8_t){access();return 1;}
bool tud_cdc_n_peek(uint8_t,uint8_t*b){access();*b=42;return true;}
int tud_cdc_n_read_char(uint8_t){access();return 42;}
uint32_t tud_cdc_n_write_available(uint8_t){access();return free_bytes;}
bool tud_cdc_n_connected(uint8_t){access();return connected;}
uint32_t tud_cdc_n_write(uint8_t,const void*,uint32_t n){access();assert(n<=free_bytes);return n;}
uint32_t tud_cdc_n_write_flush(uint8_t){access();return 1;}
class Stream {public:virtual ~Stream()=default;virtual int available(){return 0;}virtual int peek(){return -1;}virtual int read(){return -1;}virtual int availableForWrite(){return 0;}virtual void flush(){}virtual size_t write(uint8_t){return 0;}virtual size_t write(const uint8_t*,size_t){return 0;}};
#include "CoordinatedCdcStream.hpp"
int main(){Stream unused;CoordinatedCdcStream s(unused);uint8_t bytes[128]={};
for(unsigned i=0;i<10000;++i){assert(s.available()==1);assert(s.peek()==42);assert(s.read()==42);assert(s.availableForWrite()==64);s.flush();assert(s.writeAvailable(bytes,128)==64);assert(s.write(bytes,128)==128);}
#ifdef EXPECT_OLD_RACE
assert(deadlocks>0); // model observes wait inversion; deliberately does not sleep49.7days
#else
assert(deadlocks==0&&attempts==deferrals);
__usb_mutex.held=true;assert(s.available()==0&&s.peek()==-1&&s.read()==-1&&s.availableForWrite()==0);s.flush();auto busy_start=ticks;assert(s.writeAvailable(bytes,128)==0&&ticks==busy_start);__usb_mutex.held=false;
free_bytes=0;auto attempt=ticks;assert(s.writeAvailable(bytes,128)==0&&ticks==attempt);auto start=ticks;assert(s.write(bytes,128)==0&&ticks-start==2000);
free_bytes=64;connected=false;assert(s.write(bytes,1)==0);connected=true;assert(s.write(bytes,1)==1);
#endif
}
'''
def main():
    a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path);args=a.parse_args()
    with tempfile.TemporaryDirectory(prefix='glyph-usb-coordination-') as tmp:
        t=Path(tmp);(t/'pico').mkdir();(t/'pico/mutex.h').write_text('#pragma once\n');(t/'tusb.h').write_text('#pragma once\n');(t/'Arduino.h').write_text('#pragma once\n')
        (t/'harness.cpp').write_text(HARNESS)
        for old in (False,True):
            source=HEADER.read_text()
            if old:source=source.replace('held(mutex_try_enter(&__usb_mutex, nullptr))','held(true)').replace('if (held) mutex_exit(&__usb_mutex);','/* old caller never owned outer mutex */')
            (t/'CoordinatedCdcStream.hpp').write_text(source)
            cmd=['c++','-std=c++17','-Wall','-Wextra','-Werror','-Wno-unused-private-field','-fsanitize=address,undefined','-DGLYPH_CDC_COORDINATION_TEST=1','-I',str(t),str(t/'harness.cpp'),'-o',str(t/'test')]
            if old:cmd.insert(1,'-DEXPECT_OLD_RACE=1')
            subprocess.run(cmd,check=True,capture_output=True);subprocess.run([str(t/'test')],check=True,timeout=10)
    report={'status':'PASS','actual_adapter_sha256':hashlib.sha256(HEADER.read_bytes()).hexdigest(),'irq_schedules':10000,'negative':'outer mutex omitted reproduces same-core internal lock reentry','full_fifo_deadline_ms':2000,'scope':'actual adapter with deterministic pinned-lock topology model; no physical attribution'}
    if args.output_dir:args.output_dir.mkdir(parents=True,exist_ok=True);(args.output_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report));return 0
if __name__=='__main__':raise SystemExit(main())
