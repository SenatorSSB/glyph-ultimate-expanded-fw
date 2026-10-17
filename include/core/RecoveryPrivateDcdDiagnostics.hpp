#pragma once
#include <atomic>
#include <cstdint>
#include "core/RecoveryPrivateDcdMarkers.h"
#include "core/RecoveryPreSetupDiagnostics.hpp"

// One serialized USBCTRL writer. A marker publishes and closes its bank before
// vendor execution resumes; a later nonreturn cannot strand the bank open.
// Counts/IDs saturate at UINT32_MAX; no allocation, IRQ logging, MMIO or LED I/O.
// History starts with the first boot-lifetime private handler call. Enable gates
// valid publication only; it never resets history or suppresses normal-boot stores.
namespace RecoveryPrivateDcdDiagnostics {
// Marker mask bits13/14 retain the actual private false/true SETUP predicate.
constexpr uint32_t SetupTestFalse=1u<<13,SetupTestTrue=1u<<14;
// Exact pinned SDK USB_INTS bits; checked against SDK definitions by host proof.
constexpr uint32_t SetupBit=0x10000u,ResetBit=0x1000u,BuffBit=0x10u;
struct Snapshot {
    uint32_t valid=0,entries=0,returns=0,setup_status_count=0,reset_status_count=0,buff_status_count=0,multi_status_count=0;
    uint32_t ever_status=0,latest_id=0,latest_status=0,latest_markers=0,active=0;
    uint32_t first_setup_id=0,first_setup_status=0,first_setup_markers=0;
    uint32_t latest_setup_id=0,latest_setup_status=0,latest_setup_markers=0;
    uint32_t setup_test_false_count=0,marker_calls=0;
    uint32_t enabled_setup_count=0,first_enabled_setup_id=0,first_enabled_setup_status=0,first_enabled_setup_markers=0;
};
class State {
    using Word=std::atomic<uint32_t>;
    static_assert(sizeof(Word)==4 && alignof(Word)>=4,"aligned lock-free word bank required");
    // Cortex-M0 lacks general atomic RMW support. Only aligned load/store is
    // used here; final target disassembly must prove no atomic library helper.
    alignas(4) Word enabled{0},seq{0},entries{0},returns{0},setup_count{0},reset_count{0},buff_count{0},multi_count{0};
    Word ever{0},id{0},status{0},markers{0},active{0},first_id{0},first_status{0},first_markers{0};
    Word setup_id{0},setup_status{0},setup_markers{0},false_count{0},calls{0};
    Word enabled_setup_count{0},enabled_setup_id{0},enabled_setup_status{0},enabled_setup_markers{0};
    static void bump(Word &v){const uint32_t n=v.load();v.store(n==UINT32_MAX?n:n+1);}
public:
    void Enable(){enabled.store(1);}
    bool Enabled()const{return enabled.load()!=0;}
    void Marker(uint32_t marker,uint32_t value){
        if(marker>GLYPH_DCD_PRIVATE_RETURN)return;
        seq.store(seq.load()+1);bump(calls);
        if(marker==GLYPH_DCD_PRIVATE_ENTRY){
            bump(entries);id.store(entries.load());active.store(id.load());
            status.store(0);markers.store(0);
        }
        if(active.load()){
            markers.store(markers.load()|(1u<<marker));
            if(marker==GLYPH_DCD_PRIVATE_STATUS){
                status.store(value);ever.store(ever.load()|value);
                if(value&SetupBit){
                    bump(setup_count);setup_id.store(id.load());setup_status.store(value);
                    if(!first_id.load()){first_id.store(id.load());first_status.store(value);}
                    if(Enabled()){
                        bump(enabled_setup_count);
                        if(!enabled_setup_id.load()){enabled_setup_id.store(id.load());enabled_setup_status.store(value);}
                    }
                }
                if(value&ResetBit)bump(reset_count);
                if(value&BuffBit)bump(buff_count);
                if(value&&(value&(value-1u)))bump(multi_count);
            }
            if(marker==GLYPH_DCD_PRIVATE_SETUP_TEST){markers.store(markers.load()|(value?SetupTestTrue:SetupTestFalse));if(!value)bump(false_count);}
            if(status.load()&SetupBit){
                setup_markers.store(markers.load());
                if(first_id.load()==id.load()){first_markers.store(markers.load());}
                if(enabled_setup_id.load()==id.load())enabled_setup_markers.store(markers.load());
            }
            if(marker==GLYPH_DCD_PRIVATE_RETURN){bump(returns);active.store(0);}
        }
        seq.store(seq.load()+1);
    }
    void ReadInto(Snapshot &s)const{
        s={};const uint32_t a=seq.load();if(a&1u)return;
        s.entries=entries.load();s.returns=returns.load();s.setup_status_count=setup_count.load();s.reset_status_count=reset_count.load();s.buff_status_count=buff_count.load();s.multi_status_count=multi_count.load();
        s.ever_status=ever.load();s.latest_id=id.load();s.latest_status=status.load();s.latest_markers=markers.load();s.active=active.load();
        s.first_setup_id=first_id.load();s.first_setup_status=first_status.load();s.first_setup_markers=first_markers.load();
        s.latest_setup_id=setup_id.load();s.latest_setup_status=setup_status.load();s.latest_setup_markers=setup_markers.load();
        s.setup_test_false_count=false_count.load();s.marker_calls=calls.load();
        s.enabled_setup_count=enabled_setup_count.load();s.first_enabled_setup_id=enabled_setup_id.load();s.first_enabled_setup_status=enabled_setup_status.load();s.first_enabled_setup_markers=enabled_setup_markers.load();
        if(a!=seq.load())return;s.valid=Enabled()?1u:0u;
    }
};
inline void Panel(const Snapshot &s,const RecoveryPreSetupDiagnostics::Snapshot &pre,const RecoverySetupIrqDiagnostics::Snapshot &setup,const RecoveryTaskDiagnostics::Snapshot &task,unsigned *pixels){
    using namespace RecoveryTaskDiagnostics;
    RecoverySetupIrqDiagnostics::Panel(setup,task,pixels);
    if(!s.valid||!pre.valid||!setup.valid||!task.valid){for(unsigned i=0;i<8;++i)pixels[i]=Off;return;}
    // RAW means any historical SIE/INTR/INTS SETUP-positive sample, never all
    // three simultaneous. The three individual sticky bits remain in telemetry.
    const bool raw=((setup.independent_seen|setup.foreground_seen|setup.irq_seen)&11u)!=0;
    unsigned local=s.entries?(raw?Cyan:Blue):(raw?Magenta:Green);
    if(s.setup_status_count)local=Orange; // global SETUP only before observer enable
    if(s.enabled_setup_count)local=Yellow;
    if(pre.panic_kind)local=Red;
    unsigned branch=Off;
    if(s.first_setup_id){
        const uint32_t m=s.first_enabled_setup_id?s.first_enabled_setup_markers:s.first_setup_markers;
        branch=Red; // can still be in earlier SOF/BUFF, not proof of C branch failure
        if(m&(1u<<GLYPH_DCD_PRIVATE_SETUP_ENTERED))branch=Orange;
        if(m&(1u<<GLYPH_DCD_PRIVATE_PID_DONE))branch=Yellow;
        if(m&(1u<<GLYPH_DCD_PRIVATE_BEFORE_EVENT))branch=Cyan;
        if(m&(1u<<GLYPH_DCD_PRIVATE_AFTER_EVENT))branch=Green;
        if(m&((1u<<GLYPH_DCD_PRIVATE_AFTER_CLEAR)|(1u<<GLYPH_DCD_PRIVATE_RETURN)))branch=White;
    }
    pixels[0]=pixels[1]=Off;pixels[2]=pixels[3]=local;pixels[4]=pixels[5]=branch;
}
}
