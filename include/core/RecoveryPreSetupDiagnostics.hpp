#pragma once
#include <atomic>
#include <cstdint>
#include "core/RecoverySetupIrqDiagnostics.hpp"

// Core0 USBCTRL is the sole writer. Each bank closes before calling vendor
// code, so a nonreturning callback still permits bounded independent readback.
namespace RecoveryPreSetupDiagnostics {
enum Panic : uint32_t { None=0, InactiveEndpoint=1, UnhandledIrq=2, OtherUsb=3 };
struct Snapshot {
    uint32_t valid=0, irq_entered=0, irq_returned=0, irq_active=0, irq_latest_returned=0;
    uint32_t irq_pre_ints=0, irq_post_ints=0;
    uint32_t ep_entered=0, ep_returned=0, ep_irq=0, ep_addr=0, ep_active=0, ep_buf_status=0, ep_result=0, ep_inactive=0, ep_pointer=0;
    uint32_t sof_entered=0, sof_returned=0, xfer_entered=0, xfer_returned=0, xfer_accepted=0, xfer_dropped=0;
    uint32_t panic_kind=0, panic_irq=0;
};
class State {
    using Word=std::atomic<uint32_t>;
    Word enabled{0},irq_seq{0},ep_seq{0},event_seq{0},panic_seq{0};
    Word entered{0},returned{0},active{0},latest{0},pre{0},post{0};
    Word ep_entered{0},ep_returned{0},ep_irq{0},ep_addr{0},ep_active{0},ep_buf{0},ep_result{0},ep_inactive{0},ep_pointer{0};
    Word sof_entered{0},sof_returned{0},xfer_entered{0},xfer_returned{0},accepted{0},dropped{0},panic_kind{0},panic_irq{0};
    static void bump(Word &v){const uint32_t n=v.load();v.store(n==UINT32_MAX?n:n+1);}
    static void edge(Word &s){s.store(s.load()+1);}
public:
    void Enable(){enabled.store(1);}
    bool Enabled()const{return enabled.load()!=0;}
    void IrqEnter(uint32_t ints){if(!Enabled())return;edge(irq_seq);bump(entered);active.store(entered.load());pre.store(ints);edge(irq_seq);}
    void IrqReturn(uint32_t ints){if(!Enabled())return;edge(irq_seq);bump(returned);latest.store(active.load());active.store(0);post.store(ints);edge(irq_seq);}
    void EndpointEnter(uint32_t addr,bool is_active,uint32_t status,uint32_t pointer){edge(ep_seq);bump(ep_entered);ep_irq.store(active.load());ep_pointer.store(pointer);ep_addr.store(addr);ep_active.store(is_active?1u:0u);ep_buf.store(status);if(!is_active)bump(ep_inactive);edge(ep_seq);}
    void EndpointReturn(bool result){edge(ep_seq);bump(ep_returned);ep_result.store(result?1u:0u);edge(ep_seq);}
    void Event(bool sof,bool returning){edge(event_seq);if(sof)bump(returning?sof_returned:sof_entered);else bump(returning?xfer_returned:xfer_entered);edge(event_seq);}
    void Queue(bool ok){edge(event_seq);bump(ok?accepted:dropped);edge(event_seq);}
    void PanicEntered(uint32_t kind){edge(panic_seq);panic_kind.store(kind);panic_irq.store(active.load());edge(panic_seq);}
    void ReadInto(Snapshot &s)const {
        s={};const uint32_t a=irq_seq.load(),b=ep_seq.load(),c=event_seq.load(),d=panic_seq.load();if((a|b|c|d)&1u)return;
        s.irq_entered=entered.load();s.irq_returned=returned.load();s.irq_active=active.load();s.irq_latest_returned=latest.load();s.irq_pre_ints=pre.load();s.irq_post_ints=post.load();
        s.ep_entered=ep_entered.load();s.ep_returned=ep_returned.load();s.ep_irq=ep_irq.load();s.ep_addr=ep_addr.load();s.ep_active=ep_active.load();s.ep_buf_status=ep_buf.load();s.ep_result=ep_result.load();s.ep_inactive=ep_inactive.load();s.ep_pointer=ep_pointer.load();
        s.sof_entered=sof_entered.load();s.sof_returned=sof_returned.load();s.xfer_entered=xfer_entered.load();s.xfer_returned=xfer_returned.load();s.xfer_accepted=accepted.load();s.xfer_dropped=dropped.load();s.panic_kind=panic_kind.load();s.panic_irq=panic_irq.load();
        if(a!=irq_seq.load()||b!=ep_seq.load()||c!=event_seq.load()||d!=panic_seq.load())return;s.valid=Enabled()?1u:0u;
    }
};
inline void Panel(const Snapshot &s,const RecoverySetupIrqDiagnostics::Snapshot &setup,const RecoveryTaskDiagnostics::Snapshot &task,uint32_t age,unsigned *pixels){
    using namespace RecoveryTaskDiagnostics;
    RecoverySetupIrqDiagnostics::Panel(setup,task,pixels);
    if(!s.valid||!setup.valid||!task.valid){for(unsigned i=0;i<8;++i)pixels[i]=Off;return;}
    unsigned live=s.irq_latest_returned?Green:Blue;
    if(s.irq_active)live=age>=1000000u?Red:Orange;
    if(s.panic_kind)live=White;
    unsigned branch=s.sof_returned?Yellow:Off;
    if(s.ep_entered)branch=Blue;
    if(s.ep_returned==s.ep_entered&&s.ep_returned)branch=Cyan;
    if(s.sof_entered>s.sof_returned)branch=Orange;
    if(s.ep_inactive)branch=Magenta;
    if(s.panic_kind==InactiveEndpoint)branch=White;
    else if(s.panic_kind==UnhandledIrq)branch=Red;
    else if(s.panic_kind)branch=Green;
    pixels[2]=pixels[3]=live;pixels[4]=pixels[5]=branch;
}
}
