#include "core/RecoveryUsbDiagnostics.hpp"
#include "core/ColdRecoveryBoot.h"
#if defined(GLYPH_STRICT_HARDENING_CANDIDATE) && GLYPH_STRICT_HARDENING_CANDIDATE && (defined(ARDUINO_ARCH_RP2040) || defined(GLYPH_RT2_DCD_HOST))
#include <tusb.h>
#include "device/dcd.h"
#include "portable/raspberrypi/rp2040/rp2040_usb.h"
#if TUD_OPT_RP2040_USB_DEVICE_ENUMERATION_FIX
#error "Raw RT2 diagnostic candidate requires E5 workaround disabled"
#endif
#include "hardware/irq.h"
#include "hardware/structs/nvic.h"
#include "hardware/structs/resets.h"
#include "hardware/structs/usb.h"
#include "pico/platform.h"

#ifdef GLYPH_RT2_DCD_HOST
uint32_t GlyphHostPrimask();
#endif
namespace {
RecoveryTaskDiagnostics::State task_observer;
RecoverySetupIrqDiagnostics::State setup_observer;
RecoveryPreSetupDiagnostics::State pre_setup_observer;
RecoveryPrivateDcdDiagnostics::State private_dcd_observer;
// Milestones are sticky within the latest DCD BUS_RESET epoch.
volatile bool reset_seen=false,setup_seen=false,descriptor_seen=false;
volatile bool address_requested=false,address_applied=false,configured=false;
volatile bool irq_task_entered=false,irq_task_returned=false;
volatile uint32_t task_entered=0,task_returned=0;
volatile uint32_t reset_count=0,setup_count=0,reset_order=0,task_reset_count=0;
volatile bool unplug_seen=false;
volatile uint32_t descriptor_epoch=0,address_requested_epoch=0,address_applied_epoch=0,configured_epoch=0;
volatile uint32_t inspection_epoch=0;
volatile RecoveryUsbDiagnostics::BootStage boot_stage=RecoveryUsbDiagnostics::BootStage::BeforeSetup;
// Separate single-writer banks: USB event callback (core0 IRQ) and core0 reader.
// Reads are cumulative observations, not a coherent atomic hardware snapshot.
struct Observations {
    volatile uint32_t sie=0,intr=0,ints=0,inte=0,irq=0,ep_in=0,ep_out=0,raw=0;
};
Observations event_observed,foreground_observed;
// Port capture precedes core1 launch; task calls serialize under __usb_mutex.
int software_irq=-1;bool in_port=false,port_complete=false;
irq_handler_t registered_dcd_handler=nullptr;
uint8_t loops=0;bool pullup_seen=false;
volatile bool inspection_seen=false;
uint32_t foreground_epoch=0;
unsigned furthest=0;
bool standard_device(const tusb_control_request_t *r){
    return r&&r->bmRequestType_bit.type==TUSB_REQ_TYPE_STANDARD&&
        r->bmRequestType_bit.recipient==TUSB_REQ_RCPT_DEVICE;
}
uint32_t primask(){
#ifdef GLYPH_RT2_DCD_HOST
    return GlyphHostPrimask();
#else
    uint32_t value;asm volatile("mrs %0, primask":"=r"(value)::"memory");return value;
#endif
}
uint32_t irq_observation(){
    const uint32_t mask=1u<<USBCTRL_IRQ;
    return ((nvic_hw->iser&mask)?1u:2u)|((nvic_hw->ispr&mask)?4u:8u)|
        ((primask()&1u)?16u:32u)|
        ((resets_hw->reset_done&RESETS_RESET_DONE_USBCTRL_BITS)?64u:128u);
}
uint32_t setup_raw(){
    using namespace RecoverySetupIrqDiagnostics;
    // Read order is fixed and bounded. These registers are not snapshotted
    // atomically; sticky tuples describe one sequential sampling pass.
    const uint32_t sie=usb_hw->sie_status,intr=usb_hw->intr;
    const uint32_t inte=usb_hw->inte,ints=usb_hw->ints,intf=usb_hw->intf;
    return (sie&USB_SIE_STATUS_SETUP_REC_BITS?Sie:0u)|
        (intr&USB_INTR_SETUP_REQ_BITS?Intr:0u)|(inte&USB_INTE_SETUP_REQ_BITS?Inte:0u)|
        (ints&USB_INTS_SETUP_REQ_BITS?Ints:0u)|(intf&USB_INTF_SETUP_REQ_BITS?Force:0u);
}
uint32_t setup_gates(){
    using namespace RecoverySetupIrqDiagnostics;
    const uint32_t mask=1u<<USBCTRL_IRQ,exception=__get_current_exception();
    return (nvic_hw->iser&mask?NvicOn:NvicOff)|(nvic_hw->ispr&mask?Pending:NotPending)|
        (primask()&1u?Masked:Unmasked)|
        (exception==16+USBCTRL_IRQ?UsbException:exception?OtherException:Thread)|
        (resets_hw->reset_done&RESETS_RESET_DONE_USBCTRL_BITS?ResetDone:ResetNotDone)|
        (port_complete?PortReturned:0u)|(tud_inited()?TinyUsbInitialized:0u);
}
void setup_foreground(){
    if(!setup_observer.Enabled()||get_core_num()!=0||__get_current_exception()!=0)return;
    const uint32_t raw=setup_raw();const uint32_t gates=setup_gates();
    setup_observer.Foreground(raw,gates);
}
void clear(Observations &o){
    o.sie=0;o.intr=0;o.ints=0;o.inte=0;o.irq=0;o.ep_in=0;o.ep_out=0;o.raw=0;
}
void observe(Observations &o){
    const uint32_t sie=usb_hw->sie_status,intr=usb_hw->intr,ints=usb_hw->ints;
    o.sie|=sie;o.intr|=intr;o.ints|=ints;o.inte|=usb_hw->inte;o.irq|=irq_observation();
    o.ep_in|=usb_dpram->ep_buf_ctrl[0].in;o.ep_out|=usb_dpram->ep_buf_ctrl[0].out;
    // Counts positive samples, not unique packets; the same latched bit may recur.
    if((sie&USB_SIE_STATUS_SETUP_REC_BITS)||(intr&USB_INTR_SETUP_REQ_BITS)||
       (ints&USB_INTS_SETUP_REQ_BITS)){if(o.raw!=UINT32_MAX)++o.raw;}
}
}
// Called only by the exact private USBCTRL TU, including before recovery.
// Enable gates valid publication only; boot-lifetime history never resets.
extern "C" __attribute__((noinline,used)) void GlyphDcdPrivateStatus(uint32_t s0){
    private_dcd_observer.Initial(s0);
}
extern "C" __attribute__((noinline,used)) void GlyphDcdPrivateReturn(uint32_t s0,uint32_t s1){
    // The private TU already read S1. These are sequential core0 samples,
    // not an atomic snapshot and not proof that EXC_RETURN completed.
    const uint32_t mask=1u<<USBCTRL_IRQ;
    const uint32_t enabled=nvic_hw->iser;
    const uint32_t pending=nvic_hw->ispr;
    const uint32_t masked=primask();
    using namespace RecoveryPrivateDcdDiagnostics;
    const uint32_t gates=(enabled&mask?NvicEnabled:0u)|
        (pending&mask?NvicPending:0u)|(masked&1u?PrimaskSet:0u);
    private_dcd_observer.Return(s0,s1,gates);
}
namespace RecoveryUsbDiagnostics {
void BeginRecovery(){task_observer.Enable();setup_observer.Enable();pre_setup_observer.Enable();private_dcd_observer.Enable();}
void PrivateReadInto(RecoveryPrivateDcdDiagnostics::Snapshot &out){private_dcd_observer.ReadInto(out);}
void PreSetupReadInto(RecoveryPreSetupDiagnostics::Snapshot &out){pre_setup_observer.ReadInto(out);}
void SetupReadInto(RecoverySetupIrqDiagnostics::Snapshot &out){setup_observer.ReadInto(out);}
RecoveryTaskDiagnostics::Snapshot TaskRead(){return task_observer.Read();}
void TaskReadInto(RecoveryTaskDiagnostics::Snapshot &out){task_observer.ReadInto(out);}
void ObserveIndependent(){
    // SIE/INTR/INTS are non-destructive reads; no TinyUSB, mutex or NVIC read
    // on core1 (NVIC would describe core1, not the core0 USB IRQ).
    const uint32_t raw=setup_raw();
    setup_observer.Independent(raw);
    task_observer.ObserveRaw((raw&(RecoverySetupIrqDiagnostics::Sie|RecoverySetupIrqDiagnostics::Intr|RecoverySetupIrqDiagnostics::Ints))!=0,
        (usb_hw->sie_ctrl&USB_SIE_CTRL_PULLUP_EN_BITS)!=0);
}
void Stage(BootStage stage){boot_stage=stage;}
void LoopEntered(){setup_foreground();task_observer.Arm();if(loops<2)++loops;}
void InspectionDecoded(){task_observer.Inspection();inspection_epoch=reset_count;inspection_seen=true;}
Snapshot Read(){
    Snapshot s;
    // This API is called only by core0 application diagnostics, never by core1.
    setup_foreground();
    const uint32_t epoch=reset_count;
    if(foreground_epoch!=epoch){clear(foreground_observed);foreground_epoch=epoch;furthest=0;}
    observe(foreground_observed);
    s.sie_status=usb_hw->sie_status;
    s.ep0_in=usb_dpram->ep_buf_ctrl[0].in;s.ep0_out=usb_dpram->ep_buf_ctrl[0].out;
    s.seen_sie_status=event_observed.sie|foreground_observed.sie;
    s.seen_intr=event_observed.intr|foreground_observed.intr;
    s.seen_ints=event_observed.ints|foreground_observed.ints;
    s.seen_inte=event_observed.inte|foreground_observed.inte;
    s.seen_irq=event_observed.irq|foreground_observed.irq;
    s.seen_ep0_in=event_observed.ep_in|foreground_observed.ep_in;
    s.seen_ep0_out=event_observed.ep_out|foreground_observed.ep_out;
    s.task_reset_count=task_reset_count;
    const bool task_epoch_known=!unplug_seen&&task_reset_count==epoch;
    const bool descriptor_current=task_epoch_known&&descriptor_seen&&descriptor_epoch==epoch;
    const bool requested_current=task_epoch_known&&address_requested&&address_requested_epoch==epoch;
    const bool applied_current=task_epoch_known&&address_applied&&address_applied_epoch==epoch;
    const bool configured_current=task_epoch_known&&configured&&configured_epoch==epoch;
    const bool inspection_current=task_epoch_known&&inspection_seen&&inspection_epoch==epoch;
    s.bus_reset_count=reset_count;s.setup_event_count=setup_count;s.reset_order=reset_order;
    const uint32_t irq_raw=event_observed.raw,fg_raw=foreground_observed.raw;
    s.raw_setup_observations=UINT32_MAX-irq_raw<fg_raw?UINT32_MAX:irq_raw+fg_raw;
    const bool raw_setup=s.raw_setup_observations!=0;
    s.chip_version=rp2040_chip_version();s.rom_version=rp2040_rom_version();
    // bit0: TinyUSB compile option, bit1: SDK silicon predicate, bit2: would call
    // the affected-silicon body on a pulled-up bus reset. This candidate stays OFF.
    s.e5_flags=s.chip_version==1?2u:0u; // compile-time guard above proves disabled
    s.sie_ctrl=usb_hw->sie_ctrl;s.inte=usb_hw->inte;s.ints=usb_hw->ints;s.intr=usb_hw->intr;
    s.dev_addr=usb_hw->dev_addr_ctrl;s.main_ctrl=usb_hw->main_ctrl;
    s.task_entered=task_entered;s.task_returned=task_returned;
    if(loops>=2&&(s.sie_ctrl&USB_SIE_CTRL_PULLUP_EN_BITS))pullup_seen=true;
    const bool mounted_seen=configured_current&&tud_mounted();
    s.milestones=(loops>=2?RepeatedLoop:0)|(pullup_seen?PostLoopPullup:0)|
        (reset_seen?BusReset:0)|(setup_seen?Setup:0)|(descriptor_current?DeviceDescriptor:0)|
        (requested_current?AddressRequested:0)|(applied_current?AddressApplied:0)|
        (configured_current?ConfigurationComplete:0)|(mounted_seen?Mounted:0)|
        (inspection_current?Inspection:0)|(irq_task_entered?IrqTaskEntered:0)|
        (irq_task_returned?IrqTaskReturned:0)|(raw_setup?RawSetup:0);
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
        if(raw_setup)progress=4; // blue: hardware latch observed
        if(setup_seen)progress=5; // cyan: DCD emitted event (queue success unknown)
        if(descriptor_current||requested_current||applied_current)progress=6; // green: task control progress
        if(configured_current||inspection_current)progress=7; // white
    }
    // A raw pending reset has not yet established the next DCD epoch. Avoid
    // promoting SETUP bits that might belong to the retiring epoch.
    const bool pending_reset=(s.intr&USB_INTR_BUS_RESET_BITS)!=0;
    s.observation_valid=epoch==reset_count?1u:0u;
    if(!s.observation_valid){clear(foreground_observed);foreground_epoch=reset_count;furthest=0;}
    else if(!pending_reset&&progress>furthest)furthest=progress;
    return s;
}
unsigned Furthest(){return furthest;}
}

// Existing optional pin callback was undefined in the target. No task/LED/IO here.
extern "C" void tud_event_hook_cb(uint8_t port,uint32_t event,bool){
    if(port!=0||get_core_num()!=0)return;
    if(__get_current_exception()!=16+USBCTRL_IRQ)return;
    if(event==DCD_EVENT_UNPLUGGED){unplug_seen=true;task_observer.UnplugEvent();}
    if(event!=DCD_EVENT_BUS_RESET&&event!=DCD_EVENT_SETUP_RECEIVED)return;
    // Pinned queue_event calls this before DCD clears SIE status, even if enqueue
    // failed. No IRQ/task/queue acknowledgement or MMIO write is added here.
    if(event==DCD_EVENT_BUS_RESET){
        task_observer.ResetEvent();
        // SETUP is handled before RESET in the same IRQ; never carry it over.
        clear(event_observed);setup_seen=false;descriptor_seen=false;
        address_requested=false;address_applied=false;configured=false;inspection_seen=false;
        setup_count=0;reset_seen=true;
        reset_order|=1u<<unsigned(boot_stage);
        ++reset_count; // boot-lifetime epoch; wraps only after 2^32 resets
    }
    observe(event_observed);
    if(event==DCD_EVENT_SETUP_RECEIVED){setup_observer.Hook();task_observer.SetupEvent();setup_seen=true;if(setup_count!=UINT32_MAX)++setup_count;}
}
namespace {
bool pre_setup_context(){return pre_setup_observer.Enabled()&&get_core_num()==0&&__get_current_exception()==16+USBCTRL_IRQ;}
bool bounded_prefix(const char *text,const char *prefix){
    if(!text)return false;
    for(unsigned i=0;i<48;++i){if(!prefix[i])return true;if(text[i]!=prefix[i])return false;}
    return false;
}
}
extern "C" bool __real_hw_endpoint_xfer_continue(struct hw_endpoint*);
extern "C" bool __wrap_hw_endpoint_xfer_continue(struct hw_endpoint *ep){
    const bool track=pre_setup_context();
    if(track)pre_setup_observer.EndpointEnter(ep->ep_addr,ep->active,usb_hw->buf_status,uint32_t(reinterpret_cast<uintptr_t>(ep)));
    const bool result=__real_hw_endpoint_xfer_continue(ep); // original once, including its real panic
    if(track)pre_setup_observer.EndpointReturn(result);
    return result;
}
extern "C" __attribute__((noinline,used)) void GlyphObserveUsbPanic(const char *format){
    if(!pre_setup_context())return;
    using namespace RecoveryPreSetupDiagnostics;
    const uint32_t kind=bounded_prefix(format,"Can't continue xfer on inactive ep ")?InactiveEndpoint:
        bounded_prefix(format,"Unhandled IRQ ")?UnhandledIrq:OtherUsb;
    pre_setup_observer.PanicEntered(kind);
}
#ifdef ARDUINO_ARCH_RP2040
// AAPCS32 transparent tail interposer. Save original register and stack varargs,
// maintain 8-byte alignment across the observer call, restore original SP/LR,
// and tail-branch exactly once. No C variadic forwarding or panic recovery.
extern "C" __attribute__((naked,noreturn,noinline,used)) void __wrap_panic(const char*,...){
    asm volatile("push {r0-r4, lr}\n"
                 "bl GlyphObserveUsbPanic\n"
                 "ldr r4, [sp, #20]\n"
                 "mov lr, r4\n"
                 "ldr r4, =__real_panic\n"
                 "mov ip, r4\n"
                 "pop {r0-r4}\n"
                 "add sp, #4\n"
                 "bx ip\n");
}
#endif
extern "C" bool __real_tud_control_xfer(uint8_t,const tusb_control_request_t*,void*,uint16_t);
extern "C" bool __wrap_tud_control_xfer(uint8_t port,const tusb_control_request_t*r,void*b,uint16_t n){
    const uint32_t epoch=reset_count;
    const bool result=__real_tud_control_xfer(port,r,b,n);
    if(port==0&&result&&standard_device(r)&&r->bmRequestType_bit.direction==TUSB_DIR_IN&&
       r->bRequest==TUSB_REQ_GET_DESCRIPTOR&&uint8_t(r->wValue>>8)==TUSB_DESC_DEVICE)task_observer.Control();
    if(!unplug_seen&&task_reset_count==epoch&&epoch==reset_count&&port==0&&result&&standard_device(r)&&r->bmRequestType_bit.direction==TUSB_DIR_IN&&
       r->bRequest==TUSB_REQ_GET_DESCRIPTOR&&uint8_t(r->wValue>>8)==TUSB_DESC_DEVICE){descriptor_epoch=epoch;descriptor_seen=true;}
    return result;
}
extern "C" void __real_dcd_set_address(uint8_t,uint8_t);
extern "C" void __wrap_dcd_set_address(uint8_t port,uint8_t value){
    const uint32_t epoch=reset_count;
    __real_dcd_set_address(port,value);if(port==0)task_observer.AddressRequested();if(!unplug_seen&&task_reset_count==epoch&&epoch==reset_count&&port==0){address_requested_epoch=epoch;address_requested=true;}
}
extern "C" void __real_dcd_edpt0_status_complete(uint8_t,const tusb_control_request_t*);
extern "C" void __wrap_dcd_edpt0_status_complete(uint8_t port,const tusb_control_request_t*r){
    const uint32_t epoch=reset_count;
    __real_dcd_edpt0_status_complete(port,r);
    if(port==0&&standard_device(r)&&r->bmRequestType_bit.direction==TUSB_DIR_OUT){
        if(r->bRequest==TUSB_REQ_SET_ADDRESS)task_observer.AddressApplied();
        if(r->bRequest==TUSB_REQ_SET_CONFIGURATION)task_observer.Configuration(uint8_t(r->wValue)!=0);
    }
    if(unplug_seen||task_reset_count!=epoch||epoch!=reset_count||port!=0||!standard_device(r)||r->bmRequestType_bit.direction!=TUSB_DIR_OUT)return;
    if(r->bRequest==TUSB_REQ_SET_ADDRESS){address_applied_epoch=epoch;address_applied=true;}
    if(r->bRequest==TUSB_REQ_SET_CONFIGURATION&&uint8_t(r->wValue)!=0){configured_epoch=epoch;configured=true;}
}
// Pinned usbd.c reaches this while consuming RESET/UNPLUGGED. The superseded
// same-boot warm reset is not linked into the two-stage cold candidate.
extern "C" void __real_usbd_control_reset(void);
extern "C" void __wrap_usbd_control_reset(void){
    __real_usbd_control_reset();++task_reset_count;task_observer.ResetCompleted();
}
extern "C" void __real_tud_task_ext(uint32_t,bool);
extern "C" void __wrap_tud_task_ext(uint32_t timeout,bool in_isr){
    const bool core0=get_core_num()==0;
    const bool irq=__get_current_exception()!=0;
    const bool foreground=core0&&!irq&&task_observer.ForegroundEnabled();
    if(foreground){setup_foreground();task_observer.Enter();}
    if(core0){++task_entered;if(irq)irq_task_entered=true;}
    __real_tud_task_ext(timeout,in_isr);
    if(core0){++task_returned;if(irq)irq_task_returned=true;}
    if(foreground){task_observer.Return();setup_foreground();}
}
extern "C" void __real_irq_add_shared_handler(uint,irq_handler_t,uint8_t);
extern "C" void __wrap_irq_add_shared_handler(uint irq,irq_handler_t handler,uint8_t priority){
    // Pinned port also registers a lowest-order USB task trigger. Capture only
    // the DCD highest-order registration, without adding a shared handler.
    if(in_port&&get_core_num()==0&&irq==USBCTRL_IRQ&&priority==0xff){
        if(!registered_dcd_handler){
            registered_dcd_handler=handler;setup_observer.Registered();
            // Preserve the SDK's exact callback and priority. No IRQ trampoline
            // may execute observer work before the private handler's INTS load.
            __real_irq_add_shared_handler(irq,handler,priority);return;
        }
        setup_observer.DuplicateRegistration(); // forward duplicate untouched
    }
    __real_irq_add_shared_handler(irq,handler,priority);
}
extern "C" void __real_dcd_event_handler(dcd_event_t const*,bool);
extern "C" void __wrap_dcd_event_handler(dcd_event_t const *event,bool in_isr){
    const bool external=event&&event->rhport==0&&event->event_id==DCD_EVENT_SETUP_RECEIVED;
    const bool setup=external&&get_core_num()==0&&__get_current_exception()==16+USBCTRL_IRQ;
    if(external)setup_observer.ExternalEnter(!setup);
    const bool branch=event&&event->rhport==0&&pre_setup_observer.Enabled()&&get_core_num()==0&&__get_current_exception()==16+USBCTRL_IRQ;
    const bool sof=branch&&event->event_id==DCD_EVENT_SOF;
    const bool xfer=branch&&event->event_id==DCD_EVENT_XFER_COMPLETE;
    if(sof||xfer)pre_setup_observer.Event(sof,false);
    if(setup)setup_observer.EmitEnter();
    __real_dcd_event_handler(event,in_isr);
    if(sof||xfer)pre_setup_observer.Event(sof,true);
    if(setup)setup_observer.EmitReturn();
    if(external)setup_observer.ExternalReturn();
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
    if(GlyphColdRecoveryDeferPort(port))return;
    if(port!=0||get_core_num()!=0){GlyphRealPortInit(port);return;}
    in_port=true;GlyphRealPortInit(port);in_port=false;port_complete=true;
}
#endif

#if defined(GLYPH_STRICT_HARDENING_CANDIDATE) && GLYPH_STRICT_HARDENING_CANDIDATE && (defined(ARDUINO_ARCH_RP2040) || defined(GLYPH_RT2_DCD_HOST))
#include "device/usbd_pvt.h"
#include "osal/osal.h"
extern "C" osal_queue_def_t _usbd_qdef;
namespace {
unsigned event_kind(const void *p){
    const auto *event=static_cast<const dcd_event_t*>(p);
    return event->event_id==DCD_EVENT_BUS_RESET?1u:event->event_id==DCD_EVENT_UNPLUGGED?2u:event->event_id==DCD_EVENT_SETUP_RECEIVED?3u:0u;
}
bool target_queue(tu_fifo_t *ff){return ff==&_usbd_qdef.ff&&get_core_num()==0;}
}
extern "C" bool __real_tu_fifo_write(tu_fifo_t*,const void*);
extern "C" bool __wrap_tu_fifo_write(tu_fifo_t *ff,const void *p){
    const bool result=__real_tu_fifo_write(ff,p);
    if(target_queue(ff)){
        const uint32_t exception=__get_current_exception();
        if(exception==16+USBCTRL_IRQ&&event_kind(p)==3)setup_observer.Queue(result);
        if(exception==16+USBCTRL_IRQ&&pre_setup_observer.Enabled()&&static_cast<const dcd_event_t*>(p)->event_id==DCD_EVENT_XFER_COMPLETE)pre_setup_observer.Queue(result);
        task_observer.QueueSent(exception==0?0:exception==16+USBCTRL_IRQ?1:2,
            event_kind(p),result,tu_fifo_count(ff));
    }
    return result;
}
extern "C" bool __real_tu_fifo_read(tu_fifo_t*,void*);
extern "C" bool __wrap_tu_fifo_read(tu_fifo_t *ff,void *p){
    const bool tracked=target_queue(ff);
    if(tracked)task_observer.QueueReadBegin();
    const bool result=__real_tu_fifo_read(ff,p);
    if(tracked)task_observer.QueueReadEnd(result?event_kind(p):0,result);
    return result;
}
extern "C" void __real_usbd_control_set_complete_callback(usbd_control_xfer_cb_t);
extern "C" void __wrap_usbd_control_set_complete_callback(usbd_control_xfer_cb_t callback){
    if(!callback&&get_core_num()==0)task_observer.ControlBegin();
    __real_usbd_control_set_complete_callback(callback);
}
// Builtin driver function-pointer relocations are wrapped by GNU ld; local
// empty XInput reset has no external relocation and is deliberately untouched.
#define GLYPH_RESET_WRAPPER(name,index,before,after) \
extern "C" void __real_##name(uint8_t); \
extern "C" void __wrap_##name(uint8_t port){ \
    const bool track=port==0&&get_core_num()==0; \
    if(track){task_observer.ClassBoundary(index,false);if(before)task_observer.ClassStage(before);} \
    __real_##name(port); \
    if(track){task_observer.ClassBoundary(index,true);if(after)task_observer.ClassStage(after);} \
}
GLYPH_RESET_WRAPPER(cdcd_reset,0,2,3)
GLYPH_RESET_WRAPPER(mscd_reset,1,0,0)
GLYPH_RESET_WRAPPER(hidd_reset,2,0,0)
GLYPH_RESET_WRAPPER(midid_reset,3,4,5)
#undef GLYPH_RESET_WRAPPER
#endif
