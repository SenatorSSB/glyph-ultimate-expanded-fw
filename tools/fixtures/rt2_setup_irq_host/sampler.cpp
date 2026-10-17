#include "core/RecoverySetupIrqDiagnostics.hpp"
#include <cstdio>
#include <stdexcept>
using namespace RecoverySetupIrqDiagnostics;
void require(bool ok,const char *why){if(!ok)throw std::runtime_error(why);}
int main(){try{
    // All 32 tuples exercise the observer as data. Tuples contrary to stable
    // RP2040 register derivation are sampling-skew robustness, not hardware paths.
    for(unsigned raw=0;raw<32;++raw){
        State state;Snapshot s;state.ReadInto(s);require(!s.valid,"unarmed invalid");
        state.Enable();state.Registered();state.Independent(raw);state.ReadInto(s);
        require(s.valid&&s.independent_seen==raw&&s.independent_tuples==(1u<<raw),"all independent bits and tuple indexes");
        state.Foreground(raw,NvicOn|Unmasked|Pending|Thread|ResetDone|PortReturned|TinyUsbInitialized);state.ReadInto(s);
        require(s.foreground_seen==raw&&s.foreground_tuples==(1u<<raw),"foreground tuple separate from history");
        if(raw&Ints)require((s.foreground_conditions&(IntsPending|IntsGateOpen))==(IntsPending|IntsGateOpen),"co-sampled pending and enabled gate");
        if((raw&Intr)&&!(raw&Inte))require(s.foreground_conditions&IntrMasked,"co-sampled interrupt mask");
        if((raw&Sie)&&!(raw&Intr))require(s.foreground_conditions&SieWithoutIntr,"skew SIE/INTR tuple retained");
        if((raw&Intr)&&(raw&Inte)&&!(raw&Ints))require(s.foreground_conditions&IntrEnabledNoInts,"skew INTR/INTE/INTS tuple retained");
    }
    State state;Snapshot s;state.Enable();state.Registered();
    state.IrqEnter(Inte,NvicOn|Unmasked);state.IrqReturn(Inte,NvicOn|Unmasked);
    state.Independent(Sie|Intr|Inte|Ints);state.ReadInto(s);
    require(s.irq_entries==1&&s.irq_returns==1&&s.irq_first_pre==Inte&&s.irq_latest_pre==Inte&&s.irq_latest_post==Inte&&s.irq_seen==Inte&&s.irq_tuples==(1u<<Inte),"first pre/post IRQ values and banks");
    RecoveryTaskDiagnostics::Snapshot task;task.valid=1;unsigned pixels[8];Panel(s,task,pixels);
    require(pixels[4]==RecoveryTaskDiagnostics::Yellow,"earlier unrelated reset IRQ does not claim SETUP delivery");
    state.Foreground(Ints,NvicOff|Masked|Pending);state.ReadInto(s);
    require((s.foreground_conditions&(IntsNvicOff|IntsGloballyMasked|IntsPending))==(IntsNvicOff|IntsGloballyMasked|IntsPending),"closed gates co-sampled with INTS");
    State split;split.Enable();split.Foreground(Sie,NvicOff);split.Foreground(Ints,NvicOn|Unmasked);split.ReadInto(s);
    require(!(s.foreground_conditions&IntsNvicOff),"sticky histories cannot manufacture same-sample masked gate");
    State tuples;tuples.Enable();tuples.Independent(Intr);tuples.Independent(Inte);tuples.ReadInto(s);
    require(!(s.independent_tuples&(1u<<(Intr|Inte))),"separate INTR and INTE history cannot manufacture pair");
    state.IrqEnter(Sie|Intr|Inte|Ints|Force,NvicOn|Unmasked);state.IrqReturn(0,NvicOn|Unmasked);state.ReadInto(s);Panel(s,task,pixels);
    require(s.irq_entries==2&&s.irq_returns==2&&s.irq_first_pre==Inte&&s.irq_latest_pre==31&&s.irq_latest_post==0&&s.irq_seen==31&&s.irq_tuples==((1u<<Inte)|(1u<<31)|1u),"latest IRQ values remain separate from first and histories");
    require(s.irq_setup_entries==1&&pixels[4]==RecoveryTaskDiagnostics::White,"forced INTS trampoline tuple is included");
    state.DuplicateRegistration();state.ReadInto(s);require(!s.valid&&s.registration_duplicate,"duplicate instrumentation invalidates result");
    std::puts("sampler_32_tuples_correlated_gates_negative_histories=PASS");return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
