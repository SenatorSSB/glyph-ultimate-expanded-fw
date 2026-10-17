#pragma once
#include <atomic>
#include <cstdint>

// Candidate-only observer data. Each bank has exactly one serialized writer:
// core0 foreground; DCD IRQ; USB-task owner under __usb_mutex. Core1 reads only.
// Only 32-bit atomic load/store (no RMW, lock, heap or waiting) is used. All
// fields are atomic so even a rejected snapshot has no C++ data race. Sequential
// consistency makes the bounded sequence checks an actual publication order.
namespace RecoveryTaskDiagnostics {
struct Snapshot {
    uint32_t valid=0, entered=0, returned=0, active=0, first_returned=0;
    uint32_t active_resets=0, first_resets=0, reset_completed=0, first_reset_completed=0, event_flags=0, task_flags=0;
    // Task pixel: 0 red, 1 orange, 2 magenta, 3 blue, 4 green.
    // Progress pixel: 0 dark, 1 yellow, 2 cyan, 3 green, 4 white.
    unsigned task_pixel=0, progress_pixel=0;
};
class State {
    using Word=std::atomic<uint32_t>;
    Word enabled{0}, armed{0};
    Word fg_seq{0}, entered{0}, returned{0}, active{0}, first_returned{0};
    Word irq_seq{0}, reset_invocation{0}, resets{0}, first_resets{0}, event_flags{0};
    Word task_flags{0}, completed{0}, first_completed{0}, inspection{0};
    static uint32_t increment(uint32_t n){return n==UINT32_MAX?n:n+1;}
public:
    void Enable(){enabled.store(1);}
    void Arm(){if(Enabled())armed.store(1);}
    bool ForegroundEnabled() const{return armed.load()!=0;}
    bool Enabled() const{return enabled.load()!=0;}
    void Enter(){
        fg_seq.store(fg_seq.load()+1);
        const uint32_t id=increment(entered.load());entered.store(id);active.store(id);
        fg_seq.store(fg_seq.load()+1);
    }
    void Return(){
        fg_seq.store(fg_seq.load()+1);
        if(active.load()==1)first_returned.store(1);
        active.store(0);returned.store(increment(returned.load()));
        fg_seq.store(fg_seq.load()+1);
    }
    void ResetEvent(){if(!Enabled())return;
        irq_seq.store(irq_seq.load()+1);
        const uint32_t id=active.load();
        if(id){
            resets.store(id==reset_invocation.load()?increment(resets.load()):1);
            reset_invocation.store(id);
            if(id==1)first_resets.store(increment(first_resets.load()));
        }
        event_flags.store(event_flags.load()|1u);
        irq_seq.store(irq_seq.load()+1);
    }
    void SetupEvent(){if(!Enabled())return;event_flags.store(event_flags.load()|2u);}
    void UnplugEvent(){if(!Enabled())return;event_flags.store(event_flags.load()|4u);}
    void ResetCompleted(){if(!Enabled())return;completed.store(increment(completed.load()));if(active.load()==1)first_completed.store(increment(first_completed.load()));}
    void Control(){if(!Enabled())return;task_flags.store(task_flags.load()|1u);}
    void Configured(){if(!Enabled())return;task_flags.store(task_flags.load()|2u);}
    void Inspection(){if(!Enabled())return;inspection.store(1);}
    Snapshot Read() const{
        Snapshot s;
        const uint32_t f=fg_seq.load(),q=irq_seq.load();
        if((f|q)&1u)return s;
        s.entered=entered.load();s.returned=returned.load();s.active=active.load();
        s.first_returned=first_returned.load();
        const uint32_t event_id=reset_invocation.load(),count=resets.load();
        s.first_resets=first_resets.load();s.event_flags=event_flags.load();
        s.reset_completed=completed.load();s.first_reset_completed=first_completed.load();s.task_flags=task_flags.load();
        const bool inspected=inspection.load()!=0;
        if(f!=fg_seq.load()||q!=irq_seq.load())return s;
        // Never reuse a saturated invocation identity as fresh reset attribution.
        if(s.active==UINT32_MAX)return s;
        s.valid=1;s.active_resets=s.active&&event_id==s.active?count:0;
        // Freeze the first invocation evidence; later healthy calls cannot flicker
        // the pair or continuously republish LED frames. Current-call fields
        // remain separate telemetry, never redefine the first-call color.
        s.task_pixel=s.first_returned?4:s.entered?(s.first_resets>=2?3:s.first_resets?2:1):0;
        // Completion is intentionally generic RESET/UNPLUGGED processing. It
        // does not assert which queued event caused this call or queue success.
        if(s.first_reset_completed)s.progress_pixel=1;
        if(s.event_flags&2u)s.progress_pixel=2;
        if(s.task_flags&1u)s.progress_pixel=3;
        if((s.task_flags&2u)||inspected)s.progress_pixel=4;
        return s;
    }
};
}
