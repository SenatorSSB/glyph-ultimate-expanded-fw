#include "core/RecoveryUsbDiagnostics.hpp"
#if defined(GLYPH_STRICT_HARDENING_CANDIDATE) && GLYPH_STRICT_HARDENING_CANDIDATE && (defined(ARDUINO_ARCH_RP2040) || defined(GLYPH_RT2_DCD_HOST))
#include <tusb.h>
#include "device/dcd.h"
#include "hardware/irq.h"
#include "hardware/structs/nvic.h"
#include "hardware/structs/resets.h"
#include "hardware/structs/usb.h"
#include "pico/platform.h"

#ifdef GLYPH_RT2_DCD_HOST
uint32_t GlyphHostPrimask();
#endif
namespace {
// Each IRQ flag only transitions false->true; no shared IRQ/foreground RMW.
volatile bool reset_seen=false,setup_seen=false,descriptor_seen=false;
volatile bool address_requested=false,address_applied=false,configured=false;
volatile bool irq_task_entered=false,irq_task_returned=false;
volatile uint32_t task_entered=0,task_returned=0;
// Port capture precedes core1 launch; task calls serialize under __usb_mutex.
int software_irq=-1;bool in_port=false,port_complete=false;
uint8_t loops=0;bool pullup_seen=false,mounted_seen=false,inspection_seen=false;
unsigned furthest=0;
bool standard_device(const tusb_control_request_t *r){
    return r&&r->bmRequestType_bit.type==TUSB_REQ_TYPE_STANDARD&&
        r->bmRequestType_bit.recipient==TUSB_REQ_RCPT_DEVICE;
}
uint32_t primask(){
#ifdef GLYPH_RT2_DCD_HOST
    return GlyphHostPrimask();
#else
    uint32_t value;asm volatile("mrs %0, primask":"=r"(value));return value;
#endif
}
}
namespace RecoveryUsbDiagnostics {
void LoopEntered(){if(loops<2)++loops;}
void InspectionDecoded(){inspection_seen=true;}
Snapshot Read(){
    Snapshot s;
    s.sie_ctrl=usb_hw->sie_ctrl;s.inte=usb_hw->inte;s.ints=usb_hw->ints;s.intr=usb_hw->intr;
    s.dev_addr=usb_hw->dev_addr_ctrl;s.main_ctrl=usb_hw->main_ctrl;
    s.task_entered=task_entered;s.task_returned=task_returned;
    if(loops>=2&&(s.sie_ctrl&USB_SIE_CTRL_PULLUP_EN_BITS))pullup_seen=true;
    if(tud_mounted())mounted_seen=true;
    s.milestones=(loops>=2?RepeatedLoop:0)|(pullup_seen?PostLoopPullup:0)|
        (reset_seen?BusReset:0)|(setup_seen?Setup:0)|(descriptor_seen?DeviceDescriptor:0)|
        (address_requested?AddressRequested:0)|(address_applied?AddressApplied:0)|
        (configured?ConfigurationComplete:0)|(mounted_seen?Mounted:0)|
        (inspection_seen?Inspection:0)|(irq_task_entered?IrqTaskEntered:0)|
        (irq_task_returned?IrqTaskReturned:0);
    const uint32_t hardware_mask=1u<<USBCTRL_IRQ;
    const bool known=software_irq>=0&&software_irq<32;
    const uint32_t soft_mask=known?(1u<<unsigned(software_irq)):0;
    s.irq_state=((nvic_hw->iser&hardware_mask)?1u:0)|((nvic_hw->ispr&hardware_mask)?2u:0)|
        (known?4u:0)|((nvic_hw->iser&soft_mask)?8u:0)|((nvic_hw->ispr&soft_mask)?16u:0)|
        ((primask()&1u)?32u:0)|((resets_hw->reset_done&RESETS_RESET_DONE_USBCTRL_BITS)?64u:0)|
        (__get_current_exception()?128u:0)|(port_complete?256u:0)|
        (tud_inited()?512u:0)|(tud_connected()?1024u:0)|(tud_mounted()?2048u:0)|
        (uint32_t(known?software_irq:255)<<24);
    unsigned progress=0;
    if(loops>=2){
        progress=1; // repeated loop with pull-up not yet seen: orange
        if(pullup_seen)progress=2; // yellow
        if(reset_seen)progress=3; // magenta
        if(setup_seen||descriptor_seen)progress=4; // blue
        if(address_requested||address_applied)progress=5; // cyan
        if(configured||mounted_seen)progress=6; // green
        if(inspection_seen)progress=7; // white
    }
    if(progress>furthest)furthest=progress;
    return s;
}
unsigned Furthest(){return furthest;}
}

// Existing optional pin callback was undefined in the target. No task/LED/IO here.
extern "C" void tud_event_hook_cb(uint8_t port,uint32_t event,bool){
    if(port!=0)return;
    if(event==DCD_EVENT_BUS_RESET)reset_seen=true;
    if(event==DCD_EVENT_SETUP_RECEIVED)setup_seen=true;
}
extern "C" bool __real_tud_control_xfer(uint8_t,const tusb_control_request_t*,void*,uint16_t);
extern "C" bool __wrap_tud_control_xfer(uint8_t port,const tusb_control_request_t*r,void*b,uint16_t n){
    const bool result=__real_tud_control_xfer(port,r,b,n);
    if(port==0&&result&&standard_device(r)&&r->bmRequestType_bit.direction==TUSB_DIR_IN&&
       r->bRequest==TUSB_REQ_GET_DESCRIPTOR&&uint8_t(r->wValue>>8)==TUSB_DESC_DEVICE)descriptor_seen=true;
    return result;
}
extern "C" void __real_dcd_set_address(uint8_t,uint8_t);
extern "C" void __wrap_dcd_set_address(uint8_t port,uint8_t value){
    __real_dcd_set_address(port,value);if(port==0)address_requested=true;
}
extern "C" void __real_dcd_edpt0_status_complete(uint8_t,const tusb_control_request_t*);
extern "C" void __wrap_dcd_edpt0_status_complete(uint8_t port,const tusb_control_request_t*r){
    __real_dcd_edpt0_status_complete(port,r);
    if(port!=0||!standard_device(r)||r->bmRequestType_bit.direction!=TUSB_DIR_OUT)return;
    if(r->bRequest==TUSB_REQ_SET_ADDRESS)address_applied=true;
    if(r->bRequest==TUSB_REQ_SET_CONFIGURATION&&uint8_t(r->wValue)!=0)configured=true;
}
extern "C" void __real_tud_task_ext(uint32_t,bool);
extern "C" void __wrap_tud_task_ext(uint32_t timeout,bool in_isr){
    const bool core0=get_core_num()==0;
    const bool irq=__get_current_exception()!=0;
    if(core0){++task_entered;if(irq)irq_task_entered=true;}
    __real_tud_task_ext(timeout,in_isr);
    if(core0){++task_returned;if(irq)irq_task_returned=true;}
}
extern "C" int __real_user_irq_claim_unused(bool);
extern "C" int __wrap_user_irq_claim_unused(bool required){
    const int result=__real_user_irq_claim_unused(required);
    if(in_port)software_irq=result;
    return result;
}
#ifdef ARDUINO_ARCH_RP2040
void GlyphRealPortInit(uint8_t) asm("__real__Z23TinyUSB_Port_InitDeviceh");
void GlyphWrapPortInit(uint8_t) asm("__wrap__Z23TinyUSB_Port_InitDeviceh");
#else
void GlyphRealPortInit(uint8_t);
void GlyphWrapPortInit(uint8_t);
#endif
void GlyphWrapPortInit(uint8_t port){
    if(port!=0||get_core_num()!=0){GlyphRealPortInit(port);return;}
    in_port=true;GlyphRealPortInit(port);in_port=false;port_complete=true;
}
#endif
