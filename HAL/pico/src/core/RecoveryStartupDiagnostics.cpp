#include "core/RecoveryStartupDiagnostics.hpp"
#include "core/ResourceDiagnostics.hpp"
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
PIO indicator=nullptr;
int indicator_sm=-1;
bool indicator_attempted=false;
bool valid_inspection_command=false;
uint8_t shown_state=0;

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
        sm_config_set_clkdiv(&config,float(clock_get_hz(clk_sys))/8000000.0f);
        pio_gpio_init(pio,LED_PIN);
        pio_sm_set_consecutive_pindirs(pio,sm,LED_PIN,1,true);
        pio_sm_init(pio,sm,offset,&config);
        pio_sm_set_pins(pio,sm,0);
        pio_sm_set_enabled(pio,sm,true);
        indicator=pio;indicator_sm=sm;return;
    }
}

unsigned CoarseState(unsigned phase,unsigned flags) {
    if(phase<11)return 1; // red: application has not returned from SendReport
    if(flags&32u)return valid_inspection_command?5u:4u; // white / green
    return (flags&16u)?3u:2u; // blue: SETUP seen; yellow: not configured
}

bool Show(unsigned state) {
    if(!indicator||!pio_sm_is_tx_fifo_empty(indicator,indicator_sm))return false;
    // Sole physical signal: Mk6 MB1 top-left menu pair. LF4 pair stays dark.
    const uint32_t colors[]={0,0x001800u,0x181800u,0x000018u,0x180000u,0x181818u};
    const uint32_t mb1=colors[state];
    // Preload while only our SM is disabled. USB IRQs remain enabled, but
    // cannot split this frame into separate latches between CPU FIFO puts.
    pio_sm_set_enabled(indicator,indicator_sm,false);
    // The empty4-word FIFO admits all4 words; no blocking put/wait-for-DMA.
    pio_sm_put(indicator,indicator_sm,mb1<<8);pio_sm_put(indicator,indicator_sm,mb1<<8);
    pio_sm_put(indicator,indicator_sm,0);pio_sm_put(indicator,indicator_sm,0);
    pio_sm_set_enabled(indicator,indicator_sm,true);
    // 96bits/800kHz=120us +80us low latch. IRQs remain enabled. This bounded
    // LED protocol interval is diagnostic perturbation, never a USB timing fix.
    busy_wait_us_32(200);
    return true;
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
void CapturePrevious(){previous=TakePrevious(watchdog_hw->scratch);current=0;valid_inspection_command=false;shown_state=0;}
void Mark(Phase phase) {
    const unsigned old=(current>>8)&255u;
    const unsigned next=unsigned(phase)>old?unsigned(phase):old;
    // Record entry before any indicator allocation/claim or USB observation.
    if(next>old||!current)watchdog_hw->scratch[3]=kMagic|(next<<8);
    InitializeIndicator();
    const unsigned flags=Flags();const uint32_t value=kMagic|(next<<8)|flags;
    const unsigned state=CoarseState(next,flags);
    if(current==value&&shown_state==state)return;
    current=value;watchdog_hw->scratch[3]=value;
    // Keep existing changed-marker frame cadence; no startup waits added.
    // Repeated early frames all show red, never 13 transient phase colors.
    if(Show(state))shown_state=uint8_t(state);
}
void ValidInspectionCommandReceived(){
    valid_inspection_command=true;Mark(Phase::RequestByteSeen);
}
uint32_t Current(){return current;}
uint32_t Previous(){return previous;}
}
#endif
