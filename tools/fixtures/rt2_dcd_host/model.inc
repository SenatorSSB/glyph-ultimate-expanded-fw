#include "core/RecoveryUsbDiagnostics.hpp"
#include "hardware/structs/nvic.h"
#include "hardware/structs/resets.h"
#include "pico/platform.h"
#include <cstdarg>
NvicHw nvic_registers;ResetsHw reset_registers;
alignas(4096) usb_device_dpram_t usb_dpram_registers;
unsigned host_chip_version=2;
unsigned host_exception=0,host_core=0;uint32_t host_primask=0;
namespace {void physical_reset();}
bool reset_on_primask=false,reset_on_xfer=false;
uint32_t GlyphHostPrimask(){if(reset_on_primask){reset_on_primask=false;physical_reset();}return host_primask;}
void host_noop(void*){}
namespace {
struct SharedHandler{uint8_t priority;irq_handler_t fn;};
std::vector<SharedHandler> shared_handlers;irq_handler_t soft_handler=nullptr;
bool defer_hardware=false,defer_task=false,hold_address_ack=false,pending_address_ack=false;
void interrupt_pass(){
 usb_hw->ints=usb_hw->intr&usb_hw->inte;
 if(usb_hw->ints)nvic_hw->ispr|=1u<<USBCTRL_IRQ;
 if(!host_primask&&!defer_hardware&&(nvic_hw->iser&(1u<<USBCTRL_IRQ))&&(nvic_hw->ispr&(1u<<USBCTRL_IRQ))){
  nvic_hw->ispr&=~(1u<<USBCTRL_IRQ);host_exception=16+USBCTRL_IRQ;
  for(auto h:shared_handlers)h.fn();host_exception=0;
 }
 if(!host_primask&&!defer_task&&(nvic_hw->iser&(1u<<31))&&(nvic_hw->ispr&(1u<<31))){
  nvic_hw->ispr&=~(1u<<31);host_exception=47;soft_handler();host_exception=0;
 }
}
void host_setup_packet(const tusb_control_request_t&r){std::memcpy((void*)&usb_dpram->setup_packet,&r,8);usb_hw->sie_status|=USB_SIE_STATUS_SETUP_REC_BITS;usb_hw->intr|=USB_INTS_SETUP_REQ_BITS;interrupt_pass();}
void physical_reset(){usb_hw->sie_status|=USB_SIE_STATUS_BUS_RESET_BITS;usb_hw->intr|=USB_INTS_BUS_RESET_BITS;interrupt_pass();}
void host_tick(){
 if(sent<outgoing.size()&&endpoints[1].buffer){auto t=endpoints[1];endpoints[1]={};size_t n=std::min(size_t(t.bytes),outgoing.size()-sent);std::memcpy(t.buffer,outgoing.data()+sent,n);sent+=n;dcd_event_xfer_complete(0,1,n,XFER_RESULT_SUCCESS,true);}
}
void sample(){RecoveryStartupDiagnostics::Mark(RecoveryStartupDiagnostics::Phase::ReportReturned);}
unsigned state(){return (RecoveryStartupDiagnostics::Current()>>12)&15u;}
void expect(unsigned value,const char *message){sample();require(state()==value,message);}
}
extern "C" void panic(const char*format,...){throw std::runtime_error(format);}
extern "C" void irq_set_enabled(uint n,bool on){if(on)nvic_hw->iser|=1u<<n;else nvic_hw->iser&=~(1u<<n);}
extern "C" void irq_add_shared_handler(uint n,irq_handler_t h,uint8_t priority){require(n==USBCTRL_IRQ,"only actual USB shared handlers");shared_handlers.push_back({priority,h});std::sort(shared_handlers.begin(),shared_handlers.end(),[](auto a,auto b){return a.priority>b.priority;});}
extern "C" void irq_set_exclusive_handler(uint n,irq_handler_t h){require(n==31,"actual port soft IRQ claim");soft_handler=h;}
extern "C" void irq_set_pending(uint n){nvic_hw->ispr|=1u<<n;}
extern "C" int __real_user_irq_claim_unused(bool required){require(required,"pinned port required claim preserved");return 31;}
void GlyphHostSet(size_t offset,uint32_t bits){auto p=(volatile uint32_t*)((uint8_t*)usb_hw+offset);*p|=bits;}
void GlyphHostClear(size_t offset,uint32_t bits){
 auto p=(volatile uint32_t*)((uint8_t*)usb_hw+offset);*p&=~bits;
 if(offset==offsetof(usb_hw_t,sie_status)){
  if(bits&USB_SIE_STATUS_BUS_RESET_BITS)usb_hw->intr&=~USB_INTS_BUS_RESET_BITS;
  if(bits&USB_SIE_STATUS_SETUP_REC_BITS)usb_hw->intr&=~USB_INTS_SETUP_REQ_BITS;
  if(bits&USB_SIE_STATUS_SUSPENDED_BITS)usb_hw->intr&=~USB_INTS_DEV_SUSPEND_BITS;
  if(bits&USB_SIE_STATUS_RESUME_BITS)usb_hw->intr&=~USB_INTS_DEV_RESUME_FROM_HOST_BITS;
 }
 usb_hw->ints=usb_hw->intr&usb_hw->inte;
}
// Endpoint packet completion/DPRAM electrical data transfer stays explicit model.
// Actual DCD reset, SETUP decode, init/register writes, address status and endpoint
// open functions are extracted unchanged apart from SET/CLEAR MMIO adapters.
extern "C" void hw_endpoint_xfer_start(struct hw_endpoint*,uint8_t*,uint16_t);
