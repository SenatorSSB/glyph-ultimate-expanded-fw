// Deterministic peripheral doubles. Production C/C++ function bodies are included
// verbatim by the checker; no receive/backend control flow is copied here.
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <deque>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using uint = unsigned;
using absolute_time_t = uint64_t;
#define __no_inline_not_in_flash_func(x) x
#define __not_in_flash_func(x) x
struct pio_sm_config {};
struct Pio { bool enabled=true, marker=false; unsigned pc=1;uint32_t ctrl=1; } hw;
using PIO = Pio*;
PIO pio0=&hw;
struct Bank { uint32_t intr[4]{}; } bank;
Bank *iobank0_hw=&bank;
constexpr uint GPIO_IRQ_EDGE_FALL=4;
uint64_t now_us=0, limit_us=2000, tx_end=0;
bool pin_high=true, irq_disabled=false;
unsigned updates=0, pauses=0, resumes=0, resets=0, starts=0;
std::deque<uint8_t> rx;
std::vector<uint32_t> tx;
struct Event { uint64_t at; std::function<void()> run; };
std::deque<Event> events;
std::function<void()> on_disable;
struct Bound {};
void tick() {
 if (++now_us>limit_us) throw Bound();
 while(!events.empty() && events.front().at<=now_us) {
  auto f=events.front().run;events.pop_front();f();
 }
 if(tx_end && now_us>=tx_end) {tx_end=0;hw.pc=joybus_offset_read_loop;}
}
void event(uint64_t t,std::function<void()> f){events.push_back({t,f});}
void incoming(std::initializer_list<uint8_t> b){hw.marker=true;rx.insert(rx.end(),b);}
absolute_time_t make_timeout_time_us(uint64_t v){return now_us+v;}
bool time_reached(absolute_time_t t){tick();return now_us>=t;}
void tight_loop_contents(){tick();}
void busy_wait_us(uint64_t v){for(uint64_t i=0;i<v;++i)tick();}
uint32_t save_and_disable_interrupts(){assert(!irq_disabled);irq_disabled=true;return 0;}
void restore_interrupts(uint32_t){assert(irq_disabled);irq_disabled=false;}
void gpio_acknowledge_irq(uint pin,uint32_t e){assert(hw.enabled);bank.intr[pin/8]&=~(e<<(4*(pin%8)));}
bool gpio_get(uint){return pin_high;}
void pio_sm_set_enabled(PIO,uint,bool v){
 if(!v){++pauses;if(irq_disabled&&on_disable)on_disable();}else ++resumes;
 hw.enabled=v;
 hw.ctrl=v?1:0;
}
bool pio_sm_is_enabled(PIO,uint){return hw.enabled;}
bool pio_interrupt_get(PIO,uint index){assert(index==4);return hw.marker;}
void pio_interrupt_clear(PIO,uint index){assert(index==4);assert(!hw.enabled);hw.marker=false;}
uint pio_sm_get_pc(PIO,uint){return hw.pc;}
bool pio_sm_is_rx_fifo_empty(PIO,uint){tick();return rx.empty();}
uint pio_sm_get_blocking(PIO,uint){while(rx.empty())tick();auto b=rx.front();rx.pop_front();return b;}
void pio_sm_put_blocking(PIO,uint,uint32_t b){tx.push_back(b);hw.pc=joybus_offset_write;tx_end=now_us+40;}
uint pio_claim_unused_sm(PIO,bool){return 0;}
void pio_sm_claim(PIO,int){}
void pio_sm_unclaim(PIO,uint){}
int joybus_program;
uint pio_add_program(PIO,int*){return 0;}
void pio_remove_program(PIO,int*,uint){}
void pio_sm_init(PIO,uint,uint pc,pio_sm_config*){hw.enabled=false;hw.ctrl=0;hw.pc=pc==joybus_offset_read?joybus_offset_read_loop:pc;rx.clear();++resets;}
void pio_gpio_init(PIO,uint){}
pio_sm_config joybus_program_get_default_config(uint){return {};}
void sm_config_set_out_pins(pio_sm_config*,uint,uint){}
void sm_config_set_set_pins(pio_sm_config*,uint,uint){}
void sm_config_set_in_pins(pio_sm_config*,uint){}
void sm_config_set_out_shift(pio_sm_config*,bool,bool,uint){}
void sm_config_set_in_shift(pio_sm_config*,bool,bool,uint){}
void sm_config_set_clkdiv(pio_sm_config*,float){}
constexpr int clk_sys=0;
uint clock_get_hz(int){return 125000000;}
enum CommunicationBackendId {COMMS_BACKEND_GAMECUBE};
enum class InputScanSpeed {SLOW,MEDIUM,FAST};
unsigned fast_scans=0;
std::function<void()> on_fast_scan;
struct InputState {};
struct InputSource {};
struct Outputs {bool a=1,b=0,x=1,y=0,buttonR=1,triggerLDigital=1,triggerRDigital=0,start=1;
 bool dpadLeft=1,dpadRight=0,dpadDown=1,dpadUp=0;
 uint8_t leftStickX=11,leftStickY=22,rightStickX=33,rightStickY=44,triggerLAnalog=55,triggerRAnalog=66;};
struct CommunicationBackend {
 Outputs _outputs;
 CommunicationBackend(InputState&,InputSource**,size_t){}
 virtual CommunicationBackendId BackendId(){return COMMS_BACKEND_GAMECUBE;}
 void ScanInputs(InputScanSpeed speed){if(speed==InputScanSpeed::FAST){++fast_scans;if(on_fast_scan)on_fast_scan();}}
 void UpdateOutputs(){++updates;}
};
struct RP {void idleOtherCore(){++starts;}void resumeOtherCore(){}} rp2040;
