#include "core/RecoveryStartupDiagnostics.hpp"
#include "core/ResourceDiagnostics.hpp"
#include "core/RecoveryUsbDiagnostics.hpp"
#if defined(GLYPH_STRICT_HARDENING_CANDIDATE) && GLYPH_STRICT_HARDENING_CANDIDATE && (defined(ARDUINO_ARCH_RP2040) || defined(GLYPH_RECOVERY_DIAGNOSTICS_HOST))
#include <Adafruit_TinyUSB.h>
#include "hardware/clocks.h"
#include "hardware/pio.h"
#include "hardware/structs/usb.h"
#include "hardware/watchdog.h"
#include "neopixel_definitions.hpp"
#include "pico/time.h"

namespace RecoveryStartupDiagnostics {
namespace {
uint32_t current=0,previous=0;
std::atomic<uint32_t> handed_off{0},published_pair{0};
PIO indicator=nullptr;
int indicator_sm=-1;
bool indicator_attempted=false;
uint8_t shown_state=255;
uint64_t handoff_us=0,active_since_us=0;uint32_t last_active=0;
bool capture_ready=false,panel_shown=false;
std::atomic<uint32_t> dashboard{0},capture_active_age_us{0},capture_elapsed_us{0};
unsigned captured_pixels[8]={};
RecoveryTaskDiagnostics::Snapshot captured_task;
RecoverySetupIrqDiagnostics::Snapshot captured_setup;
RecoveryTaskDiagnostics::Snapshot task_sample;
RecoverySetupIrqDiagnostics::Snapshot setup_sample;

void InitializeIndicator() {
    if(indicator_attempted)return;
    indicator_attempted=true;
    // Exact four-instruction clockless program from pinned FastLED pio_gen.h,
    // T1=2/T2=5/T3=3 at8MHz; NEOPIXEL's GRB order. No DMA/IRQ/heap buffer.
    const uint16_t instructions[]={
        uint16_t(pio_encode_out(pio_x,1)),
        uint16_t(pio_encode_set(pio_pins,1)|pio_encode_delay(1)),
        uint16_t(pio_encode_mov(pio_pins,pio_x)|pio_encode_delay(4)),
        uint16_t(pio_encode_set(pio_pins,0)|pio_encode_delay(1))
    };
    const pio_program program{instructions,4,-1};
    const PIO units[]={pio0,pio1};
    for(PIO pio:units) {
        if(!pio_can_add_program(pio,&program))continue;
        const int sm=pio_claim_unused_sm(pio,false);
        if(sm<0)continue;
        const unsigned offset=pio_add_program(pio,&program);
        auto config=pio_get_default_sm_config();
        sm_config_set_wrap(&config,offset,offset+3);
        sm_config_set_set_pins(&config,LED_PIN,1);
        sm_config_set_out_pins(&config,LED_PIN,1);
        sm_config_set_out_shift(&config,false,true,24);
        sm_config_set_fifo_join(&config,PIO_FIFO_JOIN_TX);
        sm_config_set_clkdiv(&config,float(clock_get_hz(clk_sys))/8000000.0f);
        pio_gpio_init(pio,LED_PIN);
        pio_sm_set_consecutive_pindirs(pio,sm,LED_PIN,1,true);
        pio_sm_init(pio,sm,offset,&config);
        pio_sm_set_pins(pio,sm,0);
        pio_sm_set_enabled(pio,sm,true);
        indicator=pio;indicator_sm=sm;return;
    }
}

bool Show(unsigned state, unsigned progress=255) {
    if(!indicator||!pio_sm_is_tx_fifo_empty(indicator,indicator_sm))return false;
    // Only MB1 top-left menu pair. Sticky furthest progress; LF4 is dark.
    const uint32_t colors[]={0x001800u,0x061800u,0x181800u,0x001818u,
                             0x000018u,0x180018u,0x180000u,0x181818u};
    const uint32_t task_colors[]={0x001800u,0x061800u,0x001818u,0x000018u,0x180000u};
    const uint32_t progress_colors[]={0,0x181800u,0x180018u,0x180000u,0x181818u};
    const uint32_t mb1=progress==255?colors[state]:task_colors[state];
    const uint32_t second=progress==255?mb1:progress_colors[progress];
    // Preload while only our SM is disabled. USB IRQs remain enabled, but
    // cannot split this frame into separate latches between CPU FIFO puts.
    pio_sm_set_enabled(indicator,indicator_sm,false);
    // The empty4-word FIFO admits all4 words; no blocking put/wait-for-DMA.
    pio_sm_put(indicator,indicator_sm,mb1<<8);pio_sm_put(indicator,indicator_sm,second<<8);
    pio_sm_put(indicator,indicator_sm,0);pio_sm_put(indicator,indicator_sm,0);
    pio_sm_set_enabled(indicator,indicator_sm,true);
    // 96bits/800kHz=120us +80us low latch. IRQs remain enabled. This bounded
    // LED protocol interval is diagnostic perturbation, never a USB timing fix.
    busy_wait_us_32(200);
    return true;
}

// Eight words fit the joined TX FIFO before enabling this dedicated SM. No
// mid-frame CPU refill, blocking FIFO put, DMA, USB call, or clock change.
bool ShowPanel(){
    if(!indicator||!pio_sm_is_tx_fifo_empty(indicator,indicator_sm))return false;
    const uint32_t colors[]={0,0x001800u,0x061800u,0x181800u,0x001818u,
                             0x000018u,0x180018u,0x180000u,0x181818u};
    pio_sm_set_enabled(indicator,indicator_sm,false);
    for(unsigned color:captured_pixels)pio_sm_put(indicator,indicator_sm,colors[color]<<8);
    pio_sm_set_enabled(indicator,indicator_sm,true);
    // Inherited protocol interval, IRQs enabled. Eight pixels take240us;
    // hardware finishes independently after this200us interval and latches low.
    // No later frame is emitted, so no CPU wait for completion is needed.
    busy_wait_us_32(200);return true;
}

unsigned Flags() {
    unsigned flags=tud_inited()?1u:0u;
    if(Adafruit_USBD_CDC::getInstanceCount()==1)flags|=2;
    const uint8_t *desc=tud_descriptor_configuration_cb(0);
    // Pin uses a256-byte descriptor buffer. Refuse malformed bounds.
    if(desc&&desc[0]==9&&desc[1]==TUSB_DESC_CONFIGURATION) {
        const unsigned length=unsigned(desc[2])|(unsigned(desc[3])<<8);
        if(length>=9&&length<=256)for(unsigned offset=9;offset+2<=length;) {
            const unsigned n=desc[offset];if(n<2||offset+n>length)break;
            if(n>=9&&desc[offset+1]==TUSB_DESC_INTERFACE&&desc[offset+5]==TUSB_CLASS_CDC)flags|=4;
            offset+=n;
        }
    }
    if(usb_hw->sie_ctrl&USB_SIE_CTRL_PULLUP_EN_BITS)flags|=8;
    if(tud_connected())flags|=16;
    if(tud_mounted())flags|=32;
    if(tud_cdc_n_connected(0))flags|=64;
    if(indicator)flags|=128;
    return flags;
}
}
void HandOffIndicator(){
    // Core0 completes initialization and its final frame before publishing.
    // After this release, only core1 touches the SM/FIFO and scratch3.
    InitializeIndicator();shown_state=255;handoff_us=time_us_64();handed_off.store(1,std::memory_order_release);
}
void PublishIndependent(){
    if(!handed_off.load(std::memory_order_acquire)||panel_shown)return;
    if(!capture_ready){
        // Core1 performs only non-destructive USB MMIO sampling and bounded
        // atomic bank reads. No TinyUSB/Config/ProfileStore/shared USB locks.
        RecoveryUsbDiagnostics::ObserveIndependent();
        RecoveryUsbDiagnostics::TaskReadInto(task_sample);
        RecoveryUsbDiagnostics::SetupReadInto(setup_sample);
        const auto &s=task_sample;
        if(!s.valid||!setup_sample.valid)return; // one attempt per ordinary loop; never spin
        const uint64_t now=time_us_64();
        if(s.active!=last_active){last_active=s.active;active_since_us=now;}
        if(now-handoff_us<10000000u)return;
        const uint64_t age=s.active?now-active_since_us:0;
        RecoverySetupIrqDiagnostics::Panel(setup_sample,s,captured_pixels);
        captured_setup=setup_sample;
        uint32_t packed=0;for(unsigned i=0;i<8;++i)packed|=uint32_t(captured_pixels[i])<<(4*i);
        captured_task=s;
        for(unsigned i=0;i<8;++i)captured_task.pixels[i]=captured_pixels[i];
        captured_task.dashboard=packed;
        capture_active_age_us.store(age>UINT32_MAX?UINT32_MAX:uint32_t(age));
        capture_elapsed_us.store(now-handoff_us>UINT32_MAX?UINT32_MAX:uint32_t(now-handoff_us));
        dashboard.store(packed,std::memory_order_release);
        const uint32_t word=kDashboardMagic|(captured_pixels[0]<<12)|
            (captured_pixels[1]<<8)|(captured_pixels[4]<<4)|captured_pixels[6];
        published_pair.store(word,std::memory_order_release);watchdog_hw->scratch[3]=word;
        capture_ready=true;
    }
    if(ShowPanel())panel_shown=true; // unchanged settled panel is never refreshed
}
bool CapturedSetupInto(RecoverySetupIrqDiagnostics::Snapshot &out){
    if(!published_pair.load(std::memory_order_acquire)){out={};return false;}
    out=captured_setup;return true;
}
RecoveryTaskDiagnostics::Snapshot CapturedTask(){
    // Immutable after the single release publication; no shared mutable copy.
    if(!published_pair.load(std::memory_order_acquire))return {};
    return captured_task;
}
bool CapturedTaskInto(RecoveryTaskDiagnostics::Snapshot &out){
    if(!published_pair.load(std::memory_order_acquire)){out={};return false;}
    out=captured_task;return true;
}
uint32_t Dashboard(){return dashboard.load(std::memory_order_acquire);}
uint32_t CaptureActiveAgeUs(){return capture_active_age_us.load();}
uint32_t CaptureElapsedUs(){return capture_elapsed_us.load();}

void CapturePrevious(){previous=TakePrevious(watchdog_hw->scratch);current=0;}
void Mark(Phase phase) {
    if(phase==Phase::LoopEntered)RecoveryUsbDiagnostics::LoopEntered();
    if(handed_off.load(std::memory_order_acquire))return;
    const unsigned old=(current>>8)&15u;
    const unsigned next=unsigned(phase)>old?unsigned(phase):old;
    // Record entry before any indicator allocation/claim or USB observation.
    if(next>old||!current)watchdog_hw->scratch[3]=kMagic|(current&0xf000u)|(next<<8);
    InitializeIndicator();
    const unsigned flags=Flags();RecoveryUsbDiagnostics::Read();
    const unsigned state=RecoveryUsbDiagnostics::Furthest();
    const uint32_t value=kMagic|(state<<12)|(next<<8)|flags;
    if(current!=value){current=value;watchdog_hw->scratch[3]=value;}
    // A latched pixel requires no refresh. Retry a skipped frame, never rewrite
    // an unchanged successfully displayed state, even when raw flags change.
    if(shown_state!=state&&Show(state))shown_state=uint8_t(state);
}
void ValidInspectionCommandReceived(){
    RecoveryUsbDiagnostics::InspectionDecoded();Mark(Phase::RequestByteSeen);
}
uint32_t Current(){const uint32_t pair=published_pair.load(std::memory_order_acquire);return pair?pair:current;}
uint32_t Previous(){return previous;}
}
#endif
