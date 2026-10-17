#pragma once
#include <atomic>
#include <cstdint>
#include "core/RecoveryTaskDiagnostics.hpp"

// Observer banks have one serialized writer each: core1, core0 foreground,
// USBCTRL trampoline, and USBCTRL event boundary. No read-modify-write atomics.
// A tuple is sequential MMIO reads in one sample, not an atomic hardware instant.
namespace RecoverySetupIrqDiagnostics {
enum Raw : uint32_t { Sie=1, Intr=2, Inte=4, Ints=8, Force=16 };
enum Gate : uint32_t { NvicOn=1, NvicOff=2, Pending=4, NotPending=8,
    Masked=16, Unmasked=32, UsbException=64, OtherException=128,
    Thread=256, ResetDone=512, ResetNotDone=1024, PortReturned=2048,
    TinyUsbInitialized=4096 };
enum Condition : uint32_t { SieWithoutIntr=1, IntrMasked=2, IntrEnabledNoInts=4,
    IntsNvicOff=8, IntsGloballyMasked=16, IntsPending=32, IntsGateOpen=64 };
struct Snapshot {
    uint32_t valid=0, independent_seen=0, independent_tuples=0;
    uint32_t foreground_seen=0, foreground_tuples=0, foreground_gates=0, foreground_conditions=0;
    uint32_t irq_entries=0, irq_returns=0, irq_seen=0, irq_tuples=0, irq_gates=0, irq_conditions=0, irq_setup_entries=0;
    uint32_t irq_first_pre=0, irq_latest_pre=0, irq_latest_post=0;
    uint32_t setup_emit_entered=0, setup_emit_returned=0, setup_hook=0;
    uint32_t setup_accepted=0, setup_dropped=0, registration_captured=0, registration_duplicate=0, external_flags=0;
};
class State {
    using Word=std::atomic<uint32_t>;
    struct SampleBank {Word seq{0},seen{0},tuples{0},gates{0},conditions{0};};
    SampleBank independent,foreground,irq;
    Word enabled{0},registered{0},duplicate{0},setup_entries{0},entries{0},returns{0},first{0},pre{0},post{0};
    Word any_entered{0},any_returned{0},unexpected{0};
    Word emit_seq{0},emit_entered{0},emit_returned{0},hook{0},accepted{0},dropped{0};
    static void bump(Word &v){const uint32_t n=v.load();v.store(n==UINT32_MAX?n:n+1);}
    static void begin(Word &v){v.store(v.load()+1);}
    static void end(Word &v){v.store(v.load()+1);}
    static void sample(SampleBank &b,uint32_t raw,uint32_t gates){
        b.seen.store(b.seen.load()|raw);b.tuples.store(b.tuples.load()|(1u<<raw));
        // Gate evidence is associated with a SETUP-positive sample only.
        if(raw&(Sie|Intr|Ints))b.gates.store(b.gates.load()|gates);
        uint32_t condition=0;
        if((raw&Sie)&&!(raw&Intr))condition|=SieWithoutIntr;
        if((raw&Intr)&&!(raw&Inte))condition|=IntrMasked;
        if((raw&Intr)&&(raw&Inte)&&!(raw&Ints))condition|=IntrEnabledNoInts;
        if((raw&Ints)&&(gates&NvicOff))condition|=IntsNvicOff;
        if((raw&Ints)&&(gates&Masked))condition|=IntsGloballyMasked;
        if((raw&Ints)&&(gates&Pending))condition|=IntsPending;
        if((raw&Ints)&&(gates&NvicOn)&&(gates&Unmasked))condition|=IntsGateOpen;
        b.conditions.store(b.conditions.load()|condition);
    }
public:
    void Enable(){enabled.store(1);}
    bool Enabled()const{return enabled.load()!=0;}
    void Registered(){registered.store(1);}
    void DuplicateRegistration(){duplicate.store(1);}
    void Independent(uint32_t raw){if(!Enabled())return;begin(independent.seq);sample(independent,raw,0);end(independent.seq);}
    void Foreground(uint32_t raw,uint32_t gates){if(!Enabled())return;begin(foreground.seq);sample(foreground,raw,gates);end(foreground.seq);}
    void IrqEnter(uint32_t raw,uint32_t gates){if(!Enabled())return;begin(irq.seq);if(!entries.load())first.store(raw);bump(entries);if(raw&(Sie|Intr|Ints))bump(setup_entries);pre.store(raw);sample(irq,raw,gates);end(irq.seq);}
    void IrqReturn(uint32_t raw,uint32_t gates){if(!Enabled())return;begin(irq.seq);bump(returns);post.store(raw);sample(irq,raw,gates);end(irq.seq);}
    // These three flags accept multiple contexts. All writers only store 1;
    // they do not share a sequence bank or perform read-modify-write operations.
    void ExternalEnter(bool foreign){if(!Enabled())return;any_entered.store(1);if(foreign)unexpected.store(1);}
    void ExternalReturn(){if(Enabled())any_returned.store(1);}
    void EmitEnter(){if(!Enabled())return;begin(emit_seq);bump(emit_entered);end(emit_seq);}
    void EmitReturn(){if(!Enabled())return;begin(emit_seq);bump(emit_returned);end(emit_seq);}
    void Hook(){if(!Enabled())return;begin(emit_seq);bump(hook);end(emit_seq);}
    void Queue(bool ok){if(!Enabled())return;begin(emit_seq);bump(ok?accepted:dropped);end(emit_seq);}
    void ReadInto(Snapshot &s)const{
        s={};const uint32_t a=independent.seq.load(),b=foreground.seq.load(),c=irq.seq.load(),d=emit_seq.load();
        if((a|b|c|d)&1u)return;
        s.independent_seen=independent.seen.load();s.independent_tuples=independent.tuples.load();
        s.foreground_seen=foreground.seen.load();s.foreground_tuples=foreground.tuples.load();s.foreground_gates=foreground.gates.load();s.foreground_conditions=foreground.conditions.load();
        s.irq_entries=entries.load();s.irq_returns=returns.load();s.irq_seen=irq.seen.load();s.irq_tuples=irq.tuples.load();s.irq_gates=irq.gates.load();s.irq_conditions=irq.conditions.load();s.irq_setup_entries=setup_entries.load();
        s.irq_first_pre=first.load();s.irq_latest_pre=pre.load();s.irq_latest_post=post.load();
        s.setup_emit_entered=emit_entered.load();s.setup_emit_returned=emit_returned.load();s.setup_hook=hook.load();
        s.setup_accepted=accepted.load();s.setup_dropped=dropped.load();s.registration_captured=registered.load();s.registration_duplicate=duplicate.load();
        const uint32_t returned=any_returned.load(),entered=any_entered.load();
        s.external_flags=entered|(returned<<1)|(unexpected.load()<<2);
        if(a!=independent.seq.load()||b!=foreground.seq.load()||c!=irq.seq.load()||d!=emit_seq.load())return;
        s.valid=Enabled()&&!duplicate.load()?1u:0u;
    }
};
// Whole-button colors. Raw S/I/T is an unordered observed bitset; it is not a
// promotion sequence. INTE remains independently available in exact tuples.
inline void Panel(const Snapshot &s,const RecoveryTaskDiagnostics::Snapshot &task,unsigned *pixels){
    using namespace RecoveryTaskDiagnostics;
    for(unsigned i=0;i<8;++i)pixels[i]=Off; // MB1 menu pair intentionally dark
    if(!s.valid||!task.valid)return;
    const uint32_t raw=s.independent_seen|s.foreground_seen|s.irq_seen;
    const unsigned code=(raw&Sie?1u:0u)|(raw&Intr?2u:0u)|(raw&Ints?4u:0u);
    const unsigned colors[]={Off,Red,Yellow,Orange,Blue,Magenta,Cyan,White};
    pixels[2]=pixels[3]=colors[code];
    const uint32_t condition=s.foreground_conditions|s.irq_conditions;
    unsigned gate=code?Yellow:Off;
    // Each color proves presence of its condition; no absence is a timing proof.
    if((s.independent_tuples|s.foreground_tuples|s.irq_tuples)&0x0c0c0c0cu)gate=Red; // INTR + !INTE tuple
    if(condition&IntsNvicOff)gate=Orange;
    if(condition&IntsGloballyMasked)gate=Magenta;
    if(condition&IntsPending)gate=Blue;
    if(s.irq_setup_entries)gate=Green;
    if(s.irq_tuples&0xff00ff00u)gate=White; // trampoline read INTS; not handler local status
    pixels[4]=pixels[5]=gate;
    unsigned event=(s.external_flags&1u)?Orange:Off;
    if(s.setup_hook)event=Magenta;
    if(s.setup_accepted)event=Cyan;
    if(task.setup_consumed)event=Yellow;
    if(task.control_began)event=Blue;
    if(task.task_flags&7u)event=Green;
    if(task.configured_current||(task.task_flags&16u))event=White;
    if(s.setup_dropped)event=Red;
    pixels[6]=pixels[7]=event;
}
}
