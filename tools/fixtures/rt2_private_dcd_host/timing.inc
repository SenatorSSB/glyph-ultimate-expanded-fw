#include "hardware/irq.h"
extern "C" void GlyphHostPrivateMarker(uint32_t,uint32_t);
extern "C" void GlyphHostPrivateStatus(uint32_t);
// Host-only source-boundary hooks. Registers retain pinned SDK layouts. SIE
// SETUP_REC is the single source of INTR.SETUP_REQ; INTS includes force state.
extern "C" void __wrap_irq_add_shared_handler(uint,irq_handler_t,uint8_t);
extern "C" void __wrap_dcd_event_handler(dcd_event_t const*,bool);
namespace {
void GlyphPreSetupBoundary(unsigned);
unsigned actual_handler_calls=0;
int timing_point=-1;bool timing_fired=false;
void latch_setup(){
    const auto r=req(0x80,TUSB_REQ_GET_DESCRIPTOR,TUSB_DESC_DEVICE<<8,18);
    std::memcpy((void*)&usb_dpram->setup_packet,&r,8);
    usb_hw->sie_status|=USB_SIE_STATUS_SETUP_REC_BITS;
    usb_hw->intr|=USB_INTR_SETUP_REQ_BITS;
    usb_hw->ints=(usb_hw->intr&usb_hw->inte)|usb_hw->intf;
}
void GlyphTiming(unsigned point){if(point==0)++actual_handler_calls;if(timing_point==int(point)&&!timing_fired){timing_fired=true;latch_setup();}}
void GlyphSetupEvent(const uint8_t *setup){
    // Exact pinned always-inline setup helper, with only external call redirected.
    dcd_event_t event={.rhport=0,.event_id=DCD_EVENT_SETUP_RECEIVED};
    memcpy(&event.setup_received,setup,sizeof(tusb_control_request_t));
    __wrap_dcd_event_handler(&event,true);
}
}
