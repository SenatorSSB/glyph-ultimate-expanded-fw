#pragma once
#include <atomic>
#include <cstdint>
#include "core/RecoveryPrivateDcdMarkers.h"
#include "core/RecoveryPreSetupDiagnostics.hpp"

// One serialized core0 USBCTRL writer; core1 makes one bounded read attempt.
// Each hook closes its publication before vendor execution resumes. Boot history
// is never reset by Enable, including the immutable first same-invocation late tuple.
namespace RecoveryPrivateDcdDiagnostics {
// Exact pinned SDK USB_INTS bits; checked against SDK definitions by host proof.
constexpr uint32_t SetupBit=0x10000u,ResetBit=0x1000u,BuffBit=0x10u;
enum Gate : uint32_t { NvicEnabled=1u,NvicPending=2u,PrimaskSet=4u };
enum Overflow : uint32_t {
    EntriesOverflow=1u,ReturnsOverflow=2u,SetupCountOverflow=4u,
    ResetCountOverflow=8u,BuffCountOverflow=16u,LateCountOverflow=32u,
    SequenceExhausted=64u
};
struct Snapshot {
    uint32_t valid=0,entries=0,returns=0;
    uint32_t setup_status_count=0,reset_status_count=0,buff_status_count=0;
    // latest_s0 belongs to entries; latest_s1/gates belong to returns. These
    // describe the same invocation only when entries==returns without overflow.
    uint32_t latest_s0=0,latest_s1=0,latest_gates=0,late_count=0;
    uint32_t first_late_id=0,first_late_s0=0,first_late_s1=0,first_late_gates=0;
    uint32_t first_post_late_setup_id=0,overflow_flags=0;
};
static_assert(sizeof(Snapshot)==64,"fixed sixteen-word private snapshot");
class State {
#ifdef GLYPH_RECOVERY_DIAGNOSTICS_HOST
    friend struct StateTestAccess;
#endif
    using Word=std::atomic<uint32_t>;
    static_assert(sizeof(Word)==4 && alignof(Word)>=4,"aligned lock-free word bank required");
    // Only aligned atomic loads/stores, no RMW. Final ARM disassembly proves
    // these use no library helper. The sequence cannot wrap and cause ABA.
    alignas(4) Word enabled{0},seq{0},entries{0},returns{0};
    Word setup_status_count{0},reset_status_count{0},buff_status_count{0};
    Word latest_s0{0},latest_s1{0},latest_gates{0},late_count{0};
    Word first_late_id{0},first_late_s0{0},first_late_s1{0},first_late_gates{0};
    Word first_post_late_setup_id{0},overflow_flags{0};
    __attribute__((always_inline)) inline void flag(uint32_t bit){
        overflow_flags.store(overflow_flags.load(std::memory_order_relaxed)|bit,std::memory_order_relaxed);
    }
    __attribute__((always_inline)) inline uint32_t bump(Word &word,uint32_t bit){
        const uint32_t n=word.load(std::memory_order_relaxed);
        if(n==UINT32_MAX){flag(bit);return n;}
        word.store(n+1u,std::memory_order_relaxed);return n+1u;
    }
    __attribute__((always_inline)) inline bool begin(uint32_t &sequence){
        sequence=seq.load(std::memory_order_relaxed);
        if(sequence>=UINT32_MAX-3u){
            if(sequence==UINT32_MAX-3u){
                seq.store(sequence+1u,std::memory_order_relaxed);
                std::atomic_thread_fence(std::memory_order_release);
                flag(SequenceExhausted);
                seq.store(sequence+2u,std::memory_order_release);
            }
            return false; // terminal readable bank; retain all selected history
        }
        seq.store(sequence+1u,std::memory_order_relaxed);
        std::atomic_thread_fence(std::memory_order_release);return true;
    }
    __attribute__((always_inline)) inline void end(uint32_t sequence){seq.store(sequence+2u,std::memory_order_release);}
public:
    void Enable(){enabled.store(1,std::memory_order_release);}
    bool Enabled()const{return enabled.load(std::memory_order_acquire)!=0;}
    __attribute__((always_inline)) inline void Initial(uint32_t s0){
        uint32_t sequence;if(!begin(sequence))return;
        const uint32_t id=bump(entries,EntriesOverflow);
        latest_s0.store(s0,std::memory_order_relaxed);
        if(s0&SetupBit){
            bump(setup_status_count,SetupCountOverflow);
            const uint32_t first=first_late_id.load(std::memory_order_relaxed);
            if(first&&id>first&&!first_post_late_setup_id.load(std::memory_order_relaxed))
                first_post_late_setup_id.store(id,std::memory_order_relaxed);
        }
        if(s0&ResetBit)bump(reset_status_count,ResetCountOverflow);
        if(s0&BuffBit)bump(buff_status_count,BuffCountOverflow);
        end(sequence);
    }
    // s0 and s1 are the actual same-invocation handler locals, not MMIO rereads.
    // gates were sampled sequentially on core0 after s1. This records reaching
    // the normal-return hook, not completed shared dispatch or EXC_RETURN.
    __attribute__((always_inline)) inline void Return(uint32_t s0,uint32_t s1,uint32_t gates){
        uint32_t sequence;if(!begin(sequence))return;
        bump(returns,ReturnsOverflow);
        latest_s1.store(s1,std::memory_order_relaxed);
        latest_gates.store(gates,std::memory_order_relaxed);
        if(!(s0&SetupBit)&&(s1&SetupBit)){
            bump(late_count,LateCountOverflow);
            if(!first_late_id.load(std::memory_order_relaxed)){
                first_late_id.store(entries.load(std::memory_order_relaxed),std::memory_order_relaxed);
                first_late_s0.store(s0,std::memory_order_relaxed);
                first_late_s1.store(s1,std::memory_order_relaxed);
                first_late_gates.store(gates,std::memory_order_relaxed);
            }
        }
        end(sequence);
    }
    void ReadInto(Snapshot &s)const{
        // A later payload load synchronizes its preceding release fence with
        // our acquire fence, forcing the ending sequence load past that writer's
        // odd store. Initial acquire excludes older payload. No sequence wraps;
        // all payload is atomic. Reject overlap without a spin or retry.
        s={};const uint32_t a=seq.load(std::memory_order_acquire);if(a&1u)return;
        s.entries=entries.load(std::memory_order_relaxed);s.returns=returns.load(std::memory_order_relaxed);
        s.setup_status_count=setup_status_count.load(std::memory_order_relaxed);
        s.reset_status_count=reset_status_count.load(std::memory_order_relaxed);
        s.buff_status_count=buff_status_count.load(std::memory_order_relaxed);
        s.latest_s0=latest_s0.load(std::memory_order_relaxed);s.latest_s1=latest_s1.load(std::memory_order_relaxed);s.latest_gates=latest_gates.load(std::memory_order_relaxed);
        s.late_count=late_count.load(std::memory_order_relaxed);
        s.first_late_id=first_late_id.load(std::memory_order_relaxed);s.first_late_s0=first_late_s0.load(std::memory_order_relaxed);s.first_late_s1=first_late_s1.load(std::memory_order_relaxed);s.first_late_gates=first_late_gates.load(std::memory_order_relaxed);
        s.first_post_late_setup_id=first_post_late_setup_id.load(std::memory_order_relaxed);s.overflow_flags=overflow_flags.load(std::memory_order_relaxed);
        std::atomic_thread_fence(std::memory_order_acquire);
        if(a!=seq.load(std::memory_order_relaxed))return;s.valid=Enabled()?1u:0u;
    }
};
static_assert(sizeof(State)==68,"fixed fifteen-word payload plus enable/sequence");
inline void Panel(const Snapshot &s,const RecoveryPreSetupDiagnostics::Snapshot &pre,const RecoverySetupIrqDiagnostics::Snapshot &setup,const RecoveryTaskDiagnostics::Snapshot &task,unsigned *pixels){
    using namespace RecoveryTaskDiagnostics;
    RecoverySetupIrqDiagnostics::Panel(setup,task,pixels);
    if(!s.valid||!pre.valid||!setup.valid||!task.valid){for(unsigned i=0;i<8;++i)pixels[i]=Off;return;}
    // RAW is any historical positive SIE/INTR/INTS sample, not simultaneity.
    const bool raw=((setup.independent_seen|setup.foreground_seen|setup.irq_seen)&11u)!=0;
    unsigned local=s.entries?(raw?Cyan:Blue):(raw?Magenta:Green);
    if(s.overflow_flags)local=Magenta; // absence/count precision no longer known
    if(s.setup_status_count)local=Yellow; // retained positive remains a fact
    if(pre.panic_kind)local=Red;
    unsigned late=Off;
    if(s.first_late_id){
        late=s.entries>s.first_late_id?Cyan:Red;
        if(s.first_post_late_setup_id>s.first_late_id)late=White;
    }
    if(s.overflow_flags)late=Magenta; // never turn saturation into no-redispatch
    // Compact downstream hook entry shares ORANGE with the external boundary.
    if(pixels[6]==Magenta)pixels[6]=pixels[7]=Orange;
    pixels[0]=pixels[1]=Off;pixels[2]=pixels[3]=local;pixels[4]=pixels[5]=late;
}
}
