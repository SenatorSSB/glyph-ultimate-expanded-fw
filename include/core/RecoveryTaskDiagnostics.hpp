#pragma once
#include <atomic>
#include <cstdint>

// Candidate observer only. Separate serialized writers: foreground, DCD IRQ,
// USB task owner, queue producers by exception context, and core1 raw sampler.
// Bounded 32-bit atomic loads/stores; no RMW, lock, allocation or waiting.
namespace RecoveryTaskDiagnostics {
enum Color : unsigned { Off, Red, Orange, Yellow, Magenta, Blue, Cyan, Green, White };
struct Snapshot {
    uint32_t valid=0, entered=0, returned=0, active=0, first_id=0, latest_returned=0, first_returned=0;
    uint32_t total_resets=0, pre_first_resets=0, first_resets=0, active_resets=0, post_first_resets=0;
    uint32_t reset_completed=0, first_reset_completed=0, reset_consumed=0, reset_continued=0;
    uint32_t reset_stage=0, processing_invocation=0, setup_consumed=0, control_began=0, class_entered=0, class_returned=0, configured_current=0;
    uint32_t queue_attempted=0,queue_accepted=0,queue_failed=0,reset_dropped=0,setup_dropped=0,max_occupancy=0,empty_reads=0;
    uint32_t event_flags=0,task_flags=0,raw_setup_seen=0,pullup=0;
    unsigned task_pixel=0,progress_pixel=0; // retained legacy first-task summary
    unsigned pixels[8]={};uint32_t dashboard=0;
};
class State {
    using Word=std::atomic<uint32_t>;
    struct Foreground { Word seq{0},entered{0},returned{0},active{0},first_returned{0},latest{0}; } fg;
    struct Events { Word seq{0},total{0},pre{0},first{0},post{0},invocation{0},current{0},flags{0}; } irq;
    struct Task { Word seq{0},flags{0},consumed{0},completed{0},first_completed{0},continued{0},stage{0},invocation{0},kind{0},setup{0},control{0},control_started{0},empty{0},class_entered{0},class_returned{0},configured_current{0}; } task;
    struct Producer { Word seq{0},attempted{0},accepted{0},failed{0},reset_drop{0},setup_drop{0},maximum{0}; } producer[3];
    Word enabled{0},armed{0},raw_seen{0},pullup{0},inspection{0};
    static uint32_t increment(uint32_t n){return n==UINT32_MAX?n:n+1;}
    static void bump(Word &w){w.store(increment(w.load()));}
    static void begin(Word &seq){seq.store(seq.load()+1);}
    static void end(Word &seq){seq.store(seq.load()+1);}
    static uint32_t add(uint32_t a,uint32_t b){return UINT32_MAX-a<b?UINT32_MAX:a+b;}
    bool reset_context()const{return task.kind.load()==1||task.kind.load()==2;}
public:
    void Enable(){enabled.store(1);}
    void Arm(){if(Enabled())armed.store(1);}
    bool ForegroundEnabled()const{return armed.load()!=0;}
    bool Enabled()const{return enabled.load()!=0;}
    void Enter(){
        begin(fg.seq);const uint32_t id=increment(fg.entered.load());fg.entered.store(id);
        fg.active.store(id);end(fg.seq); // invocation entry linearization
    }
    void Return(){
        begin(fg.seq);const uint32_t id=fg.active.load();
        if(id==1)fg.first_returned.store(1);
        fg.latest.store(id);fg.active.store(0); // return linearization
        bump(fg.returned);end(fg.seq);
    }
    void ResetEvent(){if(!Enabled())return;
        begin(irq.seq);bump(irq.total);const uint32_t id=fg.active.load();
        if(id){irq.current.store(id==irq.invocation.load()?increment(irq.current.load()):1);irq.invocation.store(id);if(id==1)bump(irq.first);}
        else if(!fg.first_returned.load())bump(irq.pre);
        if(fg.first_returned.load()&&id!=1)bump(irq.post);
        irq.flags.store(irq.flags.load()|1u);end(irq.seq);
    }
    void SetupEvent(){if(!Enabled())return;begin(irq.seq);irq.flags.store(irq.flags.load()|2u);end(irq.seq);}
    void UnplugEvent(){if(!Enabled())return;begin(irq.seq);irq.flags.store(irq.flags.load()|4u);end(irq.seq);}
    // kind: 1 RESET, 2 UNPLUGGED, 3 SETUP, 0 other. Called within existing
    // Pico queue critical section; bank split avoids cross-context RMW.
    void QueueSent(unsigned context,unsigned kind,bool accepted,uint32_t occupancy){if(!Enabled())return;
        Producer &p=producer[context<3?context:2];begin(p.seq);bump(p.attempted);
        if(accepted)bump(p.accepted);else{bump(p.failed);if(kind==1)bump(p.reset_drop);if(kind==3)bump(p.setup_drop);}
        if(occupancy>p.maximum.load()){p.maximum.store(occupancy);}
        end(p.seq);
    }
    void QueueReadBegin(){if(!Enabled())return;begin(task.seq);
        if(reset_context()&&task.stage.load()>=6){bump(task.continued);task.stage.store(7);}
        task.kind.store(0);end(task.seq);
    }
    void QueueReadEnd(unsigned kind,bool success){if(!Enabled())return;begin(task.seq);
        if(!success)bump(task.empty);
        else{task.kind.store(kind);task.control_started.store(0);if(kind==1||kind==2){task.configured_current.store(0);bump(task.consumed);task.stage.store(1);task.class_entered.store(0);task.class_returned.store(0);task.invocation.store(fg.active.load());}if(kind==3)bump(task.setup);}
        end(task.seq);
    }
    void ClassStage(unsigned stage){if(!Enabled()||!reset_context())return;begin(task.seq);task.stage.store(stage);end(task.seq);}
    void ClassBoundary(unsigned index,bool returned){if(!Enabled()||!reset_context())return;begin(task.seq);Word &w=returned?task.class_returned:task.class_entered;w.store(w.load()|(1u<<index));end(task.seq);}
    void ResetCompleted(){if(!Enabled()||!reset_context())return;begin(task.seq);bump(task.completed);task.stage.store(6);if(fg.active.load()==1)bump(task.first_completed);end(task.seq);}
    void ControlBegin(){if(!Enabled()||task.kind.load()!=3||task.control_started.load())return;begin(task.seq);bump(task.control);task.control_started.store(1);end(task.seq);}
    void Progress(unsigned bit){if(!Enabled())return;begin(task.seq);task.flags.store(task.flags.load()|bit);end(task.seq);}
    void Control(){Progress(1);}
    void AddressRequested(){Progress(2);}
    void AddressApplied(){Progress(4);}
    void Configuration(bool on){if(!Enabled())return;begin(task.seq);task.configured_current.store(on?1u:0u);if(on)task.flags.store(task.flags.load()|8u);end(task.seq);}
    void Configured(){Configuration(true);}
    void Inspection(){if(Enabled())inspection.store(1);}
    // Core1 only; read-only hardware samples do not acknowledge/clear USB bits.
    void ObserveRaw(bool raw,bool on){if(raw)raw_seen.store(1);pullup.store(on?2u:1u);}
    Snapshot Read() const{Snapshot s;ReadInto(s);return s;}
    void ReadInto(Snapshot &s) const{
        s={};const uint32_t f=fg.seq.load(),q=irq.seq.load(),t=task.seq.load();
        uint32_t pseq[3];for(unsigned i=0;i<3;++i)pseq[i]=producer[i].seq.load();
        if((f|q|t|pseq[0]|pseq[1]|pseq[2])&1u)return;
        s.entered=fg.entered.load();s.returned=fg.returned.load();s.active=fg.active.load();s.first_id=s.entered?1u:0u;s.first_returned=fg.first_returned.load();s.latest_returned=fg.latest.load();
        const uint32_t event_id=irq.invocation.load(),count=irq.current.load();
        s.total_resets=irq.total.load();s.pre_first_resets=irq.pre.load();s.first_resets=irq.first.load();s.post_first_resets=irq.post.load();s.event_flags=irq.flags.load();
        s.reset_consumed=task.consumed.load();s.reset_completed=task.completed.load();s.first_reset_completed=task.first_completed.load();s.reset_continued=task.continued.load();s.reset_stage=task.stage.load();s.processing_invocation=task.invocation.load();
        s.configured_current=task.configured_current.load();s.class_entered=task.class_entered.load();s.class_returned=task.class_returned.load();s.setup_consumed=task.setup.load();s.control_began=task.control.load();s.empty_reads=task.empty.load();s.task_flags=task.flags.load()|(inspection.load()?16u:0u);
        for(unsigned i=0;i<3;++i){const Producer &p=producer[i];s.queue_attempted=add(s.queue_attempted,p.attempted.load());s.queue_accepted=add(s.queue_accepted,p.accepted.load());s.queue_failed=add(s.queue_failed,p.failed.load());s.reset_dropped=add(s.reset_dropped,p.reset_drop.load());s.setup_dropped=add(s.setup_dropped,p.setup_drop.load());const uint32_t n=p.maximum.load();if(n>s.max_occupancy)s.max_occupancy=n;}
        s.raw_setup_seen=raw_seen.load();s.pullup=pullup.load();
        if(f!=fg.seq.load()||q!=irq.seq.load()||t!=task.seq.load())return;
        for(unsigned i=0;i<3;++i)if(pseq[i]!=producer[i].seq.load())return;
        if(s.active==UINT32_MAX)return; // never reuse saturated task identity
        s.valid=Enabled()?1u:0u;s.active_resets=s.active&&event_id==s.active?count:0;
        s.task_pixel=s.first_returned?4:s.entered?(s.first_resets>=2?3:s.first_resets?2:1):0;
        s.progress_pixel=s.first_reset_completed?1:0;if(s.event_flags&2u)s.progress_pixel=2;if(s.task_flags&1u)s.progress_pixel=3;if(s.task_flags&24u)s.progress_pixel=4;
        s.pixels[0]=s.active?(s.active==1?Orange:White):s.first_returned?Green:Red;
        s.pixels[1]=s.active_resets>=2?Magenta:s.active_resets?Blue:Off;
        const unsigned stages[]={Off,Red,Orange,Yellow,Cyan,Green,White,Blue};
        const bool current=!s.active||s.processing_invocation==s.active;
        // Without an after-enable DCD reset, BLUE/Off would alias
        // unconsumed-one-reset Off/BLUE in an unordered physical pair.
        // Keep exact stage7 in telemetry; group this display with completion.
        s.pixels[2]=current&&s.reset_stage<8?
            ((s.reset_stage==7&&s.total_resets==0)?White:stages[s.reset_stage]):Off;
        s.pixels[3]=s.total_resets>=2?Magenta:s.total_resets?Blue:Off;
        s.pixels[4]=s.control_began?White:s.setup_consumed?Green:(s.event_flags&2u)?Cyan:s.raw_setup_seen?Blue:Off;
        s.pixels[5]=s.reset_dropped&&s.setup_dropped?Yellow:s.reset_dropped?Red:s.setup_dropped?Orange:s.queue_failed?Yellow:s.max_occupancy>=16?Magenta:Off;
        s.pixels[6]=(s.task_flags&16u)?White:s.configured_current?Green:(s.task_flags&8u)?Magenta:(s.task_flags&4u)?Blue:(s.task_flags&2u)?Cyan:(s.task_flags&1u)?Yellow:Off;
        s.pixels[7]=s.pullup==2?Orange:s.pullup==1?Red:Off;
        for(unsigned i=0;i<8;++i)s.dashboard|=uint32_t(s.pixels[i])<<(4*i);
        return;
    }
};
}
