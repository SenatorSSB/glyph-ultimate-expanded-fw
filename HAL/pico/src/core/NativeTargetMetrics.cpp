#include "core/NativeTargetMetrics.hpp"
#if GLYPH_NATIVE_TARGET_METRICS
#include <atomic>
#include <cstring>
#include <climits>
#include <initializer_list>
#ifdef GLYPH_NATIVE_METRICS_HOST
#include "native_metrics_host.hpp"
#else
#include <hardware/structs/timer.h>
#include <hardware/sync.h>
#include "native_target_source.hpp"
#endif

// Assembly initializes these own-core words without a C frame or constructor.
extern "C" {
struct NativeMetricScanState {
    uint32_t bottom, usable_bottom, top, initial_sp, minimum_sp, lowest_changed;
    uint32_t cursor, generation, max_chunk_us, flags, publish_version, last_chunk_us;
};
NativeMetricScanState glyph_native_metric_scans[2]{};
}
namespace native_metrics {
namespace {
constexpr uint32_t kPaint = 0xade175c3;
constexpr uint32_t kInitialized=1, kScanComplete=2, kBadBounds=4, kBottomExcluded=8,
    kEntryEntered=16, kBadSp=32, kFirstChanged=64, kUnstable=128, kGenerationExhausted=256;
constexpr uint32_t kSessionExpired=1u<<6, kFrameRefused=1u<<7,
    kGenerationChanged=1u<<8, kActivationRefused=1u<<9,
    kRecovered=1u<<10, kCalibrationIncomplete=1u<<11, kCaptureExhausted=1u<<12;
struct Mailbox { std::atomic<uint32_t> version, used_sp, generation, max_chunk, flags; };
static_assert(sizeof(std::atomic<uint32_t>)==4 && alignof(std::atomic<uint32_t>)==4,"aligned atomic word");
static_assert(sizeof(Mailbox)==20 && sizeof(NativeMetricScanState)==48,"frozen mailbox/scan layout");
Mailbox mailboxes[2]{};
Statistic statistics[3]{};
uint32_t overhead[3]{};
uint8_t response[kResponseBytes]{};
struct Receive { uint8_t bytes[16]; uint32_t started; uint8_t used, phase, reserved[2]; } rx{};
uint32_t last_tx_ms=0, capture_sequence=0, native_generation=0, run_flags=0;
static_assert(sizeof(rx)==24,"frozen diagnostic parser layout");
static_assert(sizeof(glyph_native_metric_scans)+sizeof(mailboxes)+sizeof(statistics)+sizeof(overhead)+
              sizeof(response)+sizeof(rx)+4*sizeof(uint32_t)==408,"diagnostic mutable static layout");
void Put(uint8_t *p,uint64_t value,unsigned count) { for(unsigned i=0;i<count;++i)p[i]=uint8_t(value>>(8*i)); }
uint64_t Get(const uint8_t *p,unsigned count) { uint64_t result=0;for(unsigned i=0;i<count;++i)result|=uint64_t(p[i])<<(8*i);return result; }
void Accumulate(Statistic &s,uint32_t value,unsigned index) {
    if (!s.count) s.minimum=value;
    else if(value<s.minimum)s.minimum=value;
    if(value>s.maximum)s.maximum=value;
    if(s.count==UINT32_MAX)run_flags|=1u<<(2*index);else ++s.count;
    const uint64_t sum=(uint64_t(s.sum_high)<<32)|s.sum_low;
    const uint64_t next=UINT64_MAX-sum<value?UINT64_MAX:sum+value;
    if(UINT64_MAX-sum<value)run_flags|=1u<<(2*index+1);
    s.sum_low=uint32_t(next);s.sum_high=uint32_t(next>>32);
}
void Maximum(uint32_t &out,uint32_t value) { if(value>out)out=value; }
uint32_t SaveIrq() {
#ifdef GLYPH_NATIVE_METRICS_HOST
    return NativeMetricHostSaveIrq();
#else
    return save_and_disable_interrupts();
#endif
}
void RestoreIrq(uint32_t state) {
#ifdef GLYPH_NATIVE_METRICS_HOST
    NativeMetricHostRestoreIrq(state);
#else
    restore_interrupts(state);
#endif
}
uint32_t StackPointer() {
#ifdef GLYPH_NATIVE_METRICS_HOST
    return NativeMetricHostSp();
#else
    uint32_t sp;asm volatile("mov %0, sp":"=r"(sp));return sp;
#endif
}
uint32_t StackWord(uint32_t address) {
#ifdef GLYPH_NATIVE_METRICS_HOST
    return NativeMetricHostWord(address);
#else
    return *reinterpret_cast<const volatile uint32_t *>(address);
#endif
}
// One high/low/high pass. An incoherent timer cannot create valid evidence.
bool Uptime(uint64_t &time) {
#ifdef GLYPH_NATIVE_METRICS_HOST
    return NativeMetricHostUptime(time);
#else
    const uint32_t high=timer_hw->timerawh,low=timer_hw->timerawl,after=timer_hw->timerawh;
    time=(uint64_t(high)<<32)|low;return high==after;
#endif
}
void Publish(unsigned core,NativeMetricScanState &s) {
    if(s.publish_version>=UINT32_MAX-1) {s.flags|=kGenerationExhausted;return;}
    if(s.publish_version==UINT32_MAX-3)s.flags|=kGenerationExhausted;
    auto &m=mailboxes[core];const uint32_t odd=s.publish_version+1,even=odd+1;
    const uint32_t used=s.top-((s.lowest_changed<s.initial_sp)?s.lowest_changed:s.initial_sp);
    const uint32_t sampled=s.top-s.minimum_sp;
    m.version.store(odd,std::memory_order_seq_cst);
    m.used_sp.store((used&65535u)|(sampled<<16),std::memory_order_seq_cst);
    m.generation.store(s.generation,std::memory_order_seq_cst);
    m.max_chunk.store(s.max_chunk_us,std::memory_order_seq_cst);
    m.flags.store(s.flags&65535u,std::memory_order_seq_cst);
    m.version.store(even,std::memory_order_seq_cst);s.publish_version=even;
}
bool ReadMailbox(unsigned core,uint8_t *out) {
    auto &m=mailboxes[core];const uint32_t first=m.version.load(std::memory_order_seq_cst);
    const uint32_t used=m.used_sp.load(std::memory_order_seq_cst),generation=m.generation.load(std::memory_order_seq_cst);
    const uint32_t max_chunk=m.max_chunk.load(std::memory_order_seq_cst),flags=m.flags.load(std::memory_order_seq_cst);
    const uint32_t last=m.version.load(std::memory_order_seq_cst);
    if(!first||(first&1)||first!=last) {Put(out+12,kUnstable,2);return false;}
    Put(out,used,4);Put(out+4,generation,4);Put(out+8,max_chunk,4);Put(out+12,flags,2);
    return (flags&(kInitialized|kScanComplete|kEntryEntered|kBottomExcluded))==(kInitialized|kScanComplete|kEntryEntered|kBottomExcluded)&&
        !(flags&(kBadBounds|kBadSp|kFirstChanged|kGenerationExhausted));
}
}
uint32_t Now() {
#ifdef GLYPH_NATIVE_METRICS_HOST
    return NativeMetricHostNow();
#else
    return timer_hw->timerawl;
#endif
}
void Calibrate() {
    // Exactly once in core0 startup, before backend activation and polling.
    if(statistics[2].count)return;
    for(unsigned i=0;i<16;++i) {const uint32_t start=Now(),end=Now();Accumulate(statistics[2],end-start,2);}
}
void RecordFrame(uint32_t begin,uint32_t end,uint32_t before,uint32_t after) {
    if(before!=after)run_flags|=kGenerationChanged;
    if(!before||!after||before!=after)run_flags|=kFrameRefused;
    else if(native_generation&&native_generation!=before)run_flags|=kGenerationChanged;
    else {native_generation=before;Accumulate(statistics[0],end-begin,0);}
    Maximum(overhead[0],Now()-end);
}
void RecordActivation(uint32_t begin,uint32_t end,uint32_t generation,bool accepted,bool recovered) {
    if(!statistics[0].count) {
        // Backend initialization publishes primary then viewer using the same
        // existing real activation path. Retain only the latest provisional
        // boot interval; the first native frame latches that final generation.
        // No activation is suppressed, replayed, or included twice in evidence.
        statistics[1]={};
        run_flags&=~(kActivationRefused|kRecovered);
        native_generation=accepted?generation:0;
        if(!accepted||!generation)run_flags|=kActivationRefused;
        else {Accumulate(statistics[1],end-begin,1);if(recovered)run_flags|=kRecovered;}
    } else {
        // A later publication is outside the single boot-selected interval.
        run_flags|=kActivationRefused;
        if(generation!=native_generation)run_flags|=kGenerationChanged;
    }
    Maximum(overhead[1],Now()-end);
}
void RecordObserver(uint32_t begin) {Maximum(overhead[2],Now()-begin);}
void ServiceCore(unsigned core) {
    if(core>1)return;
    const uint32_t begin=Now();auto &s=glyph_native_metric_scans[core];
    if(!(s.flags&kInitialized)||s.flags&kBadBounds) {s.flags|=kBadBounds;Publish(core,s);return;}
    const uint32_t irq=SaveIrq(),sp=StackPointer();
    if((sp&7)||sp<s.usable_bottom||sp>s.top)s.flags|=kBadSp;
    else if(sp<s.minimum_sp)s.minimum_sp=sp;
    if(s.bottom+32!=s.usable_bottom||s.top-s.bottom!=2048||
       (s.cursor&3)||s.cursor<s.usable_bottom||s.cursor>s.top) s.flags|=kBadBounds;
    else {
        for(unsigned i=0;i<16&&s.cursor<s.top;++i,s.cursor+=4) {
            if(StackWord(s.cursor)!=kPaint) {if(s.cursor<s.lowest_changed)s.lowest_changed=s.cursor;if(s.cursor==s.usable_bottom)s.flags|=kFirstChanged;}
        }
        if(s.cursor==s.top) {
            s.flags|=kScanComplete;
            if(s.generation==UINT32_MAX)s.flags|=kGenerationExhausted;else ++s.generation;
            s.cursor=s.usable_bottom;
        }
    }
    RestoreIrq(irq);
    // Publishing belongs to the scan cost. The final maximum store is outside
    // the measured span, and appears in the next complete mailbox publication.
    Publish(core,s);s.last_chunk_us=Now()-begin;Maximum(s.max_chunk_us,s.last_chunk_us);
}
void ExpireRequest(uint32_t now) {if(rx.used&&uint32_t(now-rx.started)>=250) {rx.used=0;rx.phase=0;}}
void DiscardRequest() {rx.used=0;rx.phase=0;}
bool ConsumeRequest(uint8_t byte,uint32_t now,bool &candidate) {
    ExpireRequest(now);
    if(rx.phase==2) {
        // Preserve the first complete token. A further frame is consumed only
        // to classify ambiguity, without writing into that candidate buffer.
        if(rx.used<4 && byte!=kMagic[rx.used]) {rx.used=byte==kMagic[0]?1:0;return rx.used!=0;}
        ++rx.used;
        if(rx.used==16) {rx.used=0;candidate=true;}
        return true;
    }
    if(rx.used<4) {
        if(byte!=kMagic[rx.used]) {rx.used=byte==kMagic[0]?1:0;rx.started=now;return rx.used!=0;}
        if(!rx.used)rx.started=now;
        rx.bytes[rx.used++]=byte;
        if(rx.used==4)rx.phase=1;
        return true;
    }
    rx.bytes[rx.used++]=byte;
    if(rx.used==16) {
        rx.used=0;rx.phase=0;
        if(rx.bytes[4]==1&&rx.bytes[5]==1&&Get(rx.bytes+6,2)==16&&Get(rx.bytes+8,8)) {rx.phase=2;candidate=true;}
    }
    return true;
}
bool CanRespond(uint32_t now) {return rx.phase==2&&!rx.used&&(!capture_sequence||uint32_t(now-last_tx_ms)>=1000)&&capture_sequence!=UINT32_MAX;}
const uint8_t *Snapshot(uint32_t,uint32_t actual_generation) {
    if(capture_sequence==UINT32_MAX-1)run_flags|=kCaptureExhausted;
    std::memset(response,0,sizeof(response));std::memcpy(response,kMagic,4);
    response[4]=1;response[5]=0x81;Put(response+6,sizeof(response),2);Put(response+8,Get(rx.bytes+8,8),8);response[17]=2;
    uint16_t valid=(1u<<7)|(1u<<8);bool invalid=false;
    if(statistics[0].count)valid|=1u;
    if(statistics[1].count)valid|=2u;
    if(statistics[2].count==16)valid|=4u;else run_flags|=kCalibrationIncomplete;
    if(ReadMailbox(0,response+108))valid|=8u;
    if(ReadMailbox(1,response+124))valid|=16u;
    for(unsigned offset:{120u,136u})if(Get(response+offset,2)&(kBadBounds|kBadSp|kFirstChanged|kGenerationExhausted))invalid=true;
    std::memcpy(response+20,kNativeTargetSourceSha,20);
    Put(response+152,kNativeTargetSourceFlags,2);
    if(kNativeTargetSourceFlags==3)valid|=32u;
    if(native_generation&&actual_generation==native_generation)valid|=64u;
    else if(native_generation||!actual_generation) {run_flags|=kGenerationChanged;invalid=true;}
    uint64_t uptime=0;
    const bool coherent=Uptime(uptime);
    if(!coherent)uptime=0; // unavailable; never encode a torn value as exact uptime
    if(!coherent||uptime>=3600000000ull) {run_flags|=kSessionExpired;invalid=true;}
    Put(response+156,uptime/1000000ull>UINT32_MAX?UINT32_MAX:uptime/1000000ull,4);
    Put(response+40,capture_sequence==UINT32_MAX?UINT32_MAX:capture_sequence+1,4);Put(response+44,native_generation,4);
    for(unsigned j=0;j<3;++j) {
        const auto &s=statistics[j];const uint32_t words[5]={s.count,s.minimum,s.maximum,s.sum_low,s.sum_high};
        for(unsigned i=0;i<5;++i)Put(response+48+20*j+4*i,words[i],4);
    }
    for(unsigned i=0;i<3;++i)Put(response+140+4*i,overhead[i],4);
    if(run_flags&(kSessionExpired|kGenerationChanged|kFrameRefused|kActivationRefused|kCaptureExhausted))invalid=true;
    response[16]=invalid?2:((valid==511&&!(run_flags&~kRecovered))?0:1);
    Put(response+18,valid,2);Put(response+154,run_flags,2);return response;
}
void ResponseAdmitted(uint32_t now) {
    if(capture_sequence==UINT32_MAX)run_flags|=kCaptureExhausted;
    else ++capture_sequence;
    last_tx_ms=now;DiscardRequest();
}
}
#endif
