"""Compile actual startup detector/port bodies with scripted SDK boundaries; no devices."""
from pathlib import Path
import argparse,hashlib,json,subprocess

def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args()
 a.out.mkdir(parents=True,exist_ok=False);stubs=a.out/'stubs/pico';stubs.mkdir(parents=True)
 (stubs/'stdlib.h').write_text('#pragma once\n#include <cstdint>\nusing uint=unsigned;\n')
 source=a.repo/'HAL/pico/src/comms/BootJoybusDetection.cpp';text=source.read_text();start=text.index('class BootJoybusPort {');at=text.index('{',start)+1;depth=1
 while depth:depth+=(text[at]=='{')-(text[at]=='}');at+=1
 actual=text[start:at+1]+'\n'+text[text.index('__attribute__((noinline)) bool detect_boot_gamecube'):]
 legacy_source=a.repo/'lib/glyph-joybus-pio/src/N64Console.cpp';legacy=legacy_source.read_text();begin=legacy.index('{',legacy.index('bool __no_inline_not_in_flash_func(N64Console::Detect)()'));end=legacy.index('\nbool __no_inline_not_in_flash_func(N64Console::WaitForPoll)()',begin)
 legacy='bool LegacyN64Detect() { joybus_port_t legacy_port{}; constexpr unsigned reply_delay=4,reset_wait_period_us=50;\n'+legacy[begin+1:end].replace('&_port','&legacy_port')
 cpp=a.out/'regression.cpp';cpp.write_text(r'''
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include "comms/BootJoybusDetection.hpp"
using uint=unsigned;using PIO=int*;static int token;static PIO pio0=&token;
using absolute_time_t=uint64_t;struct pio_sm_config{};
struct joybus_port_t{uint pin;PIO pio;uint sm;uint offset;pio_sm_config config;};
static int joybus_program;static bool legacy_mode=false;
struct State {
 bool sm=true,program=true,line=true,full=false,released=false,enabled=false;
 int claim=0,unclaim=0,added=0,removed=0,terminated=0,begin=0,reset=0,rx=0,tail=0,repeat=-1,full_after=-1;
 uint64_t clock=0;size_t index=0;
 std::vector<int> commands;std::vector<uint32_t> puts,waits;
} s;
int pio_claim_unused_sm(PIO,bool required){assert(!required);++s.claim;return s.sm?1:-1;}
bool pio_can_add_program(PIO,const int*){return s.program;}
void pio_sm_unclaim(PIO,uint){++s.unclaim;}
int pio_add_program(PIO,const int*){++s.added;return 2;}
pio_sm_config joybus_program_get_config(PIO,uint,uint,uint){return {};}
void joybus_port_reset(joybus_port_t*){++s.reset;}
void pio_sm_set_enabled(PIO,uint,bool enabled){s.enabled=enabled;}
void pio_sm_set_consecutive_pindirs(PIO,uint,uint,uint,bool output){assert(!s.enabled&&!output);s.released=true;}
void joybus_port_terminate(joybus_port_t*){assert(s.released&&!s.enabled);++s.terminated;++s.unclaim;++s.removed;}
absolute_time_t make_timeout_time_us(uint32_t us){return s.clock+us;}
bool time_reached(absolute_time_t deadline){return s.clock>=deadline;}
bool gpio_get(uint){return s.line;}
void tight_loop_contents(){++s.clock;}
void joybus_program_send_init(PIO,uint,uint,uint,pio_sm_config*){++s.begin;s.enabled=true;}
bool pio_sm_is_tx_fifo_full(PIO,uint){return s.full||(s.full_after>=0&&int(s.puts.size())>=s.full_after);}
void pio_sm_put(PIO,uint,uint32_t value){s.puts.push_back(value);}
uint joybus_receive_bytes(joybus_port_t*,uint8_t *bytes,uint size,uint64_t timeout,bool first){
 assert(first);if(size==2){assert(timeout==50);++s.tail;return 0;}
 assert(size==1);++s.rx;if(!legacy_mode)assert(s.rx<=60);
 if(legacy_mode&&s.rx==61){std::fprintf(stderr,"VENDOR_REPEAT_61 %s\n",s.repeat==0?"PROBE":"RESET");std::fflush(stderr);}
 if(legacy_mode&&s.rx==62)std::_Exit(73);
 int command=s.index<s.commands.size()?s.commands[s.index++]:s.repeat;
 if(command<0){s.clock+=timeout;return 0;}*bytes=command;return 1;
}
void busy_wait_us(uint32_t us){s.clock+=us;if(!legacy_mode)s.waits.push_back(us);}
void joybus_send_bytes(joybus_port_t*,uint8_t*,uint){}
''' +legacy+actual+r'''
static unsigned checks=0;
void done(){assert(s.claim==1);assert(s.unclaim==(s.sm?1:0));assert(s.added==(s.sm&&s.program?1:0));assert(s.removed==s.added&&s.terminated==s.added);if(s.added)assert(s.released);++checks;}
void fresh(){s=State{};}
void response(const uint8_t *bytes,size_t n,size_t from=0){assert(s.puts.size()>=from+n);for(size_t i=0;i<n;++i)assert(s.puts[from+i]==((uint32_t(bytes[i])<<24)|(uint32_t(i+1==n)<<23)));}
int main(int argc,char **argv){
 if(argc==2){legacy_mode=true;s.repeat=argv[1][0]=='p'?0:255;return LegacyN64Detect()?0:1;}
 for(bool n64:{false,true}) {
  const int budget=n64?60:10;
  for(int command:{-1,0,255,0x99}) {
   fresh();s.repeat=command;assert(!(n64?detect_boot_n64(8):detect_boot_gamecube(8)));assert(s.rx==budget);
   if(command==0x99){assert(s.reset==budget+1);assert(s.waits.size()==unsigned(budget));for(auto wait:s.waits)assert(wait==unsigned(n64?50:130));}
   if(command==0||command==255){assert(s.puts.size()==unsigned(budget*3));if(n64)response(reinterpret_cast<const uint8_t*>(&default_n64_status),3);else response(reinterpret_cast<const uint8_t*>(&default_gc_status),3);}
   done();
  }
  fresh();s.commands.assign(budget-1,0);s.commands.push_back(n64?1:0x40);assert(n64?detect_boot_n64(8):detect_boot_gamecube(8));assert(s.rx==budget);
  if(n64){response(reinterpret_cast<const uint8_t*>(&default_n64_report),sizeof(default_n64_report),s.puts.size()-sizeof(default_n64_report));assert(s.waits.back()==40*sizeof(n64_report_t));}else assert(s.tail==1);
  done();
  fresh();s.commands.assign(budget,0);s.commands.push_back(n64?1:0x40);assert(!(n64?detect_boot_n64(8):detect_boot_gamecube(8)));assert(s.index==unsigned(budget));done();
  for(int failure:{0,1,2}) {
   fresh();s.repeat=0;if(failure==0)s.line=false;else if(failure==1)s.full=true;else s.full_after=1;
   assert(!(n64?detect_boot_n64(8):detect_boot_gamecube(8)));assert(s.rx==1);assert(s.clock==unsigned(4+(n64?20000:10000)));assert(s.puts.size()==unsigned(failure==2?1:0));done();
  }
  for(int unavailable:{0,1}){fresh();if(unavailable==0)s.sm=false;else s.program=false;assert(!(n64?detect_boot_n64(8):detect_boot_gamecube(8)));assert(s.rx==0);done();}
 }
 for(int command:{0x41,0x42}){fresh();s.repeat=command;assert(detect_boot_gamecube(8));assert(s.rx==1&&s.puts.empty());done();}
 fresh();s.commands={0,255,0,255,1};assert(detect_boot_n64(8));assert(s.rx==5);done();
 std::printf("{\"checks\":%u,\"hardware_operations\":0,\"source\":\"actual_header_and_port_bodies\"}\n",checks);
}
''')
 commands=[]
 def run(argv):
  c=subprocess.run(list(map(str,argv)),capture_output=True,text=True,timeout=60);commands.append(dict(argv=list(map(str,argv)),exit_status=c.returncode,stdout=c.stdout,stderr=c.stderr));(a.out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');assert c.returncode==0,c.stdout+c.stderr;return c.stdout
 binary=a.out/'regression'
 run(['clang++','-std=c++20','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I',a.out/'stubs','-I',a.repo/'include','-I',a.repo/'lib/glyph-joybus-pio/include',cpp,'-o',binary])
 result=json.loads(run([binary]));assert result['checks']==25
 for mode in ['probe','reset']:
  c=subprocess.run([str(binary),mode],capture_output=True,text=True,timeout=10)
  assert c.returncode==73 and ('VENDOR_REPEAT_61 '+mode.upper()) in c.stderr,(mode,c.returncode,c.stdout,c.stderr)
  commands.append(dict(argv=[str(binary),mode],exit_status=c.returncode,stdout=c.stdout,stderr=c.stderr,outcome='EXPECTED_WITNESS_EXIT_AT_62ND_RECEIVE_AFTER_61_RETURNED',timeout_seconds=10))
 (a.out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');result['unchanged_vendor_repeat_stream_reproductions']=2
 result['source_files_sha256']={str(p.relative_to(a.repo)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,legacy_source,a.repo/'include/comms/BootJoybusDetection.hpp',a.repo/'lib/glyph-joybus-pio/include/gamecube_definitions.h',a.repo/'lib/glyph-joybus-pio/include/n64_definitions.h']}
 (a.out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
